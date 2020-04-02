from unittest.mock import patch
import tempfile
import os

import twinotter.plots.basic_flight_track
import twinotter.plots.vertical_profile
import twinotter.plots.heights_and_legs
import twinotter.quicklook


@patch('matplotlib.pyplot.savefig')
def test_basic_flight_path(mock_savefig):
    twinotter.plots.basic_flight_track.generate(flight_data_path="obs/flight330")
    mock_savefig.assert_called_once()

@patch('matplotlib.pyplot.show')
def test_vertical_profile_plot(mock_showfig):
    twinotter.plots.vertical_profile.main(flight_data_path="obs/flight330")
    mock_showfig.assert_called_once()


LEGS_FILE_FLIGHT330 = """
,Label,Start,End
0,Leg,11:34:19,11:45:53
1,Leg,12:28:16,12:42:38
2,Leg,12:47:53,12:54:11
3,Leg,12:56:39,13:06:48
4,Leg,13:17:19,13:31:20
5,Leg,13:47:48,13:56:54
6,Profile,11:45:53,11:50:05
7,Profile,12:18:49,12:28:37
8,Profile,13:08:33,13:12:25
9,Profile,13:43:35,13:47:48
10,Profile,13:36:56,13:44:17
11,Profile,13:05:45,13:09:15
"""

@patch('matplotlib.pyplot.savefig')
def test_heights_and_legs_plot(mock_savefig):
    # "leg"-files are created interactively, so we just add the content for one
    # here and write that to a temporary file
    fh = tempfile.NamedTemporaryFile(delete=False, mode="w")
    try:
        fh.write(LEGS_FILE_FLIGHT330)
        fh.close()

        twinotter.plots.heights_and_legs.generate(
            flight_data_path="obs/flight330",
            legs_file=fh.name
        )
        mock_savefig.assert_called_once()
    finally:
        os.unlink(fh.name)

@patch('matplotlib.pyplot.savefig')
def test_quicklook_plot(mock_savefig):
    # "leg"-files are created interactively, so we just add the content for one
    # here and write that to a temporary file
    fh = tempfile.NamedTemporaryFile(delete=False, mode="w")
    try:
        fh.write(LEGS_FILE_FLIGHT330)
        fh.close()

        twinotter.quicklook.generate(
            flight_data_path="obs/flight330",
            legs_file=fh.name
        )
        mock_savefig.assert_called_with()
    finally:
        os.unlink(fh.name)


# this doesn't run properly because of the gui needing to be opened
# @patch('matplotlib.pyplot.show')
# def test_interactive_flight_path(mock_show):
    # twinotter.plots.interactive_flight_track.start_gui(flight_data_path="obs/flight330")
    # mock_show.assert_called_once()
