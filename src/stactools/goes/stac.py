import pkg_resources
from typing import Optional, Dict

from pystac import Item, Asset, MediaType
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.eo import Band, EOExtension

from stactools.core.io import ReadHrefModifier
from stactools.goes import Dataset
from stactools.goes.enums import (ProductionEnvironment, OrbitalSlot, Mode,
                                  ImageType, ProductionDataSource, PlatformId,
                                  MesoscaleImageNumber)


def create_item(href: str,
                read_href_modifier: Optional[ReadHrefModifier] = None,
                cog_directory: Optional[str] = None,
                tight_geometry: bool = False) -> Item:
    """Creates a pystac.Item from a GOES netcdf file."""
    if read_href_modifier:
        href = read_href_modifier(href)
    dataset = Dataset(href, tight_geometry=tight_geometry)
    if cog_directory:
        cogs = dataset.cogify(cog_directory)
    else:
        cogs = {}
    return create_item_from_dataset(dataset, cogs)


def create_item_from_dataset(dataset: Dataset,
                             cogs: Dict[str, str] = {}) -> Item:
    """Creates a pystac.Item from a GOES dataset.

    Optionally, add in the provided COGS as assets. The cogs should be a
    dictionary of variable name -> path.
    """
    item = Item(id=dataset.id,
                geometry=dataset.geometry,
                bbox=dataset.bbox,
                datetime=dataset.datetime,
                properties={})
    item.common_metadata.start_datetime = dataset.start_datetime
    item.common_metadata.end_datetime = dataset.end_datetime
    item.stac_extensions.append(
        "https://stac-extensions.github.io/processing/v1.0.0/schema.json")
    item.properties["processing:software"] = {
        "stactools-goes": pkg_resources.require("stactools-goes")[0].version
    }
    item.properties["goes:production-site"] = dataset.production_site
    item.properties["goes:production-environment"] = ProductionEnvironment(
        dataset.production_environment).value
    item.properties["goes:orbital-slot"] = OrbitalSlot(
        dataset.orbital_slot).value
    item.properties["goes:platform-id"] = PlatformId(dataset.platform_id).value
    item.properties["goes:instrument-type"] = dataset.instrument_type
    item.properties["goes:scene-id"] = ImageType(dataset.scene_id).value
    item.properties["goes:instrument-id"] = dataset.instrument_id
    item.properties["goes:timeline-id"] = Mode(dataset.timeline_id).value
    item.properties["goes:production-data-source"] = ProductionDataSource(
        dataset.production_data_source).value
    item.properties["goes:id"] = dataset.goes_id
    if dataset.mesoscale_image_number:
        item.properties["goes:mesoscale-image-number"] = MesoscaleImageNumber(
            dataset.mesoscale_image_number).value
    else:
        item.properties["goes:mesoscale-image-number"] = None

    ProjectionExtension.add_to(item)
    projection = ProjectionExtension.ext(item)
    projection.epsg = None
    projection.wkt2 = dataset.projection_wkt2
    projection.shape = dataset.projection_shape
    projection.transform = dataset.projection_transform

    bands = None
    if dataset.channels and dataset.band_wavelength:
        bands = dict(
            (channel,
             Band.create(name=channel,
                         center_wavelength=dataset.band_wavelength[channel]))
            for channel in dataset.channels)
        for band in bands.values():
            common_name = _common_name(band.center_wavelength)
            if common_name:
                band.common_name = common_name

    item.add_asset(
        "data",
        Asset(href=dataset.original_href,
              title=dataset.title,
              description=dataset.description,
              media_type="application/netcdf",
              roles=["data"]))
    if bands:
        eo = EOExtension.ext(item.assets["data"], add_if_missing=True)
        eo.bands = list(bands.values())

    for variable, path in cogs.items():
        item.add_asset(
            variable,
            Asset(href=path,
                  title=(dataset.long_name[variable]),
                  media_type=MediaType.COG,
                  roles=["data"]))
        if bands:
            parts = variable.split('_')
            assert len(parts) == 2
            variable_category, channel = parts
            if variable_category == "DQF":
                continue
            eo = EOExtension.ext(item.assets[variable])
            eo.bands = [bands[channel]]
    return item


def _common_name(center_wavelenth: float) -> Optional[str]:
    # Taken from
    # https://github.com/stac-utils/pystac/blob/69e9f76b40ed6399b78c671636311e42f2cd17be/pystac/extensions/eo.py#L238-L255
    name_to_range = {
        "coastal": (0.40, 0.45),
        "blue": (0.45, 0.50),
        "green": (0.50, 0.60),
        "red": (0.60, 0.70),
        "yellow": (0.58, 0.62),
        "pan": (0.50, 0.70),
        "rededge": (0.70, 0.75),
        "nir": (0.75, 1.00),
        "cirrus": (1.35, 1.40),
        "swir16": (1.55, 1.75),
        "swir22": (2.10, 2.30),
        "lwir11": (10.5, 11.5),
        "lwir12": (11.5, 12.5),
    }
    for key, (min, max) in name_to_range.items():
        if center_wavelenth >= min and center_wavelenth <= max:
            return key
    return None
