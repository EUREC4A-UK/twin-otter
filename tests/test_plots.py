from unittest.mock import patch
import pytest
from pathlib import Path
import os

import matplotlib as mpl

import twinotter.plots.basic_flight_track
import twinotter.plots.vertical_profile
import twinotter.plots.heights_and_legs
import twinotter.plots.interactive_flight_track
import twinotter.quicklook

# Fix for CI tests of tk GUI
# https://stackoverflow.com/a/50089385/8270394
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')


@patch('matplotlib.pyplot.savefig')
def test_basic_flight_path(mock_savefig, testdata):
    twinotter.plots.basic_flight_track.generate(
        flight_data_path=testdata['flight_data_path']
    )
    mock_savefig.assert_called_once()

@patch('matplotlib.pyplot.show')
def test_vertical_profile_plot(mock_showfig, testdata):
    twinotter.plots.vertical_profile.main(
        flight_data_path=testdata['flight_data_path']
    )
    mock_showfig.assert_called_once()


@patch('matplotlib.pyplot.savefig')
def test_heights_and_legs_plot(mock_savefig, testdata):
    twinotter.plots.heights_and_legs.generate(
        flight_data_path=testdata['flight_data_path'],
        legs_file=testdata['flight_legs_data_path']
    )
    mock_savefig.assert_called_once()

@patch('matplotlib.pyplot.savefig')
def test_quicklook_plot(mock_savefig, testdata):
    twinotter.quicklook.generate(
        flight_data_path=testdata['flight_data_path'],
        legs_file=testdata['flight_legs_data_path']
    )

    with open(testdata['flight_legs_data_path']) as fh:
        file_content = fh.read()
        n_legs = len(file_content.split('Leg'))-1
        n_profiles = len(file_content.split('Profile'))-1

    figures_path = Path(testdata['flight_data_path'])/"figures"
    for n in range(n_legs):
        fn_fig = str(figures_path/"Leg{}_quicklook.png".format(n))
        mock_savefig.assert_any_call(fn_fig)

    for n in range(n_profiles):
        fn_fig = str(figures_path/"Profile{}_skewt.png".format(n))
        mock_savefig.assert_any_call(fn_fig)

@patch('tkinter.mainloop')
def test_interactive_flight_path(mock_mainloop, testdata):
    twinotter.plots.interactive_flight_track.start_gui(
        flight_data_path=testdata['flight_data_path'])
    mock_mainloop.assert_called_once()
