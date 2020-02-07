import pandas as pd
import xarray as xr
from pathlib import Path
import re


flight_info = pd.read_csv('obs/flight_information.csv')

MASIN_CORE_FORMAT = "core_masin_{date}_r{revision}_flight{flight_num}_{freq}hz.nc"
MASIN_CORE_RE = "core_masin_(?P<date>\d{8})_r(?P<revision>\d{3})_flight(?P<flight_num>\d{3})_(?P<freq>\d+)hz\.nc"

def load_flight(flight_data_path, frequency=1, revision="most_recent"):
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

    ds = xr.open_dataset(filename, decode_cf=False)

    # drop points where lat/lon aren't given (which means the flag is 0
    # "quality_good"
    ds = ds.where(ds.LON_OXTS_FLAG==0, drop=True)
    # drop nans too...
    ds = ds.where(~ds.LON_OXTS.isnull(), drop=True)

    # XXX: quick fix until we get loading with CF-convention parsing working
    ds = ds.where(ds.LON_OXTS!=ds.LON_OXTS._FillValue, drop=True)

    # plot as function of time
    ds = ds.swap_dims(dict(data_point='Time'))

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
