import pytest
from unittest.mock import patch

import datetime
import pytz

import twinotter
import twinotter.external.goes
import twinotter.external.goes.download_matching


def test_load_nc(testdata):
    ds = twinotter.external.goes.load_nc(
        path=testdata["goes_path"],
        time=testdata['goes_time'],
    )

    assert len(ds) == 93


@patch("worldview_dl.download_image")
def test_download_matching(mock_download_image, testdata):
    twinotter.external.goes.download_matching.get_images(testdata["flight_data_path"])

    mock_download_image.assert_any_call(
        fn="GOES-East_ABI_Band2_Red_Visible_1km_2020-01-24_11-10.tiff",
        time=datetime.datetime(2020, 1, 24, 11, 10, tzinfo=pytz.utc),
        bbox=[10., -60., 15., -50.],
        layers=["GOES-East_ABI_Band2_Red_Visible_1km", "Reference_Labels"],
        image_format="tiff",
        resolution=0.01,
    )

    mock_download_image.assert_any_call(
        fn="GOES-East_ABI_Band2_Red_Visible_1km_2020-01-24_14-00.tiff",
        time=datetime.datetime(2020, 1, 24, 14, tzinfo=pytz.utc),
        bbox=[10., -60., 15., -50.],
        layers=["GOES-East_ABI_Band2_Red_Visible_1km", "Reference_Labels"],
        image_format="tiff",
        resolution=0.01,
    )
