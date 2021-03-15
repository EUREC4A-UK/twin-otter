from pathlib import Path
import re

import yaml
import xarray as xr


# netCDF naming: core_masin_YYYYMMDD_rNNN_flightNNN_Nhz.nc
MASIN_CORE_FORMAT = "core_masin_{date}_r{revision}_flight{flight_num}_{freq}hz.nc"
MASIN_CORE_RE = "core_masin_(?P<date>\d{8})_r(?P<revision>\d{3})_flight(?P<flight_num>\d{3})_(?P<freq>\d+)hz\.nc"

# A nice way of formatting the flight time
time_of_day_format = "{hours:02d}:{minutes:02d}:{seconds:02d}"


def _monkey_patch_xr_load():
    # by the CF-convections units should always be a string
    # http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html#units
    # fix here as it breaks cf-convention loading in xarray otherwise

    def _fix_var(var):
        if var.attrs["units"] == 1:
            var.attrs["units"] = "1"

    _decode_variable_old = xr.conventions.decode_cf_variable

    def _decode_cf_variable(name, var, *args, **kwargs):
        _fix_var(var)
        return _decode_variable_old(name=name, var=var, *args, **kwargs)

    xr.conventions.decode_cf_variable = _decode_cf_variable

    _decode_variables_old = xr.conventions.decode_cf_variables

    def _decode_cf_variables(variables, *args, **kwargs):
        for var in variables:
            _fix_var(variables[var])
        return _decode_variables_old(variables, *args, **kwargs)

    xr.conventions.decode_cf_variables = _decode_cf_variables


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
    files = list((Path(flight_data_path) / "MASIN").glob(fn_pattern))

    meta = {}
    for file in files:
        meta[file] = re.match(MASIN_CORE_RE, file.name).groupdict()

    if len(files) == 0:
        raise FileNotFoundError(
            "Couldn't find MASIN data in `{}/MASIN`, "
            "please place data there.".format(flight_data_path)
        )

    if len(files) > 1:
        if revision == "*":
            filename = sorted(files, key=lambda v: meta[v]["revision"], reverse=True)[0]
        else:
            raise FileExistsError(
                "More than one MASIN file was found: `{}`".format(", ".join(files))
            )
    else:
        filename = files[0]

    ds = open_masin_dataset(filename, meta[filename], debug=debug)

    return ds


def open_masin_dataset(filename, meta, debug=False):
    _monkey_patch_xr_load()
    ds = xr.open_dataset(filename, decode_cf=True)
    if debug:
        print("Loaded {}".format(filename))

    # drop points where lat/lon aren't given (which means the flag is 0
    # "quality_good"
    ds = ds.where(ds.LON_OXTS_FLAG == 0, drop=True)
    # drop nans too...
    ds = ds.where(~ds.LON_OXTS.isnull(), drop=True)

    # plot as function of time
    ds = ds.swap_dims(dict(data_point="Time"))

    ds.attrs["source_file"] = filename
    ds.attrs["flight_number"] = meta["flight_num"]

    return ds


def load_segments(filename):
    """Read a segments yaml file created with twinotter.plots.interactive_flight_track

    Args:
        filename (str):

    Returns:
        dict:
    """
    with open(filename, "r") as data:
        segments = yaml.load(data, yaml.CLoader)

    return segments


def _matching_segments(segments, segment_type):
    return [seg for seg in segments["segments"] if segment_type in seg["kinds"]]


def count_segments(segments, segment_type):
    """Return the number of flight segments of the requested segment_type

    Args:
        segments (dict): Flight segments description from load_segments
        segment_type (str): The label of a segment type

    Returns:
        int:

    """
    return len(_matching_segments(segments, segment_type))


def extract_segments(ds, segments, segment_type, segment_idx=None):
    """Extract a subset of the given dataset with the segments requested

    Args:
        ds (xarray.DataSet): Flight dataset
        segments (dict): Flight segments description from load_segments
        segment_type (str): The label of a segment type
        segment_idx (int): The index of the segment within the flight (starts at zero)
            If the default of None is given then the returned dataset will contain all
            matching segments concatenated.

    Returns:
        xarray.DataSet:

    """
    # All segments of the requested type
    matching_segments = _matching_segments(segments, segment_type)

    # If a single index is requested return that index of legs with the requested type
    if segment_idx is not None:
        segment = matching_segments[segment_idx]
        return ds.sel(Time=slice(segment["start"], segment["end"]))

    # Otherwise merge all legs with the requested type
    else:
        ds_matching = []
        for segment in matching_segments:
            ds_matching.append(ds.sel(Time=slice(segment["start"], segment["end"])))

        return xr.concat(ds_matching, dim="Time")


def generate_file_path(
    flight_number, date, frequency=1, revision=1, flight_data_path=None
):
    # Make the filename
    filename = MASIN_CORE_FORMAT.format(
        flight_num=flight_number,
        date=date.replace("-", ""),
        freq=frequency,
        revision="{:03d}".format(revision),
    )

    # Find all matching files in the obs directory
    file_path = list(Path(flight_data_path).rglob(filename))

    # Should only be one of these files
    if len(file_path) == 1:
        return file_path[0]
    elif len(file_path) > 1:
        raise FileExistsError("Multiple files found matching {}".format(filename))
    else:
        raise FileNotFoundError("No files found matching {}".format(filename))
