from datetime import datetime as Datetime
from datetime import timedelta, timezone

import dateutil.parser
from h5py import File

from stactools.goes.errors import GOESRAttributeError, GOESRFileNameError


def get_nc_str_attr(nc: File, attribute: str) -> str:
    v = nc.attrs[attribute]
    if not isinstance(v, bytes):
        raise GOESRAttributeError(
            f"Attribute {attribute} expected to be bytes, was {type(v)}"
        )
    return v.decode("utf-8")


def get_nc_datetime_attr(nc: File, attribute: str) -> Datetime:
    v = nc.attrs[attribute]
    if not isinstance(v, bytes):
        raise GOESRAttributeError(
            f"Attribute {attribute} expected to be bytes, was {type(v)}"
        )
    return dateutil.parser.parse(v)


def goes_time_to_datetime(goes_time: str) -> Datetime:
    """Parse a datetime contained in a GOES-R ABI L2 file name

    File names encode times as YYYYDDDHHMMSSs format, where:
    - YYYY = year: e.g., 2015
    - DDD = day of year: 001-366
    - HH = UTC hour of day: 00-23
    - SSs = second of minute: 00-60 (60 indicates leap second and third “s” is tenth of second)
    """
    try:
        result = Datetime.strptime(goes_time[:-3], "%Y%j%H%M")
        result += timedelta(seconds=int(goes_time[-3:-1]))
        result += timedelta(milliseconds=int(goes_time[-1]) * 100)
        result.replace(tzinfo=timezone.utc)
        return result
    except (ValueError, TypeError) as e:
        raise GOESRFileNameError(
            f"GOES filename contains date that can't be parsed: {goes_time}"
        ) from e
