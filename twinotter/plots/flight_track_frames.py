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

    # Get GOES images filenames
    goes_images = goes.find_images_in_path(goes_path)

    # Selecting matching times
    date = summary.extract_date(dataset)

    start = date + summary.extract_time(dataset, 'time_coverage_start')
    end = date + summary.extract_time(dataset, 'time_coverage_end')

    start = twinotter.util.round_datetime(start, goes.time_resolution)
    end = twinotter.util.round_datetime(end, goes.time_resolution) + goes.time_resolution

    keep = []
    for filename in goes_images:
        if start < goes.time_from_filename(str(filename)) < end:
            keep.append(filename)

    if len(keep) == 0:
        raise FileNotFoundError("No GOES images found matching the time for the given"
                                "flight")
    goes_images = keep

    # Loop over satellite images
    for n, filename in enumerate(goes_images):
        # create figure
        bbox = [-60, -56.4, 12, 14.4]
        domain_aspect = (bbox[3] - bbox[2]) / (bbox[1] - bbox[0])
        fig = plt.figure(figsize=(11., domain_aspect * 10), dpi=96)
        ax = plt.axes(projection=ccrs.PlateCarree())
        eurec4a.add_halo_circle(ax)
        ax.set_extent(bbox, crs=ccrs.PlateCarree())
        fig.tight_layout()

        plt.pcolormesh(*goes.load_image(str(filename)), cmap='Greys_r')
        plots.plot_flight_path(ax=ax, ds=dataset)

        path_fig = output_path + '/' + 'flight{}_track_frame_{:03d}.png'.format(
            dataset.flight_number, n)
        plt.savefig(path_fig, bbox_inches='tight')
        print("Saved flight track to `{}`".format(str(path_fig)))

    return


if __name__ == '__main__':
    main()
