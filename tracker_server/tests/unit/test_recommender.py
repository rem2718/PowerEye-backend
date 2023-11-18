import pytest
import pickle

from sklearn.cluster import KMeans
import pandas as pd

from app.recommender import Recommender as EPR
from app.types_classes import EType


@pytest.fixture(scope="module")
def model():
    file_path = "models_filesystem/cluster_models/64d154bc94895e0b4c1bc080/64d1682993d44252699aa22a.pkl"
    file = open(file_path, "rb")
    model = pickle.load(file)
    file.close()
    return model


@pytest.fixture(scope="module")
def appliance():
    appliance = pd.read_csv("tests/unit/64d154d494895e0b4c1bc081.csv")["charger_20"]
    return appliance


@pytest.mark.parametrize(
    ("month_enegry", "goal", "output"),
    (
        (0, 100, 0),
        (10, 100, 0),
        (25, 100, 25),
        (30, 100, 25),
        (50, 100, 50),
        (60, 100, 50),
        (75, 100, 75),
        (90, 100, 75),
        (100, 100, 100),
        (110, 100, 100),
        (125, 100, 125),
        (130, 100, 125),
        (150, 100, 150),
        (160, 100, 150),
        (175, 100, 175),
        (190, 100, 175),
        (200, 100, 200),
        (210, 100, 0),
    ),
)
def test_check_goal(month_enegry, goal, output):
    res = EPR.check_goal(month_enegry, goal)
    assert res == output


@pytest.mark.parametrize(
    ("cur_hour", "status", "e_type", "output"),
    (
        (12, False, 1, False),
        (12, False, 2, False),
        (12, False, 3, False),
        (12, True, 1, False),
        (12, True, 2, False),
        (12, True, 3, False),
        (13, False, 1, False),
        (13, False, 2, False),
        (13, False, 3, False),
        (13, True, 1, False),
        (13, True, 2, True),
        (13, True, 3, True),
        (14, False, 1, False),
        (14, False, 2, False),
        (14, False, 3, False),
        (14, True, 1, False),
        (14, True, 2, True),
        (14, True, 3, True),
        (17, False, 1, False),
        (17, False, 2, False),
        (17, False, 3, False),
        (17, True, 1, False),
        (17, True, 2, False),
        (17, True, 3, False),
        (19, False, 1, False),
        (19, False, 2, False),
        (19, False, 3, False),
        (19, True, 1, False),
        (19, True, 2, False),
        (19, True, 3, False),
    ),
)
def test_check_peak(cur_hour, status, e_type, output):
    res = EPR.check_peak(cur_hour, status, e_type, [EType.PHANTOM.value, EType.SHIFTABLE.value])
    assert res == output


@pytest.mark.parametrize(
    ("power", "status", "output"),
    (
        (0, True, True),
        (0.1, True, True),
        (1000, True, False),
        (0, False, False),
        (0.1, False, False),
        (1000, False, False),
    ),
)
def test_check_phantom(model, power, status, output):
    res = EPR.check_phantom(model, power, status)
    assert res == output
    res = EPR.check_phantom(False, power, status)
    assert res == False


@pytest.mark.parametrize(
    ("energy", "baseline", "output"),
    (
        (110, 100, True),
        (100, 100, False),
        (90, 100, False),
    ),
)
def test_check_baseline(energy, baseline, output):
    res = EPR.check_baseline(energy, baseline)
    assert res == output


@pytest.mark.parametrize(
    ("size", "output"),
    (
        (500, False),
        (20000, True),
    ),
)
def test_cluster(appliance, size, output):
    appliance = appliance.head(size)
    res = EPR.cluster(appliance)
    if output:
        assert isinstance(res, KMeans)
    else:
        assert res == output
