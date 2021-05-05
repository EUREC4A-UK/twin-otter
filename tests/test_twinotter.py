import pytest

import numpy as np
import pandas as pd

import twinotter


@pytest.mark.parametrize(
    "load_from,revision",
    [
        ("flight_data_path", "most_recent"),
        ("flight_data_path", 4),
        ("flight_data_file", "most_recent"),
    ],
)
def test_load_flight(testdata, load_from, revision):
    ds = twinotter.load_flight(flight_data_path=testdata[load_from], revision=revision)

    # Check that the dataset still contains the right number of variables
    assert len(ds) == 58

    # Check that the time period of the dataset is the same
    assert len(ds.Time == 9928)

    # Check that there are no NaNs left in the dataset
    # Awkward syntax because xarray.DataArray.any returns an array
    # Numpy now has it's own bool type so we have to use "==" rather than "is"
    # Using pd.isnull because np.isnan doesn't work on object arrays
    # - https://stackoverflow.com/a/36001191/8270394
    assert pd.isnull(ds.Time.values).any() == False

    return


def test_load_flight_empty_fails(testdata_empty):
    with pytest.raises(FileNotFoundError):
        twinotter.load_flight(flight_data_path=testdata_empty["flight_data_path"])
    return


def test_load_segments(testdata):
    flight_segments = twinotter.load_segments(testdata["flight_segments_file"])


def test_count_segments(testdata):
    flight_segments = twinotter.load_segments(testdata["flight_segments_file"])
    assert twinotter.count_segments(flight_segments, "level") == 10
    assert twinotter.count_segments(flight_segments, "profile") == 7


def test_extract_segments(testdata):
    ds = twinotter.load_flight(flight_data_path=testdata["flight_data_path"])
    flight_segments = twinotter.load_segments(testdata["flight_segments_file"])

    ds_segs = twinotter.extract_segments(ds, flight_segments, "level")
    assert len(ds_segs.Time) == 5684
