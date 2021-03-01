"""Download all GOES satellite images during the given flight.

Data is downloaded to the current working directory

Usage:
    download_matching.py  <flight_data_path>
    download_matching.py  (-h | --help)

Arguments:
    <flight_data_path>  Input flight data

Options:
    -h --help        Show help

"""
import pytz

import worldview_dl

from .. import goes
from ... import load_flight, summary, util
from ...util import scripting


def main():
    scripting.parse_docopt_arguments(get_images, __doc__)
    return


def get_images(
    flight_data_path,
    layer=goes.default_layer,
    image_resolution=goes.default_spatial_resolution,
    bbox=goes.default_bbox,
):
    """Download all GOES images during the time of the specified flight

    Args:
        flight_data_path: The path to the MASIN flight data file or directory
        layer: The GOES image layer to use. Also used as the prefix of the filename
        image_resolution (float):
        bbox: The spatial area to use in the format [S W N E] with units degrees
    """
    dataset = load_flight(flight_data_path)

    date = summary.extract_date(dataset)
    date = date.astimezone(pytz.utc)

    start = date + summary.extract_time(dataset, "time_coverage_start")
    end = date + summary.extract_time(dataset, "time_coverage_end")

    start = util.round_datetime(start, goes.time_resolution)
    end = util.round_datetime(end, goes.time_resolution) + goes.time_resolution

    time = start
    while time <= end:
        # Create the output filename
        filename = goes.filename_at_time(time, layer=layer)
        print(filename)

        worldview_dl.download_image(
            fn=filename,
            time=time,
            bbox=bbox,
            layers=[layer, "Reference_Labels"],
            image_format="tiff",
            resolution=image_resolution,
        )
        time += goes.time_resolution

    return


if __name__ == "__main__":
    main()
