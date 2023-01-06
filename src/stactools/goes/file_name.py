"""Filename parsing for GOES-R ABI Level 2 data.

Taken from https://www.goes-r.gov/products/docs/PUG-L2+-vol5.pdf
See APPENDIX A on page marked 608
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime as Datetime
from typing import Optional

from pystac.utils import map_opt

from stactools.goes.enums import (
    ImageType,
    MesoscaleImageNumber,
    Mode,
    PlatformId,
    ProductAcronym,
    SystemEnvironment,
)
from stactools.goes.errors import GOESRFileNameError
from stactools.goes.utils import goes_time_to_datetime

FILE_NAME_REGEX = re.compile(
    f'(?P<system>{"|".join([e.value for e in SystemEnvironment])})_'
    r"ABI-L2-"
    f'(?P<product>{"|".join([e.value for e in ProductAcronym])})'
    r"(?P<image_type>\w)(?P<mesoscale_number>\d)?-"
    r"M(?P<mode>\d+?)C?(?P<channel>\d*)_"
    r"(?P<platform>G\d+)_"
    r"(?P<cyclone_id>\w\w\d\d\d\d\d\d)?_?"
    r"s(?P<start_time>\d+)_"
    r"e(?P<end_time>\d+)_"
    r"c(?P<created_time>\d+)\.nc"
)


@dataclass
class ABIL2FileName:
    system: SystemEnvironment
    product: ProductAcronym
    image_type: ImageType
    mesoscale_number: Optional[MesoscaleImageNumber]
    mode: Mode
    channel: Optional[int]
    platform: PlatformId
    cyclone_id: Optional[str]
    start_time: str
    end_time: str
    created_time: str

    def __str__(self):
        return self.to_str()

    def to_str(self) -> str:
        mesoscale_number_part = (
            f"{self.mesoscale_number.value}" if self.mesoscale_number else ""
        )
        channel_part = f"C{self.channel:0>2d}" if self.channel else ""
        cyclone_id_part = f"{self.cyclone_id}_" if self.cyclone_id else ""
        return (
            f"{self.system.value}_"
            "ABI-L2-"
            f"{self.product.value}{self.image_type.value}"
            f"{mesoscale_number_part}"
            "-"
            f"M{self.mode.value}"
            f"{channel_part}"
            "_"
            f"{self.platform.value}_"
            f"{cyclone_id_part}"
            f"s{self.start_time}_"
            f"e{self.end_time}_"
            f"c{self.created_time}.nc"
        )

    @classmethod
    def from_str(cls, file_name: str) -> "ABIL2FileName":
        m = FILE_NAME_REGEX.match(file_name)
        if not m:
            raise GOESRFileNameError(
                f"{file_name} not recognized as GOES-R ABI L2 formatted file name"
            )

        channel: Optional[int] = None
        if m.group("channel"):
            try:
                channel = int(m.group("channel"))
            except (ValueError, TypeError) as e:
                raise GOESRFileNameError(
                    f"Invalid channel: {m.group('channel')}"
                ) from e

        return cls(
            system=SystemEnvironment(m.group("system")),
            product=ProductAcronym(m.group("product")),
            image_type=ImageType(m.group("image_type")),
            mesoscale_number=map_opt(
                lambda x: MesoscaleImageNumber(x), m.group("mesoscale_number") or None
            ),
            mode=Mode(m.group("mode")),
            channel=channel,
            platform=PlatformId(m.group("platform")),
            cyclone_id=m.group("cyclone_id") or None,
            start_time=m.group("start_time"),
            end_time=m.group("end_time"),
            created_time=m.group("created_time"),
        )

    @classmethod
    def from_href(cls, href: str) -> "ABIL2FileName":
        return cls.from_str(os.path.basename(href))

    @classmethod
    def from_cog_href(cls, href: str) -> "ABIL2FileName":
        m = re.match(r"(.*c[\d]+)_([^.]+?)\.tif", href)
        if not m:
            raise GOESRFileNameError(f"{href} is not a valid Goes COG href")
        fname = os.path.basename(m.group(1)) + ".nc"
        try:
            return cls.from_str(fname)
        except GOESRFileNameError as e:
            raise GOESRFileNameError(f"{href} is not a valid Goes COG file name") from e

    @classmethod
    def product_from_href(cls, href: str) -> "ProductAcronym":
        file_name = cls.from_href(href)
        return file_name.product

    def get_product_file_prefix(self, product: ProductAcronym) -> str:
        mesoscale_number_part = (
            f"{self.mesoscale_number.value}" if self.mesoscale_number else ""
        )
        return (
            f"{self.system.value}_"
            "ABI-L2-"
            f"{product.value}"
            f"{self.image_type.value}"
            f"{mesoscale_number_part}"
            "-"
            f"M{self.mode.value}"
            "_"
            f"{self.platform.value}_"
            f"s{self.start_time}_"
        )

    def get_channel_file_prefix(self, product: ProductAcronym, channel: int) -> str:
        if product != ProductAcronym.CMIP and product != ProductAcronym.DMW:
            raise GOESRFileNameError(
                f"Channel path not valid for {product.value}, "
                f"only valid for {ProductAcronym.CMIP.value} and {ProductAcronym.DMW.value}"
            )

        mesoscale_number_part = (
            f"{self.mesoscale_number.value}" if self.mesoscale_number else ""
        )
        return (
            f"{self.system.value}_"
            "ABI-L2-"
            f"{product.value}"
            f"{self.image_type.value}"
            f"{mesoscale_number_part}"
            "-"
            f"M{self.mode.value}"
            f"C{channel:0>2d}"
            "_"
            f"{self.platform.value}_"
            f"s{self.start_time}_"
        )

    def get_cog_file_name(self, variable: str) -> str:
        """Returns a COG filename for the given nc dataset variable"""
        nc_file_name = self.to_str()
        base_name = os.path.splitext(nc_file_name)[0]

        return f"{base_name}_{variable}.tif"

    def get_item_id(self) -> str:
        mesoscale_number_part = (
            f"{self.mesoscale_number.value}" if self.mesoscale_number else ""
        )
        return (
            f"{self.system.value}_"
            "ABI-L2-"
            f"{self.image_type.value}"
            f"{mesoscale_number_part}"
            "-"
            f"M{self.mode.value}"
            "_"
            f"{self.platform.value}_"
            f"s{self.start_time}"
        )

    @property
    def start_datetime(self) -> Datetime:
        return goes_time_to_datetime(self.start_time)

    @property
    def end_datetime(self) -> Datetime:
        return goes_time_to_datetime(self.end_time)

    @property
    def created_datetime(self) -> Datetime:
        return goes_time_to_datetime(self.created_time)
