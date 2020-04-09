from pathlib import Path
import tarfile
import tempfile
import os

import requests
import pytest

import twinotter

TESTDATA_URL = "http://gws-access.ceda.ac.uk/public/eurec4auk/testdata/twinotter.testdata.tar.gz"


@pytest.fixture
def testdata(scope="session"):
    fhtar = tempfile.NamedTemporaryFile(
        delete=False, suffix='.tar.gz'
    )
    tempdir = tempfile.TemporaryDirectory()

    r = requests.get(TESTDATA_URL)
    fhtar.write(r.content)
    fhtar.close()

    p_root = Path(tempdir.name)
    tarfile.open(fhtar.name, 'r:gz').extractall(p_root)

    yield dict(
        path=str(p_root/"obs"),
        flight_data_path=str(p_root/"obs"/"flight330"),
        flight_legs_data_path=str(p_root/"obs"/"flight330"/"flight330-legs.csv"),
    )

    os.unlink(fhtar.name)


@pytest.fixture
def testdata_empty(scope="session"):
    tempdir = tempfile.TemporaryDirectory()
    p_root = Path(tempdir.name)

    return dict(flight_data_path=str(p_root))
