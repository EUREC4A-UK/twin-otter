from unittest.mock import patch

import twinotter.plots.basic_flight_track
import twinotter.plots.vertical_profile


@patch('matplotlib.pyplot.savefig')
def test_basic_flight_path(mock_savefig):
    twinotter.plots.basic_flight_track.generate(flight_data_path="obs/flight330")
    mock_savefig.assert_called_once()

@patch('matplotlib.pyplot.show')
def test_vertical_profile_plot(mock_showfig):
    twinotter.plots.vertical_profile.main(flight_data_path="obs/flight330")
    mock_showfig.assert_called_once()

# this doesn't run properly because of the gui needing to be opened
# @patch('matplotlib.pyplot.show')
# def test_interactive_flight_path(mock_show):
    # twinotter.plots.interactive_flight_track.start_gui(flight_data_path="obs/flight330")
    # mock_show.assert_called_once()
