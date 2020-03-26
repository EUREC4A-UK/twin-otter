import datetime

import numpy as np
from osgeo import gdal


# GOES data parameters
# Filename
goes_filename = '{layer}_{year:04d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}.tiff'
# Time Resolution
resolution = datetime.timedelta(minutes=10)

# Defaults (for EUREC4A)
default_layer = 'GOES-East_ABI_Band2_Red_Visible_1km'
# Spatial resolution (degrees)
default_resolution = 0.01
# Image extent [S, W, N, E]
default_bbox = [10., -60., 15., -50.]


def filename_at_time(time, layer=default_layer):
    return goes_filename.format(
        layer=layer,
        year=time.year,
        month=time.month,
        day=time.day,
        hour=time.hour,
        minute=time.minute
    )


def load_image(filename):
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
