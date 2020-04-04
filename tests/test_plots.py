from unittest.mock import patch
import pytest
import tempfile
import os
from pathlib import Path
import requests

import twinotter.plots.basic_flight_track
import twinotter.plots.vertical_profile
import twinotter.plots.heights_and_legs
import twinotter.quicklook

TESTDATA_URL = "http://homepages.see.leeds.ac.uk/~earlcd/eurec4a/testdata/twinotter.testdata.tar.gz"


def untar_data(url, fname, dest):
    "Download `url` to `fname` if `dest` doesn't exist, and un-tgz to folder `dest`."
    dest = url2path(url, data) if dest is None else Path(dest)/url2name(url)
    fname = Path(ifnone(fname, _url2tgz(url, data)))
    if force_download or (fname.exists() and url in _checks and _check_file(fname) != _checks[url]):
        print(f"A new version of the {'dataset' if data else 'model'} is available.")
        if fname.exists(): os.remove(fname)
        if dest.exists(): shutil.rmtree(dest)
    if not dest.exists():
        fname = download_data(url, fname=fname, data=data)
        if url in _checks:
            assert _check_file(fname) == _checks[url], f"Downloaded file {fname} does not match checksum expected! Remove that file from {Config().data_archive_path()} and try your code again."
    return dest


class TestData():
    def __init__(self, url):
        self.url = url

    def __enter__(self):
        self.fhtar = tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix='.tar.gz'
        )
        r = requests.get(TESTDATA_URL)
        self.fhtar.write(r.content)
        self.fhtar.close()

        tarfile.open(fname, 'r:gz').extractall(dest.parent)

    def __exit__(self):
        os.unlink(fhtar.name)

    @property
    def path(self):
        return self.fh.name

@pytest.fixture
def testdata_single_flight(scope="module"):
    # "leg"-files are created interactively, so we just add the content for one
    # here and write that to a temporary file
    fh = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix='.tar.gz')
    try:
        r = requests.get(TESTDATA_URL)
        fh.write(r.content)
        fh.close()

        twinotter.plots.heights_and_legs.generate(
            flight_data_path="obs/flight330",
            legs_file=fh.name
        )
        mock_savefig.assert_called_once()
    finally:
        os.unlink(fh.name)




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
        n_legs = len(LEGS_FILE_FLIGHT330.split('Leg'))-1
        for n in range(n_legs):
            fn_fig = "flight{}/Leg{}_quicklook.png".format(330, n)
            mock_savefig.assert_any_call(fn_fig)

        n_profiles = len(LEGS_FILE_FLIGHT330.split('Profile'))-1
        for n in range(n_profiles):
            fn_fig = "flight{}/Profile{}_skewt.png".format(330, n)
            mock_savefig.assert_any_call(fn_fig)
    finally:
        os.unlink(fh.name)


# this doesn't run properly because of the gui needing to be opened
# @patch('matplotlib.pyplot.show')
# def test_interactive_flight_path(mock_show):
    # twinotter.plots.interactive_flight_track.start_gui(flight_data_path="obs/flight330")
    # mock_show.assert_called_once()
