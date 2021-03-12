"""
::

    Usage:
        flight_track_frames.py  <flight_data_path>
            [<lon_min> <lon_max> <lat_min> <lat_max> <resolution>]
            [--goes_path=<path>]
            [--output_path=<path>]
        flight_track_frames.py  (-h | --help)

    Arguments:
        <flight_data_path>  Input flight data

    Options:
        -h --help           Show help
        --goes_path=<path>
            Folder containing downloaded GOES images [default: .]
        --output_path=<path>
            Folder to put the output frames in [default: .]

"""

import datetime

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import xarray as xr

from .. import load_flight, plots, util
from ..util import scripting
from ..external import eurec4a, goes


def main():
    scripting.parse_docopt_arguments(generate, __doc__)
    return


def generate(
    flight_data_path,
    lon_min=-60,
    lon_max=-56.4,
    lat_min=12,
    lat_max=14.4,
    resolution=0.01,
    goes_path=".",
    output_path=".",
):
    substep = datetime.timedelta(minutes=1)

    # Setup the grid to interpolate the satellite data on to
    lon = np.arange(lon_min, lon_max, resolution)
    lat = np.arange(lat_min, lat_max, resolution)
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    # Load flight data
    dataset = load_flight(flight_data_path)

    # Get start and end time for satellite data from flight
    start = dataset.Time[0].data.astype("M8[ms]").astype("O")[()]
    end = dataset.Time[-1].data.astype("M8[ms]").astype("O")[()]

    # Start the satellite images at the nearest time to the flight start
    sat_image_time = util.round_datetime(start, goes.time_resolution)

    # Loop over satellite images
    n = 0
    # Start on the minute
    time = util.round_datetime(start, datetime.timedelta(minutes=1), mode="ceil")
    while time <= end:
        # Load the current satellite image
        goes_data = goes.load_nc(goes_path, sat_image_time)

        # Interpolate the satellite data to a regular grid
        goes_data_grid = xr.Dataset(coords=dict(latitude=lat, longitude=lon))
        for band in ["refl_0_65um_nom", "refl_0_86um_nom", "refl_0_47um_nom"]:
            band_grid = griddata(
                (
                    goes_data["longitude"].values.flatten(),
                    goes_data["latitude"].values.flatten(),
                ),
                goes_data[band].values.flatten(),
                (lon_grid, lat_grid),
            )

            goes_data_grid[band] = (["latitude", "longitude"], band_grid)

        sat_image_time += goes.time_resolution
        while time < sat_image_time - goes.time_resolution / 2 and time <= end:
            fig, ax = make_frame(goes_data_grid)

            overlay_flight_path_segment(ax, dataset, time)

            path_fig = (
                output_path
                + "/"
                + "flight{}_track_frame_{:03d}.png".format(
                    dataset.attrs["flight_number"], n
                )
            )
            plt.text(
                0, 0, str(time), transform=ax.transAxes, fontdict=dict(color="green")
            )
            plt.savefig(path_fig, bbox_inches="tight")
            print("Saved flight track to `{}`".format(str(path_fig)))
            plt.close()

            time += substep
            n += 1


def make_frame(goes_data):
    # create figure
    bbox = [-60, -56.4, 12, 14.4]
    domain_aspect = (bbox[3] - bbox[2]) / (bbox[1] - bbox[0])
    fig = plt.figure(figsize=(11.0, domain_aspect * 10), dpi=96)
    projection = ccrs.PlateCarree()
    ax = plt.axes(projection=projection)

    plots.add_land_and_sea(ax)

    # Plot the current satellite image
    goes.plot.geocolor(ax, goes_data, projection)

    eurec4a.add_halo_circle(ax, color="teal", linewidth=3)

    ax.set_extent(bbox, crs=projection)

    return fig, ax


def overlay_flight_path_segment(ax, flight_data, time):
    # Plot the flight track +- the satellite resolution
    start = time - goes.time_resolution
    end = time + goes.time_resolution

    # Plot the full flight path in a faded red
    plots.flight_path(
        ax=ax,
        ds=flight_data,
        vmin=-10,
        vmax=0,
        cmap="Reds",
        alpha=0.3,
        linewidths=3,
        add_cmap=False,
    )

    # Plot the +-10 mins of flight path normally
    plots.flight_path(
        ax=ax,
        ds=flight_data.sel(Time=slice(start, end)),
        cmap="cool",
        mark_end_points=False,
    )

    # Add a marker with the current position and rotation
    plots.add_flight_position(ax, flight_data.sel(Time=time))


if __name__ == "__main__":
    main()
