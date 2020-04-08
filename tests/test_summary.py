import pytest
import pathlib

import twinotter.summary


def test_summary(testdata):
    flight_summary_path = pathlib.Path(testdata["path"])/"test.csv"

    twinotter.summary.generate(
        flight_data_path=testdata["flight_data_path"],
        flight_summary_path=flight_summary_path
    )

    # Check the summary file has been produced
    assert flight_summary_path.is_file()

    return
