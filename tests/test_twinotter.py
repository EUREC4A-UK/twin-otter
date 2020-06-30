import pytest

import numpy as np

import twinotter


@pytest.mark.parametrize("load_from,revision", [
    ("flight_data_path", "most_recent"),
    ("flight_data_path", 4),
    ("flight_data_file", "most_recent"),
])
def test_load_flight(testdata, load_from, revision):
    ds = twinotter.load_flight(flight_data_path=testdata[load_from], revision=revision)

    # Check that the dataset still contains the right number of variables
    assert len(ds) == 58

    # Check that the time period of the dataset is the same
    assert len(ds.Time == 9928)

    # Check that there are no NaNs left in the dataset
    # Awkward syntax because xarray.DataArray.any returns an array
    assert False in np.isnan(ds.Time).any()

    return


def test_load_flight_empty_fails(testdata_empty):
    with pytest.raises(FileNotFoundError):
        twinotter.load_flight(
            flight_data_path=testdata_empty["flight_data_path"]
        )
    return
