import logging
import os
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, TypeVar

import fsspec
import rasterio
from h5py import File
from pystac import Item
from pystac.extensions.eo import EOExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import RasterExtension
from stactools.core.io import ReadHrefModifier

from stactools.goes import __version__, cog
from stactools.goes.bands import get_channel_resolution
from stactools.goes.dataset import Dataset
from stactools.goes.enums import ImageType, PlatformId
from stactools.goes.errors import GOESRProductHrefsError
from stactools.goes.file_name import ABIL2FileName
from stactools.goes.product import PRODUCTS, ProductAcronym

logger = logging.getLogger(__name__)

T = TypeVar("T")

BackoffFunc = Callable[[Callable[[], T]], T]
"""Defines a backoff function that users can supply
to perform exponential backoff of reads such as
rasterio reads.

Backoff functions take a method that returns T, and calls
it, returning the resulting T. Inside the backoff function
you can place logic that captures throttling exceptions
and performs retries, which is useful in highly parallelized
data processing scenarios.
"""


@dataclass
class ProductHrefs:
    nc_href: str
    """Path to netcdf data file for a single product."""

    cog_hrefs: Optional[Dict[str, str]]
    """Path to COG data for this product.

    Key is the variable name, value is the href.
    """

    @staticmethod
    def validate_single_observation(product_hrefs: List["ProductHrefs"]) -> None:
        """Validates that all hrefs are from a single observation."""
        item_ids = set(
            [ABIL2FileName.from_href(ph.nc_href).get_item_id() for ph in product_hrefs]
        )
        if len(item_ids) != 1:
            raise GOESRProductHrefsError(
                f"ProductHrefs represent multiple observations: {','.join(item_ids)}"
            )


def normalize_cmi_cog_assets(item: Item) -> None:
    """Normalize COG assets for CMI band data, if they exist.

    The CMIP and MCMIP both contain variables for
    Cloud and Moisture Imagery.
    The resolution for the single band CMIP data
    varies for 1, 2, 3 and 5, but each of the others
    match at 2km resolution. Deduplicate the
    CMIP and MCMIP COG data for other bands, and
    normalize the asset keys. Use CMI as the prefix for
    all COG asset keys and suffix the km resolution.
    """
    # Create a Dict of channel (e.g. 'C01') to a Dict of the
    # asset keys for each of the CMIP and MCMIP products.
    channel_to_cmi_cog_asset_keys: Dict[int, Dict[ProductAcronym, List[str]]] = {}
    for asset_key in item.assets:
        # Ignore nc assets
        if item.assets[asset_key].href.endswith("nc"):
            continue
        target_product: Optional[ProductAcronym] = None
        if asset_key.startswith(ProductAcronym.CMIP.value):
            target_product = ProductAcronym.CMIP
        if asset_key.startswith(ProductAcronym.MCMIP.value):
            target_product = ProductAcronym.MCMIP
        if target_product:
            channel: Optional[int] = None
            m = re.search(r"_C(\d\d)", asset_key)
            if m:
                channel = int(m.group(1))
            elif target_product == ProductAcronym.CMIP:
                raise Exception(f"CMIP expected to have info in asset_key: {asset_key}")
            if channel is not None:
                if channel not in channel_to_cmi_cog_asset_keys:
                    channel_to_cmi_cog_asset_keys[channel] = {}
                if target_product not in channel_to_cmi_cog_asset_keys[channel]:
                    channel_to_cmi_cog_asset_keys[channel][target_product] = []
                channel_to_cmi_cog_asset_keys[channel][target_product].append(asset_key)

    # Deduplicate products that contain the same data.
    # Convert asset keys to "CMI" instead of "CMIP" or "MCMIP"
    # Append the resolution to the asset key
    for channel, product_to_asset_keys in channel_to_cmi_cog_asset_keys.items():
        if len(product_to_asset_keys) > 1:
            res_in_meters = get_channel_resolution(channel)
            if res_in_meters != 2000:
                res_in_km = int(res_in_meters / 1000) if res_in_meters != 500 else 0.5
                # If this is channel 2, 3 or 5, then the CMIP data
                # contains a higher resolution version of the data.
                # Modify the asset keys accordingly.
                for asset_key in product_to_asset_keys[ProductAcronym.CMIP]:
                    asset = item.assets[asset_key]
                    asset.title = f"{asset.title} (full resolution)"
                    new_key = asset_key.replace("CMIP", "CMI") + f"_{res_in_km}km"
                    item.assets[new_key] = asset
                    item.assets.pop(asset_key)
            else:
                # CMIP product data is redundant, remove those assets.
                for asset_key in product_to_asset_keys[ProductAcronym.CMIP]:
                    if asset_key.startswith(ProductAcronym.CMIP.value):
                        item.assets.pop(asset_key)

        # Convert MCMIP -> CMI, suffix with 2km
        if ProductAcronym.MCMIP in product_to_asset_keys:
            for asset_key in product_to_asset_keys[ProductAcronym.MCMIP]:
                asset = item.assets[asset_key]
                new_key = asset_key.replace("MCMIP", "CMI") + "_2km"
                item.assets[new_key] = asset
                item.assets.pop(asset_key)


