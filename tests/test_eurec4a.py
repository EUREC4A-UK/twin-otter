import pytest

import twinotter.external.eurec4a


@pytest.mark.parametrize(
    "platform,flight_number,flight_id",
    [
        ("TO", 330, "TO-0330"),
        ("HALO", 119, "HALO-0119"),
        ("P3", 117, "P3-0117"),
    ],
)
def test_load_segments(platform, flight_number, flight_id):
    flight_segments = twinotter.external.eurec4a.load_segments(
        flight_number, platform=platform
    )
    assert flight_segments["flight_id"] == flight_id
