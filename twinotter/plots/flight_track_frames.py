"""

Usage:
    flight_track_frames.py  <flight_data_path> [<goes_path>] [-o <output_path>]
    flight_track_frames.py  (-h | --help)

Arguments:
    <flight_data_path>  Input flight data
    <goes_path>         Folder containing downloaded GOES images [Default: "."]
    <output_path>       Folder to put the output frames in [Default: "."]

Options:
    -h --help        Show help
    -o --output_path

"""
import datetime

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import twinotter
from twinotter import plots, summary
from twinotter.external import eurec4a, goes
from twinotter.util import scripting


def main():
    scripting.parse_docopt_arguments(generate, __doc__)
    return


def generate(flight_data_path, goes_path=".", output_path="."):
    substep = datetime.timedelta(minutes=1)

    # Load flight data
    dataset = twinotter.load_flight(flight_data_path)

    # Get start and end time for satellite data from flight
    start = summary.extract_time(dataset, 'time_coverage_start')
    end = summary.extract_time(dataset, 'time_coverage_end')

    # Get corresponding satellite time for start
    date = summary.extract_date(dataset)
    sat_image_time = twinotter.util.round_datetime(date + start, goes.time_resolution)

    # Loop over satellite images
    n = 0
    # Start on the minute
    time = twinotter.util.round_datetime(
        start, datetime.timedelta(minutes=1), mode='ceil')
    while time <= end:
        # Load the current satellite image
        goes_data = goes.load_nc(goes_path, sat_image_time)

        sat_image_time += goes.time_resolution
        while time < sat_image_time - date - goes.time_resolution / 2:
            # create figure
            bbox = [-60, -56.4, 12, 14.4]
            domain_aspect = (bbox[3] - bbox[2]) / (bbox[1] - bbox[0])
            plt.figure(figsize=(11., domain_aspect * 10), dpi=96)
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_extent(bbox, crs=ccrs.PlateCarree())

            plots.add_land_and_sea(ax)

            # Plot the current satellite image
            plt.pcolormesh(
                goes_data.longitude,
                goes_data.latitude,
                goes_data.refl_0_65um_nom,
                cmap='Greys_r')

            eurec4a.add_halo_circle(ax, color='teal', linewidth=3)

            # Plot the flight track +- the satellite resolution
            try:
                idx_s = twinotter.index_from_time(
                    time - goes.time_resolution, dataset.Time)
            except TypeError:
                # If we try to before the dataset we get a TypeError as np.where doesn't
                # return anything
                idx_s = 0
            try:
                idx_f = twinotter.index_from_time(
                    time + goes.time_resolution, dataset.Time)
            except TypeError:
                # Same as above but for looking at the end of the dataset
                idx_f = -1

            # Plot the full flight path in a faded red
            plots.plot_flight_path(ax=ax, ds=dataset, vmin=-10, vmax=0, cmap='Reds', alpha=0.3, linewidths=3, add_cmap=False)

            # Plot the +-10 mins of flight path normally
            plots.plot_flight_path(ax=ax, ds=dataset.isel(Time=slice(idx_s, idx_f)), cmap='cool', mark_end_points=False)

            # Add a marker with the current position and rotation
            ds_now = dataset.isel(Time=int((idx_s + idx_f)/2))
            plots.add_flight_position(ax, ds_now)

            path_fig = output_path + '/' + 'flight{}_track_frame_{:03d}.png'.format(
                dataset.attrs['flight_number'], n)
            plt.text(0, 0, str(time), transform=ax.transAxes, fontdict=dict(color='green'))
            plt.savefig(path_fig, bbox_inches='tight')
            print("Saved flight track to `{}`".format(str(path_fig)))
            plt.close()

            time += substep
            n += 1

    return


if __name__ == '__main__':
    main()
