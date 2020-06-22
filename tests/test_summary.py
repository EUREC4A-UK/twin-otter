import pytest
import pathlib
import tempfile

import twinotter.summary


def test_summary(testdata):
    flight_summary_path = pathlib.Path(tempfile.NamedTemporaryFile(suffix=".csv").name)

    twinotter.summary.generate(
        flight_data_path=testdata["flight_data_path"],
        flight_summary_path=flight_summary_path
    )

    # Check the summary file has been produced
    assert flight_summary_path.is_file()

    # Run again with the existing file
    twinotter.summary.generate(
        flight_data_path=testdata["flight_data_path"],
        flight_summary_path=flight_summary_path
    )

    return
