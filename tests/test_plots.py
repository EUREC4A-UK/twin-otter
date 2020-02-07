from unittest.mock import patch

import twinotter.plots.basic_flight_track
import twinotter.plots.interactive_flight_track


@patch('matplotlib.pyplot.savefig')
def test_basic_flight_path(mock_savefig):
    twinotter.plots.basic_flight_track.main(flight_data_path="obs/flight330")
    mock_savefig.assert_called_once()

@patch('matplotlib.pyplot.show')
def test_interactive_flight_path(mock_show):
    twinotter.plots.interactive_flight_track.main(flight_data_path="obs/flight330")
    mock_show.assert_called_once()
