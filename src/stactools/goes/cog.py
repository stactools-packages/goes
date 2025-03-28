import logging
import os
import subprocess
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional
from urllib.parse import urlparse

import fsspec
from h5py import File

from stactools.goes.dataset import Dataset
from stactools.goes.errors import CogifyError
from stactools.goes.file_name import ABIL2FileName

logger = logging.getLogger(__name__)

BLOCKSIZE = 2**22


def gdal_path(nc_path: str, variable: str) -> str:
    return f"netcdf:{nc_path}:{variable}"


def cogify(
    nc_href: str,
    directory: str,
    target_srs: Optional[str] = None,
    additional_suffix: Optional[str] = None,
    variables_to_include: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Converts a GOES NetCDF file into two or more COGs in the provided output directory.

    Returns the cogs as a dict of variable name -> path. If there is just
    one variables and one data quality field, two cogs will be created.
    Compound datasets, e.g. MCMIP, will produce 2
    * n files, were n is the number of subdatasets.

    If variables_to_include is given, COGs will only
    be created for variables that are in the given list.
    """
    file_name = ABIL2FileName.from_str(os.path.basename(nc_href))

    def _cogify(path: str, directory: str) -> Dict[str, str]:
        cogs = {}
        with open(path, "rb") as f:
            with File(f) as nc:
                dataset = Dataset.from_nc(file_name, nc)
        for variable in dataset.asset_variables:
            if variables_to_include and variable not in variables_to_include:
                logger.warning(f"Skipping COG creation for variable {variable}")
                continue

            logger.info(f"Creating COG for variable {variable}")
            outfile = os.path.join(directory, file_name.get_cog_file_name(variable))
            if additional_suffix:
                base, ext = os.path.splitext(outfile)
                outfile = f"{base}_{additional_suffix}{ext}"

            infile = gdal_path(path, variable)

            args = []
            if target_srs:
                args.append("gdalwarp")
            else:
                args.append("gdal_translate")
            args.extend(
                [
                    # If the HDF5 driver is installed, GDAL will try to use it.
                    # https://gdal.org/en/stable/drivers/raster/netcdf.html
                    "-if",
                    "netCDF",
                    "-of",
                    "COG",
                    "-co",
                    "compress=deflate",
                ]
            )
            if target_srs:
                args.extend(["-t_srs", target_srs])
            args.extend([infile, outfile])

            logger.info(f"Running {args}")
            # Since GOES is a geostationary satellite, some of the full disk
            # images contain "space" pixels.
            # https://gdal.org/en/stable/user/configoptions.html#proj-options
            # For some reason, this _MUST_ be set as an environment variable.
            # If you try to pass it as a CLI config option, it doesn't work.
            os.environ["OGR_ENABLE_PARTIAL_REPROJECTION"] = "TRUE"
            result = subprocess.run(args, capture_output=True)
            logger.info(result.stdout.decode("utf-8").strip())
            if result.returncode != 0:
                logger.error(result.stderr.decode("utf-8").strip())
                raise CogifyError(result.stderr.decode("utf-8").strip())
            else:
                logger.info(result.stderr.decode("utf-8").strip())
            cogs[variable] = outfile

        return cogs

    if urlparse(nc_href).scheme:
        with TemporaryDirectory() as temporary_directory:
            local_path = os.path.join(temporary_directory, file_name.to_str())
            with fsspec.open(nc_href) as source:
                with fsspec.open(local_path, "wb") as target:
                    data = True
                    while data:
                        data = source.read(BLOCKSIZE)
                        target.write(data)
            return _cogify(local_path, directory)
    else:
        return _cogify(nc_href, directory)
