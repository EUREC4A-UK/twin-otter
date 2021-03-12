"""
Module to work with CSV files of measurements of Cloud Condensation Nuclei
measurements from the CCN-100 probe

"A DMT single-column cloud condensation counter model measures the spectrum of
CCN concentration as a function of supersaturation continuously using
uninterrupted flow and a multichannel, optical particle counter that measures
the size of the activated droplet."
"""

import xarray as xr
import pandas as pd
from pathlib import Path


def _load_meta(fn, nlines=3):
    meta = {}
    with open(fn) as fh:
        for n in range(3):
            line = fh.readline()
            key, value = line.split(",")
            meta[key.strip().lower()] = value.strip()
    return meta


def load_csv(fn, n_header_lines=3):
    """
    Load CCN datafile with filename `fn` and return as xarray.Dataset
    """
    meta = _load_meta(fn, nlines=n_header_lines)
    df = pd.read_csv(fn, skiprows=n_header_lines)
    # cleanup column names
    df.columns = [s.strip().lower().replace(" ", "_") for s in df.columns]
    # make times into datetimes
    df["time"] = meta["date"] + "T" + df["time"] + "Z"
    df["time"] = pd.to_datetime(df["time"], format="%m/%d/%yT%H:%M:%SZ", utc=True)

    ds = xr.Dataset.from_dataframe(df)
    ds = ds.swap_dims(dict(index="time"))

    ds.attrs.update(meta)

    return ds


def load_all(data_path):
    """
    Load all CCN files in `data_path` and combine into single xarray.Dataset
    """
    all_ds = [load_csv(fn=fn) for fn in Path(data_path).glob("*.csv")]
    if len(all_ds) == 0:
        raise Exception("No CCN data found in `{}`".format(data_path))
    else:
        return xr.concat(all_ds, dim="time")
