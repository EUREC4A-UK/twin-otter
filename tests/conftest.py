from pathlib import Path
import tarfile
import tempfile
import shutil

import requests
import pytest

TESTDATA_URL = "http://gws-access.ceda.ac.uk/public/eurec4auk/testdata/twinotter.testdata.tar.gz"

# A testdata folder in this directory
testdata_dir = Path(__file__).parent / "testdata"


def download_testdata():
    fhtar = tempfile.NamedTemporaryFile(
        delete=False, suffix='.tar.gz'
    )

    r = requests.get(TESTDATA_URL)
    fhtar.write(r.content)
    fhtar.close()

    tarfile.open(fhtar.name, 'r:gz').extractall(testdata_dir)

    return


@pytest.fixture
def testdata(scope="session"):
    # Download testdata if it is not there yet
    if not testdata_dir.exists():
        download_testdata()

    # Copy data to a temporary directory
    tempdir = tempfile.TemporaryDirectory()
    p_root = Path(tempdir.name)
    shutil.copytree(testdata_dir / "obs", p_root / "obs")

    yield dict(
        path=str(p_root/"obs"),
        flight_data_path=str(p_root/"obs"/"flight330"),
        flight_legs_data_path=str(p_root/"obs"/"flight330"/"flight330-legs.csv"),
    )


@pytest.fixture
def testdata_empty(scope="session"):
    tempdir = tempfile.TemporaryDirectory()
    p_root = Path(tempdir.name)

    return dict(flight_data_path=str(p_root))
