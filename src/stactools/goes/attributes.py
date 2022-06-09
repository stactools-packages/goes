from dataclasses import dataclass
from datetime import datetime as Datetime

from h5py import File

from stactools.goes.enums import ProductionEnvironment
from stactools.goes.errors import GOESRAttributeError
from stactools.goes.utils import get_nc_datetime_attr, get_nc_str_attr


@dataclass
class GlobalAttributes:
    title: str
    summary: str
    production_environment: ProductionEnvironment
    start_datetime: Datetime
    end_datetime: Datetime
    spatial_resolution_km: float

    @classmethod
    def from_nc(cls, nc: File) -> "GlobalAttributes":
        title = get_nc_str_attr(nc, "title")
        summary = get_nc_str_attr(nc, "summary")

        start_datetime = get_nc_datetime_attr(nc, "time_coverage_start")
        end_datetime = get_nc_datetime_attr(nc, "time_coverage_end")
        production_environment = get_nc_str_attr(nc, "production_environment")

        # All resolutions have the format
        # "Xkm at nadir"
        res_at_nadir = get_nc_str_attr(nc, "spatial_resolution")
        try:
            spatial_resolution_km = float(res_at_nadir.replace("km at nadir", ""))
        except ValueError as e:
            raise GOESRAttributeError(
                f"Cannot parse spatial_resolution {res_at_nadir}"
            ) from e

        return GlobalAttributes(
            title=title,
            summary=summary,
            production_environment=ProductionEnvironment(production_environment),
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            spatial_resolution_km=spatial_resolution_km,
        )
