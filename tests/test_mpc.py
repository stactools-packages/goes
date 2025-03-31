import unittest
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import planetary_computer
import requests
from azure.storage.blob import BlobServiceClient
from planetary_computer.sas import get_token

from stactools.goes.enums import PlatformId, ProductAcronym
from stactools.goes.file_name import ABIL2FileName
from stactools.goes.product import PRODUCTS

GOES_STORAGE_ACCOUNT = "goeseuwest"
GOES_ACCOUNT_URL = f"https://{GOES_STORAGE_ACCOUNT}.blob.core.windows.net"
GOES_CONTAINERS = {
    PlatformId.G16: "noaa-goes16",
    PlatformId.G17: "noaa-goes17",
}
GOES_COG_CONTAINER = "noaa-goes-cogs"


class MPCDataError(Exception):
    pass


class MicrosoftPCData:
    """Defines the layout of GOES-R data assets stored in
    Azure as part of the Microsoft Planetary Computer

    Args:
        nc_href: HREF to a single NetCDF asset. This will define all other paths.
    """

    def __init__(self, nc_href: str) -> None:
        self.reference_nc_href = nc_href
        self.reference_file_name = ABIL2FileName.from_href(nc_href)
        self.nc_container = GOES_CONTAINERS[self.reference_file_name.platform]

        parsed_url = urlparse(nc_href)
        self.folder = "/".join(parsed_url.path.split("/")[3:6])

        self.nc_urls: Dict[Tuple[ProductAcronym, Optional[int]], str] = {
            (
                self.reference_file_name.product,
                self.reference_file_name.channel,
            ): nc_href
        }

    def _get_product_folder(self, product: ProductAcronym) -> str:
        return f"ABI-L2-{product.value}{self.reference_file_name.image_type.value}"

    def get_nc_href(
        self, product: ProductAcronym, channel: Optional[int] = None
    ) -> str:
        if (product, channel) not in self.nc_urls:
            parts = [self._get_product_folder(product)]

            parts.append(self.folder)

            if channel:
                parts.append(
                    self.reference_file_name.get_channel_file_prefix(product, channel)
                )
            else:
                parts.append(self.reference_file_name.get_product_file_prefix(product))

            prefix = "/".join(parts)

            sas_token = get_token(GOES_STORAGE_ACCOUNT, self.nc_container).token

            with BlobServiceClient(
                account_url=GOES_ACCOUNT_URL, credential=sas_token
            ) as client:
                with client.get_container_client(self.nc_container) as container:
                    blobs = [
                        b.name for b in container.list_blobs(name_starts_with=prefix)
                    ]
                    if len(blobs) == 0:
                        raise MPCDataError(
                            f"No netCDF file found for product {product.value} "
                            f"based on {self.reference_nc_href} "
                            f"(prefix {prefix})"
                        )
                    if len(blobs) > 1:
                        raise MPCDataError(
                            f"More than 1 file found for product {product.value} "
                            f"based on {self.reference_nc_href}: "
                            f"{','.join(blobs)}"
                        )
                    self.nc_urls[(product, channel)] = (
                        f"{GOES_ACCOUNT_URL}/{self.nc_container}/{blobs[0]}"
                    )

        return self.nc_urls[(product, channel)]

    def get_cog_hrefs(
        self, product: ProductAcronym, channel: Optional[int] = None
    ) -> Dict[str, str]:
        nc_href = self.get_nc_href(product, channel=channel)
        nc_file_name = ABIL2FileName.from_href(nc_href)
        cog_file_names = PRODUCTS[product].get_cog_file_names(nc_file_name)

        path_parts = [GOES_ACCOUNT_URL, GOES_COG_CONTAINER]
        if nc_file_name.platform == PlatformId.G17:
            path_parts.append("goes-17")
        elif nc_file_name.platform == PlatformId.G18:
            path_parts.append("goes-18")
        elif nc_file_name.platform == PlatformId.G19:
            path_parts.append("goes-19")
        else:
            path_parts.append("goes-16")
        path_parts.append(self._get_product_folder(product))
        path_parts.append(self.folder)

        return {
            var: "/".join(path_parts + [cog_file_name])
            for var, cog_file_name in cog_file_names.items()
        }


class MPCDataTest(unittest.TestCase):
    def test_gets_nc_hrefs(self):
        mcmip_href = (
            "https://goeseuwest.blob.core.windows.net/noaa-goes16/"
            "ABI-L2-MCMIPF/2018/010/05/"
            "OR_ABI-L2-MCMIPF-M3_G16_s20180100500410_e20180100511183_c20180100511270.nc"
        )

        mpc_data = MicrosoftPCData(mcmip_href)

        # Fetch nc hrefs, ensure no exceptions are raised.
        _ = mpc_data.get_nc_href(ProductAcronym.FDC)
        _ = mpc_data.get_nc_href(ProductAcronym.CMIP, channel=2)

        # Check COG hrefs exist
        for cog_href in mpc_data.get_cog_hrefs(ProductAcronym.FDC).values():
            r = requests.head(planetary_computer.sign(cog_href))
            r.raise_for_status()

        # Check COG hrefs for single channel CMIP
        for cog_href in mpc_data.get_cog_hrefs(ProductAcronym.CMIP, channel=5).values():
            r = requests.head(planetary_computer.sign(cog_href))
            r.raise_for_status()
