from pathlib import Path
import re
import datetime

import parse
import numpy as np
import xarray as xr


# netCDF naming: core_masin_YYYYMMDD_rNNN_flightNNN_Nhz.nc
MASIN_CORE_FORMAT = "core_masin_{date}_r{revision}_flight{flight_num}_{freq}hz.nc"
MASIN_CORE_RE = "core_masin_(?P<date>\d{8})_r(?P<revision>\d{3})_flight(?P<flight_num>\d{3})_(?P<freq>\d+)hz\.nc"


def load_flight(flight_data_path, frequency=1, revision="most_recent", debug=False):
    # If a path to a netCDF file is specified just load it
    if Path(flight_data_path).is_file():
        meta = re.match(MASIN_CORE_RE, Path(flight_data_path).name).groupdict()
        return open_masin_dataset(flight_data_path, meta, debug=debug)

    # Otherwise a directory is supplied so look for files that match within
    # the given directory

    # If you want to use the most recent revision, get the filenames of all the
    # revisions and choose the newest one
    if revision == "most_recent":
        revision = "*"
    else:
        revision = "{:03d}".format(revision)

    fn_pattern = MASIN_CORE_FORMAT.format(
        date="*", revision=revision, flight_num="*", freq=frequency
    )
    files = list((Path(flight_data_path)/"MASIN").glob(fn_pattern))

    meta = {}
    for file in files:
        meta[file] = re.match(MASIN_CORE_RE, file.name).groupdict()

    if len(files) == 0:
        raise Exception("Couldn't find MASIN data in `{}/MASIN`, please place"
                        " data there.".format(flight_data_path))

    if len(files) > 1:
        if revision == "*":
            filename = sorted(files, key=lambda v: meta[v]['revision'], reverse=True)[0]
        else:
            raise Exception("More than one MASIN file was found: `{}`".format(
                ", ".join(files)
            ))
    else:
        filename = files[0]

    ds = open_masin_dataset(filename, meta[filename], debug=debug)

    return ds


def open_masin_dataset(filename, meta, debug=False):
    ds = xr.open_dataset(filename, decode_cf=False)
    if debug:
        print("Loaded {}".format(filename))

    # drop points where lat/lon aren't given (which means the flag is 0
    # "quality_good"
    ds = ds.where(ds.LON_OXTS_FLAG == 0, drop=True)
    # drop nans too...
    ds = ds.where(~ds.LON_OXTS.isnull(), drop=True)

    # XXX: quick fix until we get loading with CF-convention parsing working
    ds = ds.where(ds.LON_OXTS != ds.LON_OXTS._FillValue, drop=True)

    # plot as function of time
    ds = ds.swap_dims(dict(data_point='Time'))

    ds.attrs['source_file'] = filename
    ds.attrs['flight_number'] = meta['flight_num']

    return ds


def flight_leg_times(flight_legs, leg_name, leg_number=0):
    """Get a slice representing a single section of the flight

    Args:
        flight_legs (pandas.DataFrame):
        leg_name (str):
        leg_number (int): For multiple of the same type of leg within a flight,
            select which leg you want. Default is zero

    Returns:
        slice:
    """
    idx = flight_legs[flight_legs['Label'] == leg_name].index[leg_number]
    start = flight_legs['Start'][idx]
    end = flight_legs['End'][idx]

    return start, end


def index_from_time(timestr, time):
    """

    Args:
        timestr (str): A string representing time of day formatted as "HH:MM:SS"
        time (array):

    Returns:
        int:
    """
    HH, MM, SS = parse.parse("{:d}:{:d}:{:d}", timestr)
    dt = datetime.timedelta(hours=HH, minutes=MM, seconds=SS)

    idx = int(np.where(time == dt.total_seconds())[0])

    return idx


def generate_file_path(flight_number, date, frequency=1, revision=1, flight_data_path=None):
    # Make the filename
    filename = MASIN_CORE_FORMAT.format(
        flight_num=flight_number,
        date=date.replace('-', ''),
        freq=frequency,
        revision='{:03d}'.format(revision)
    )

    # Find all matching files in the obs directory
    file_path = list(Path(flight_data_path).rglob(filename))

    # Should only be one of these files
    if len(file_path) == 1:
        return file_path[0]
    elif len(file_path) > 1:
        raise FileExistsError(
            'Multiple files found matching {}'.format(filename))
    else:
        raise FileNotFoundError(
            'No files found matching {}'.format(filename))
