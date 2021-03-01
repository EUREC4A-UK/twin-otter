import re
import pathlib
import datetime

import parse
import numpy as np
import xarray as xr

from . import plot


#: Filename pattern of netCDF files on the AERIS server
nc_filename = (
    "clavrx_OR_ABI-L1b-RadF-M6C01_G16_s"
    "{year:04d}{day:03d}{hour:02d}{minute:02d}"
    "{something}_BARBADOS-2KM-FD.level2.nc"
)

# GOES data parameters
filename_format = (
    "{layer}_{year:04d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}.tiff"
)
time_resolution = datetime.timedelta(minutes=10)

# Defaults (for EUREC4A)
default_layer = "GOES-East_ABI_Band2_Red_Visible_1km"
# Spatial resolution (degrees)
default_spatial_resolution = 0.01
# Image extent [S, W, N, E]
default_bbox = [10.0, -60.0, 15.0, -50.0]


def filename_at_time(time, layer=default_layer):
    return filename_format.format(
        layer=layer,
        year=time.year,
        month=time.month,
        day=time.day,
        hour=time.hour,
        minute=time.minute,
    )


def time_from_filename(filename):
    image_info = parse.parse(filename_format, filename).named
    del image_info["layer"]

    return datetime.datetime(**image_info)


def find_images_in_path(path, layer=default_layer):
    # Use a specific layer or use layer "*" to get all layers
    # Replace all times with "*" to search for all images
    filename_to_search = re.sub(r"\{\w+:\d\dd}", "*", filename_format).format(
        layer=layer
    )

    # Use pathlib to search the give path for all matching filenames
    path = pathlib.Path(path)
    return sorted(list(path.rglob(filename_to_search)))


def _load_image(filename):
    from osgeo import gdal

    # Load GeoTiff data
    ds = gdal.Open(filename)

    # Get the dimentions of column and row
    nc = ds.RasterXSize
    nr = ds.RasterYSize

    # Read elevation data
    # The first dimension of the array is RGB but they are all the same so just return
    # the first on for now. May need to change this if we can get colour satellite
    # images
    data = ds.ReadAsArray()[0]

    # Get Longitude and Latitude info
    geotransform = ds.GetGeoTransform()
    x_origin = geotransform[0]
    y_origin = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    # Generate Longitude and Latitude array
    lons = x_origin + np.arange(0, nc) * pixel_width
    lats = y_origin + np.arange(0, nr) * pixel_height

    return lons, lats, data


def load_nc(path, time):
    """Load the netCDF dataset corresponding to the given time

    This function finds files matching the AERIS :data:`nc_filename` formatted for the
    given time

    Args:
        path (str): The directory containing GOES netCDF files
        time (datetime.datetime): The time of the file to load

    Returns:
        xarray.dataset: The loaded netCDF file with values filtered where the
            coordinates are NaN

    Raises:
        FileNotFoundError: If the netCDF is not present

        FileExistsError: If multiple matching netCDF files are found with the same name
    """
    filename = nc_filename.format(
        year=time.year,
        day=time.timetuple().tm_yday,
        hour=time.hour,
        minute=time.minute,
        something="*",
    )

    # Find matching filenames in the GOES folder
    file_path = list(pathlib.Path(path).rglob(filename))

    if len(file_path) == 0:
        raise FileNotFoundError("No GOES data found in {} for {}".format(path, time))
    elif len(file_path) > 1:
        raise FileExistsError(
            "More than one file found in {} for {}".format(path, time)
        )

    dataset = xr.load_dataset(str(file_path[0]))

    # Remove values where the coordinates are NaNs
    dataset = dataset.where(~dataset.longitude.isnull(), drop=True)

    return dataset
