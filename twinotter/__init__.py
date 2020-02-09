from pathlib import Path

import pandas as pd
import xarray as xr


# netCDF naming: core_masin_YYYYMMDD_rNNN_flightNNN_Nhz.nc
MASIN_CORE_FORMAT = "core_masin_{date}_r{revision}_flight{flight_number}_{frequency}hz.nc"
MASIN_CORE_RE = "core_masin_(?P<date>\d{8})_r(?P<revision>\d{3})_flight(?P<flight_num>\d{3})_(?P<freq>\d+)hz\.nc"


def load_flight(flight_number, frequency=1, revision="most_recent", debug=False):
    filename = generate_file_path(flight_number, frequency)

    if revision == "most_recent":
        revision = "*"
    else:
        revision = "{:03d}".format(revision)

    ds = xr.open_dataset(filename, decode_cf=False)
    if debug:
        print("Loaded {}".format(filename))

    # drop points where lat/lon aren't given (which means the flag is 0
    # "quality_good"
    ds = ds.where(ds.LON_OXTS_FLAG==0, drop=True)
    # drop nans too...
    ds = ds.where(~ds.LON_OXTS.isnull(), drop=True)

    # XXX: quick fix until we get loading with CF-convention parsing working
    ds = ds.where(ds.LON_OXTS!=ds.LON_OXTS._FillValue, drop=True)

    # plot as function of time
    ds = ds.swap_dims(dict(data_point='Time'))

    ds.attrs['source_file'] = filename
    ds.attrs['flight_number'] = meta[filename]['flight_num']

    return ds


def flight_leg_index(flight_number, leg_name, leg_number=0):
    """Get a slice representing a single section of the flight

    Args:
        flight_number (int):
        leg_name (str):
        leg_number (int): For multiple of the same type of leg within a flight,
            select which leg you want. Default is zero

    Returns:
        slice:
    """
    legs = pd.read_csv('obs/legs_flight{}.csv'.format(flight_number))
    idx = legs[legs['Type'] == leg_name].index[leg_number]
    start = legs['Start'][idx]
    end = legs['End'][idx]

    return slice(start, end)


def generate_file_path(flight_number, date, frequency=1, revision=1):
    # Make the filename
    filename = MASIN_CORE_FORMAT.format(
        flight_number=flight_number,
        date=date.replace('-', ''),
        frequency=frequency,
        revision='{:03d}'.format(revision)
    )

    # Find all matching files in the obs directory
    file_path = list(Path('obs/').rglob(filename))

    # Should only be one of these files
    if len(file_path) == 1:
        return file_path[0]
    elif len(file_path) > 1:
        raise FileExistsError(
            'Multiple files found matching {}'.format(filename))
    else:
        raise FileNotFoundError(
            'No files found matching {}'.format(filename))
