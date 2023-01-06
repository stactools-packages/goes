import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from h5py import File
from pyproj.crs import GeographicCRS, ProjectedCRS
from pyproj.crs.coordinate_operation import GeostationarySatelliteConversion
from pyproj.crs.datum import CustomDatum, CustomEllipsoid
from shapely.geometry import Polygon, box, mapping, shape
from stactools.core.projection import reproject_geom

from stactools.goes.attributes import GlobalAttributes
from stactools.goes.enums import ImageType
from stactools.goes.errors import GOESInvalidGeometryError, GOESMissingExtentError
from stactools.goes.file_name import ABIL2FileName

GOES_ELLIPSOID = CustomEllipsoid.from_name("GRS80")

logger = logging.getLogger(__name__)


def maybe_flip_x_across_antimeridian(x: float) -> float:
    """Flips a longitude across the antimeridian if needed."""
    if x > 90:
        return (-180 * 2) + x
    else:
        return x


def ensure_no_antimeridian_crossing(geom: Dict[str, Any]) -> None:
    """Modifies a geometry so that it doesn't cross the antimeridian."""

    def fn(coords):
        coords = list(coords)
        for i in range(0, len(coords)):
            coord = coords[i]
            if isinstance(coord[0], Sequence):
                coords[i] = fn(coord)
            else:
                x, y = coord
                x = maybe_flip_x_across_antimeridian(x)

                coords[i] = [x, y]
        return coords

    geom["coordinates"] = fn(geom["coordinates"])


@dataclass
class DatasetGeometry:
    """The projection and geometry information for a GOES netcdf dataset.

    Projection stuff built with help from
    https://github.com/OSGeo/gdal/blob/95e35bd1c40ec6ce33341ed6390cce955048067f/gdal/frmts/netcdf/netcdfdataset.cpp
    """

    projection_wkt2: str
    projection_shape: List[int]
    projection_transform: List[float]
    projection_bbox: List[float]
    bbox: List[float]
    footprint: Dict[str, Any]

    @classmethod
    def from_nc(cls, nc: File, image_type: ImageType) -> "DatasetGeometry":
        projection = nc["goes_imager_projection"]
        sweep_angle_axis = projection.attrs["sweep_angle_axis"].decode("utf-8")
        satellite_height = projection.attrs["perspective_point_height"][0].item()
        latitude_natural_origin = projection.attrs["latitude_of_projection_origin"][
            0
        ].item()
        longitude_natural_origin = projection.attrs["longitude_of_projection_origin"][
            0
        ].item()
        extent = nc["geospatial_lat_lon_extent"]
        xmin = extent.attrs["geospatial_westbound_longitude"][0].item()
        ymin = extent.attrs["geospatial_southbound_latitude"][0].item()
        xmax = extent.attrs["geospatial_eastbound_longitude"][0].item()
        ymax = extent.attrs["geospatial_northbound_latitude"][0].item()

        if all(v == -999.0 for v in (xmin, ymin, xmax, ymax)):
            raise GOESMissingExtentError(
                "All four geospatial extents are -999.0 (missing)"
            )

        # If xmin is -999.0, clip as -180
        # This happens when the left side of the shot
        # extends past the curvature of the earth.
        # Use gdalwarp's behavior in this case
        # (which sets this to -179.9999443)
        if xmin == -999.0:
            xmin = -180.0

        # If others are that clip value, consider a bad geom
        for v in [ymin, xmax, ymax]:
            if v == -999.0:
                raise GOESInvalidGeometryError("Lat/lng value is -999.0")

        rowcount = len(nc["y"][:])
        colcount = len(nc["x"][:])
        x = nc["x"][:].tolist()
        x_scale = nc["x"].attrs["scale_factor"][0].item()
        x_offset = nc["x"].attrs["add_offset"][0].item()
        y = nc["y"][:].tolist()
        y_scale = nc["y"].attrs["scale_factor"][0].item()
        y_offset = nc["y"].attrs["add_offset"][0].item()

        # we let GRS80 and WGS84 be ~the same for these purposes, since we're
        # not looking for survey-level precision in these bounds
        bbox = [maybe_flip_x_across_antimeridian(xmin), ymin, xmax, ymax]

        datum = CustomDatum(ellipsoid=GOES_ELLIPSOID)
        conversion = GeostationarySatelliteConversion(
            sweep_angle_axis,
            satellite_height,
            latitude_natural_origin,
            longitude_natural_origin,
        )
        crs = ProjectedCRS(
            conversion=conversion, geodetic_crs=GeographicCRS(datum=datum)
        )

        projection_wkt2 = crs.to_wkt()
        projection_shape = [rowcount, colcount]

        x_bounds = [(x_scale * x + x_offset) * satellite_height for x in [x[0], x[-1]]]
        y_bounds = [(y_scale * y + y_offset) * satellite_height for y in [y[0], y[-1]]]
        xres = (x_bounds[1] - x_bounds[0]) / (colcount - 1)
        yres = (y_bounds[1] - y_bounds[0]) / (rowcount - 1)

        projection_transform = [
            xres,
            0,
            x_bounds[0] - xres / 2,
            0,
            yres,
            y_bounds[0] - yres / 2,
        ]
        projection_bbox = [x_bounds[0], y_bounds[0], x_bounds[1], y_bounds[1]]

        use_bbox_geom = image_type == ImageType.FULL_DISK

        if not use_bbox_geom:
            projection_geometry = Polygon(
                [
                    (x_bounds[0], y_bounds[0]),
                    (x_bounds[0], y_bounds[1]),
                    (x_bounds[1], y_bounds[1]),
                    (x_bounds[1], y_bounds[0]),
                ]
            )

            geometry = reproject_geom(crs, "EPSG:4326", mapping(projection_geometry))

            ensure_no_antimeridian_crossing(geometry)

            # Check if there are any infinities in the geom,
            # if so then just use bbox.
            shp = shape(geometry)
            use_bbox_geom = not shp.is_valid

        if use_bbox_geom:
            # Full disk images don't map to espg:4326 well
            # Just use the bbox
            # https://github.com/stactools-packages/goes/issues/4
            geometry = mapping(box(*bbox))

            ensure_no_antimeridian_crossing(geometry)

        return DatasetGeometry(
            projection_wkt2=projection_wkt2,
            projection_shape=projection_shape,
            projection_transform=projection_transform,
            projection_bbox=projection_bbox,
            bbox=bbox,
            footprint=geometry,
        )


@dataclass
class Dataset:
    """A GOES netcdf dataset."""

    file_name: ABIL2FileName
    global_attributes: GlobalAttributes
    geometry: DatasetGeometry
    asset_variables: List[str]
    """Keys are variable names, values are long description.

    Only captures variables that are images."""

    @classmethod
    def from_nc(cls, file_name: ABIL2FileName, nc: File) -> "Dataset":
        global_attributes = GlobalAttributes.from_nc(nc)
        geometry = DatasetGeometry.from_nc(nc, file_name.image_type)

        asset_variables = [key for key in nc.keys() if len(nc[key].shape) == 2]

        return Dataset(
            file_name=file_name,
            global_attributes=global_attributes,
            geometry=geometry,
            asset_variables=asset_variables,
        )
