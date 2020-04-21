import datetime

import pytest

import twinotter.external.goes


def test_load_nc(testdata):
    ds = twinotter.external.goes.load_nc(
        path=testdata["goes_path"],
        time=datetime.datetime(
            year=2020,
            month=1,
            day=24,
            hour=14,
            minute=0,
        ),
    )
