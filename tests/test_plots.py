from unittest.mock import patch
import pytest
from pathlib import Path

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

import twinotter.plots.basic_flight_track
import twinotter.plots.flight_track_frames
import twinotter.plots.vertical_profile
import twinotter.plots.heights_and_legs
import twinotter.quicklook
import twinotter.external.goes


@patch("matplotlib.pyplot.savefig")
def test_basic_flight_path(mock_savefig, testdata):
    twinotter.plots.basic_flight_track.generate(
        flight_data_path=testdata["flight_data_path"]
    )
    mock_savefig.assert_called_once()


def test_flight_track_frame(testdata):
    ds = twinotter.external.goes.load_nc(
        path=testdata["goes_path"], time=testdata["goes_time"],
    )
    fig, ax = twinotter.plots.flight_track_frames.make_frame(ds)

    plt.close(fig)


def test_overlay_flight_path_segment(testdata):
    twinotter.plots.flight_track_frames.overlay_flight_path_segment(
        ax=plt.axes(projection=ccrs.PlateCarree()),
        flight_data=twinotter.load_flight(testdata["flight_data_path"]),
        time=testdata["goes_time"],
    )

    plt.close()


@patch("matplotlib.pyplot.show")
def test_vertical_profile_plot(mock_showfig, testdata):
    twinotter.plots.vertical_profile.main(flight_data_path=testdata["flight_data_path"])
    mock_showfig.assert_called_once()


@patch("matplotlib.pyplot.savefig")
def test_heights_and_legs_plot(mock_savefig, testdata):
    twinotter.plots.heights_and_legs.generate(
        flight_data_path=testdata["flight_data_path"],
        flight_segments_file=testdata["flight_segments_file"],
    )
    mock_savefig.assert_called_once()


@patch("matplotlib.figure.Figure.savefig")
def test_quicklook_plot(mock_savefig, testdata):
    twinotter.quicklook.generate(
        flight_data_path=testdata["flight_data_path"],
        flight_segments_file=testdata["flight_segments_file"],
    )

    with open(testdata["flight_segments_file"]) as fh:
        file_content = fh.read()
        n_levels = len(file_content.split("level")) - 1
        n_profiles = len(file_content.split("profile")) - 1

        print(n_levels, n_profiles)

    for n in range(n_levels):
        fn_fig = "flight330_level{}_quicklook.png".format(n)
        mock_savefig.assert_any_call(fn_fig)

        fn_fig = "flight330_level{}_paluch.png".format(n)
        mock_savefig.assert_any_call(fn_fig)

    for n in range(n_profiles):
        fn_fig = "flight330_profile{}_skewt.png".format(n)
        mock_savefig.assert_any_call(fn_fig)


# this doesn't run properly because of the gui needing to be opened
# @patch('matplotlib.pyplot.show')
# def test_interactive_flight_path(mock_show):
# twinotter.plots.interactive_flight_track.start_gui(flight_data_path="obs/flight330")
# mock_show.assert_called_once()