def create_item(
    product_hrefs: List[ProductHrefs],
    read_href_modifier: Optional[ReadHrefModifier] = None,
    backoff_func: Optional[BackoffFunc] = None,
) -> Item:
    """Creates an Item from GOES-R ABI Level 2 product HREFs.

    This method will only read information from the NetCDF file represented in the
    first entry of product_hrefs.

    backoff_func: A backoff function that can be used for exponential backoff
        of data reading for throttling messages occurring during highly parallelized jobs.
    """
    dataset: Dataset
    _rhm: ReadHrefModifier = (
        read_href_modifier if read_href_modifier is not None else lambda x: x
    )
    with_backoff = backoff_func if backoff_func else lambda f: f()

    if len(product_hrefs) == 0:
        raise GOESRProductHrefsError("product_hrefs cannot be empty.")
    ProductHrefs.validate_single_observation(product_hrefs)

    # Grab the first href as a token dataset to derive the common attributes.
    token_nc_href = product_hrefs[0].nc_href
    token_file_name = ABIL2FileName.from_href(token_nc_href)

    def read_dataset() -> Dataset:
        logger.info(f"Reading metadata from {token_nc_href}")
        with fsspec.open(_rhm(token_nc_href)) as file:
            with File(file) as nc:
                return Dataset.from_nc(token_file_name, nc)

    dataset = with_backoff(read_dataset)

    start_datetime = dataset.global_attributes.start_datetime

    item = Item(
        id=dataset.file_name.get_item_id(),
        geometry=dataset.geometry.footprint,
        bbox=dataset.geometry.bbox,
        datetime=start_datetime,
        properties={},
    )

    item.common_metadata.platform = PlatformId.to_stac_value(dataset.file_name.platform)
    item.common_metadata.instruments = ["ABI"]

    item.stac_extensions.append(
        "https://stac-extensions.github.io/processing/v1.0.0/schema.json"
    )
    item.properties["processing:software"] = {"stactools-goes": __version__}

    item.properties["goes:system-environment"] = dataset.file_name.system.value
    item.properties["goes:image-type"] = ImageType.to_stac_value(
        dataset.file_name.image_type
    )
    item.properties["goes:mode"] = dataset.file_name.mode.value
    item.properties["goes:processing-level"] = "L2"
    if dataset.file_name.mesoscale_number:
        item.properties["goes:mesoscale-image-number"] = int(
            dataset.file_name.mesoscale_number.value
        )

    # Projection

    projection = ProjectionExtension.ext(item, add_if_missing=True)
    projection.epsg = None
    projection.wkt2 = dataset.geometry.projection_wkt2
    projection.shape = dataset.geometry.projection_shape
    projection.transform = dataset.geometry.projection_transform
    projection.bbox = dataset.geometry.projection_bbox

    # Add assets for products

    has_eo = False
    has_raster = False

    for hrefs in product_hrefs:
        file_name = ABIL2FileName.from_str(os.path.basename(hrefs.nc_href))
        product = PRODUCTS[file_name.product]
        nc_asset_key, nc_asset_def = product.get_nc_asset_def(file_name)
        item.add_asset(nc_asset_key, nc_asset_def.create_asset(hrefs.nc_href))

        if hrefs.cog_hrefs:
            has_raster = True

            for variable, cog_href in hrefs.cog_hrefs.items():
                cog_asset_key, cog_asset_def = product.get_cog_asset_def(
                    file_name, variable
                )
                asset = cog_asset_def.create_asset(cog_href)

                # Get COG metadata
                logger.info(f"Reading COG metadata from from {cog_href}...")

                def get_cog_metadata() -> None:
                    with rasterio.open(_rhm(cog_href)) as ds:
                        # Set transform and shape if needed
                        if not projection.shape or ds.shape[0] != projection.shape[0]:
                            ProjectionExtension.ext(asset).shape = list(ds.shape)
                            ProjectionExtension.ext(asset).transform = list(
                                ds.transform
                            )

                        dtypes = {i: dtype for i, dtype in zip(ds.indexes, ds.dtypes)}
                        dtype = dtypes[1]

                        raster = RasterExtension.ext(asset)
                        assert raster.bands
                        band = raster.bands[0]
                        assert band
                        band.data_type = dtype
                        assert band.data_type
                        if band.data_type.startswith("float"):
                            band.nodata = ds.nodata
                        else:
                            band.nodata = int(ds.nodata)

                with_backoff(get_cog_metadata)

                if "eo:bands" in asset.extra_fields:
                    has_eo = True

                item.add_asset(cog_asset_key, asset)

    if has_eo:
        EOExtension.add_to(item)
    if has_raster:
        RasterExtension.add_to(item)

    normalize_cmi_cog_assets(item)

    return item


def create_item_from_href(
    href: str,
    read_href_modifier: Optional[ReadHrefModifier] = None,
    cog_directory: Optional[str] = None,
    backoff_func: Optional[BackoffFunc] = None,
) -> Item:
    """Creates a pystac.Item from a GOES netcdf file.

    cog_directory: The directory COGs will be saved to,
        if generating COGs.
    backoff_func: A backoff function that can be used for exponential backoff
        of data reading for throttling messages occurring during highly parallelized jobs.
    """
    cogs: Optional[Dict[str, str]] = None
    if cog_directory:
        cogs = cog.cogify(href, cog_directory)

    return create_item(
        product_hrefs=[ProductHrefs(nc_href=href, cog_hrefs=cogs)],
        read_href_modifier=read_href_modifier,
        backoff_func=backoff_func,
    )
