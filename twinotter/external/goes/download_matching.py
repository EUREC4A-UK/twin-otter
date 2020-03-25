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

import re
import datetime
import pytz

import worldview_dl

import twinotter
from twinotter import summary


# Resolution of GOES data (constant)
goes_time_resolution = datetime.timedelta(minutes=10)

# Filename
goes_filename = '{layer}_{year:04d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}.tiff'

bbox = [10., -60., 15., -50.]
layer = 'GOES-East_ABI_Band2_Red_Visible_1km'

resolution = 0.01


def main():
    _parse_docopt_arguments(get_images, __doc__)
    return


def get_images(flight_data_path, output='.'):
    dataset = twinotter.load_flight(flight_data_path)

    date = summary.extract_date(dataset)
    date = date.astimezone(pytz.utc)

    start = date + summary.extract_time(dataset, 'time_coverage_start')
    end = date + summary.extract_time(dataset, 'time_coverage_end')

    start = round_datetime(start, goes_time_resolution)
    end = round_datetime(end, goes_time_resolution) + goes_time_resolution

    time = start
    while time <= end:
        # Create the output filename
        filename = goes_filename.format(
            layer=layer,
            year=time.year,
            month=time.month,
            day=time.day,
            hour=time.hour,
            minute=time.minute)
        print(filename)

        worldview_dl.download_image(
            fn=filename,
            time=time,
            bbox=bbox,
            layers=[layer, 'Reference_Labels'],
            image_format="tiff",
            resolution=resolution,
        )
        time += goes_time_resolution

    return


def round_datetime(time, resolution):
    excess = datetime.timedelta(
        days=time.day,
        hours=time.hour,
        minutes=time.minute,
        seconds=time.second,
        microseconds=time.microsecond
    ) % resolution

    return time - excess


def _parse_docopt_arguments(function, __doc__):
    """

    Args:
        function:
        __doc__: The docstring of the function being parsed

    Returns:

    """
    # Load in the arguments
    import docopt
    arguments = docopt.docopt(__doc__)

    # Remove the help and version options
    del arguments['--help']

    # Parse the remaining arguments
    parsed_arguments = {}
    for arg in arguments.keys():
        # Arguments specified as all upper case (<ARG>)
        if arg.upper() == arg:
            newarg = arg
        # Arguments specified in angle brackets (<arg>)
        elif re.match(r"<(.*)>", arg):
            newarg = re.match(r"<(.*)>", arg).groups()[0]
        # Arguments specific with dashes (-arg | --arg)
        elif re.match(r"-+(.*)", arg):
            newarg = re.match(r"-+(.*)", arg).groups()[0]
        else:
            raise KeyError("Couldn't parse argument {}".format(arg))

        parsed_arguments[newarg] = arguments[arg]

    # Call the function and return
    return function(**parsed_arguments)


if __name__ == "__main__":
    main()
