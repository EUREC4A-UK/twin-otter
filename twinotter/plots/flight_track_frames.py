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
import numpy as np
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
    # Load flight data
    dataset = twinotter.load_flight(flight_data_path)

    # Get start and end time for satellite data from flight
    date = summary.extract_date(dataset)

    start = date + summary.extract_time(dataset, 'time_coverage_start')
    end = date + summary.extract_time(dataset, 'time_coverage_end')

    start = twinotter.util.round_datetime(start, goes.time_resolution)
    end = twinotter.util.round_datetime(end, goes.time_resolution) + goes.time_resolution

    time = start
    # Loop over satellite images
    n = 0
    while time <= end:
        goes_data = goes.load_nc(goes_path, time)

        # create figure
        bbox = [-60, -56.4, 12, 14.4]
        domain_aspect = (bbox[3] - bbox[2]) / (bbox[1] - bbox[0])
        fig = plt.figure(figsize=(11., domain_aspect * 10), dpi=96)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent(bbox, crs=ccrs.PlateCarree())
        fig.tight_layout()

        plt.pcolormesh(
            goes_data.longitude,
            goes_data.latitude,
            goes_data.refl_0_65um_nom,
            cmap='Greys_r')

        # Plot the flight track between the previous and next satellite image
        try:
            idx_s = int(np.where(
                dataset.Time == (time - date - goes.time_resolution).total_seconds())[0])
        except TypeError:
            # If we try to before the dataset we get a TypeError as np.where doesn't
            # return anything
            idx_s = 0
        try:
            idx_f = int(np.where(
                dataset.Time == (time - date + goes.time_resolution).total_seconds())[0])
        except TypeError:
            # Same as above but for looking at the end of the dataset
            idx_f = -1

        plots.plot_flight_path(ax=ax, ds=dataset.isel(Time=slice(idx_s, idx_f)))
        eurec4a.add_halo_circle(ax)

        path_fig = output_path + '/' + 'flight{}_track_frame_{:03d}.png'.format(
            dataset.attrs['flight_number'], n)
        plt.savefig(path_fig, bbox_inches='tight')
        print("Saved flight track to `{}`".format(str(path_fig)))

        time += goes.time_resolution
        n += 1

    return


if __name__ == '__main__':
    main()
