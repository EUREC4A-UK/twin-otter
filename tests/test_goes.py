import pytest

import twinotter.external.goes


def test_load_nc(testdata):
    ds = twinotter.external.goes.load_nc(
        path=testdata["goes_path"], time=testdata["goes_time"],
    )

    assert len(ds) == 93
