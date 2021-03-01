from pathlib import Path
import tarfile
import tempfile
import shutil
import datetime

import requests
import pytest

TESTDATA_URL = "http://gws-access.ceda.ac.uk/public/eurec4auk/testdata/twinotter.testdata.tar.gz"

GOES_TESTDATA_URL = (
    "https://observations.ipsl.fr/aeris/eurec4a-data/"
    "SATELLITES/GOES-E/2km_10min/2020/2020_01_24/"
    "clavrx_OR_ABI-L1b-RadF-M6C01_G16_s20200241400165_BARBADOS-2KM-FD.level2.nc"
)

# A testdata folder in this directory
testdata_dir = Path(__file__).parent / "testdata"
testdata_twinotter_dir = testdata_dir / "obs"
testdata_goes_dir = testdata_dir / "goes"


def download_testdata():
    fhtar = tempfile.NamedTemporaryFile(
        delete=False, suffix='.tar.gz'
    )

    r = requests.get(TESTDATA_URL)
    fhtar.write(r.content)
    fhtar.close()

    tarfile.open(fhtar.name, 'r:gz').extractall(testdata_dir)

    return


def download_goes_testdata():
    with requests.get(GOES_TESTDATA_URL, stream=True) as r:
        with open(testdata_goes_dir / GOES_TESTDATA_URL.split("/")[-1], 'wb') as f:
            shutil.copyfileobj(r.raw, f)


@pytest.fixture
def testdata(scope="session"):
    # Download testdata if it is not there yet
    if not testdata_twinotter_dir.exists():
        testdata_twinotter_dir.mkdir()
        download_testdata()

    if not testdata_goes_dir.exists():
        testdata_goes_dir.mkdir()
        download_goes_testdata()

    # Copy data to a temporary directory
    tempdir = tempfile.TemporaryDirectory()
    p_root = Path(tempdir.name)
    shutil.copytree(testdata_dir / "obs", p_root / "obs")
    shutil.copytree(testdata_dir / "goes", p_root / "goes")

    flight_data_path = p_root/"obs"/"flight330"

    # Create an duplicate older MASIN file (to be avoided in tests)
    (flight_data_path/"MASIN"/"core_masin_20200124_r001_flight330_1hz.nc").symlink_to(
        flight_data_path/"MASIN"/"core_masin_20200124_r004_flight330_1hz.nc")

    yield dict(
        path=str(p_root/"obs"),
        flight_data_path=str(flight_data_path),
        flight_data_file=str(flight_data_path / "MASIN" /
                             "core_masin_20200124_r004_flight330_1hz.nc"),
        flight_legs_data_path=str(testdata_dir /
                                  "../EUREC4A_TO_Flight-Segments_20200124a_0.1.yaml"),
        goes_path=str(p_root/"goes"),
        goes_time=datetime.datetime(
            year=2020,
            month=1,
            day=24,
            hour=14,
            minute=0,
        ),
    )


@pytest.fixture
def testdata_empty(scope="session"):
    tempdir = tempfile.TemporaryDirectory()
    p_root = Path(tempdir.name)

    return dict(flight_data_path=str(p_root))
