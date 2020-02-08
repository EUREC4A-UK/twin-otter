import pandas as pd
import xarray as xr
from pathlib import Path
import re

import xarray as xr


# flight_info = pd.read_csv('obs/flight_information.csv')

MASIN_CORE_FORMAT = "core_masin_{date}_r{revision}_flight{flight_num}_{freq}hz.nc"
MASIN_CORE_RE = "core_masin_(?P<date>\d{8})_r(?P<revision>\d{3})_flight(?P<flight_num>\d{3})_(?P<freq>\d+)hz\.nc"

def _monkey_patch_xr_load():
    # by the CF-convections units should always be a string
    # http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html#units
    # fix here as it breaks cf-convention loading in xarray otherwise
    import xarray.conventions

    _decode_old = xarray.conventions.decode_cf_variable
    def _decode_cf_variable(name, var, *args, **kwargs):
        if var.attrs['units'] == 1:
            var.attrs['units'] = "1"
        return _decode_old(name=name, var=var, *args, **kwargs)

    xarray.conventions.decode_cf_variable = _decode_cf_variable

def load_flight(flight_data_path, frequency=1, revision="most_recent", debug=False,
                filter_invalid=True):
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

    _monkey_patch_xr_load()
    ds = xr.open_dataset(filename)

    if debug:
        print("Loaded {}".format(filename))

    if filter_invalid:
        # drop points where lat/lon aren't given (which means the flag is 0
        # "quality_good"
        ds = ds.where(ds.LON_OXTS_FLAG==0, drop=True)
        # drop nans too...
        ds = ds.where(~ds.LON_OXTS.isnull(), drop=True)

    # plot as function of time
    ds = ds.swap_dims(dict(data_point='Time'))

    ds.attrs['source_file'] = filename
    ds.attrs['flight_number'] = meta[filename]['flight_num']

    return ds


def flight_leg_index(flight_data_path, leg_name, leg_number=0):
    """Get a slice representing a single section of the flight

    Args:
        flight_data_path (str):
        leg_name (str):
        leg_number (int): For multiple of the same type of leg within a flight,
            select which leg you want. Default is zero

    Returns:
        slice: 
    """
    p = Path(flight_data_path)/"flight_legs.csv"
    legs = pd.read_csv(p)
    idx = legs[legs['Type'] == leg_name].index[leg_number]
    start = legs['Start'][idx]
    end = legs['End'][idx]

    return slice(start, end)
