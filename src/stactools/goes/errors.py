class CogifyError(Exception):
    """Raises if there is an error during cogification."""

    pass


class GOESRFileNameError(Exception):
    """Errors related to parsing or creating GOES-R ABI Level 2 file names"""

    pass


class GOESRAttributeError(Exception):
    """Raised when unable to parse an attribute from a GOES-R netcdf file"""

    pass


class GOESRProductHrefsError(Exception):
    """Errors related to validating ProductHrefs"""

    pass


class GOESInvalidGeometryError(Exception):
    """Raises when there's an invalid geometry

    E.g. a coordinate is a fill value (-999.0)
    """

    pass


class GOESMissingExtentError(Exception):
    """Raised when all four bounds are missing (-999) in the netcdf"""
