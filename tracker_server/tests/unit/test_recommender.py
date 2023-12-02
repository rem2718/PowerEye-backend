import pytest
import pickle

from sklearn.cluster import KMeans
from xgboost import XGBRegressor
import pandas as pd
import numpy as np

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
    appliance = pd.read_csv(
        "tests/unit/64d154d494895e0b4c1bc081.csv", parse_dates=["timestamp"]
    )
    appliance["timestamp"] = appliance["timestamp"].apply(
        lambda x: x.replace(second=0, microsecond=0)
    )
    appliance = appliance.sort_values(by="timestamp")
    appliance = appliance.set_index("timestamp")
    return appliance["charger_20"]


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
    res = EPR.check_peak(
        cur_hour, status, e_type, [EType.PHANTOM.value, EType.SHIFTABLE.value]
    )
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


def test_check_baseline(appliance):
    res = EPR.check_baseline(0.06, appliance, {"cols": [], "nr_maes": (3, 0.2)})
    assert res == False


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


def test_fill_na(appliance):
    app = EPR._fill_na(appliance)
    assert not app.isnull().sum()


def test_normalize(appliance):
    app = EPR._fill_na(appliance)
    res = EPR._normalize(app)
    assert res.shape == app.shape


def test_feature_engineering(appliance):
    app = appliance.copy()
    app = EPR._fill_na(app)
    app = EPR._normalize(app)
    app = pd.DataFrame(app)
    app = app.dropna()
    app = app.reset_index()
    app.columns = ["timestamp", "energy"]
    app = EPR._feature_engineering(app)
    cols = [
        "hour",
        "month",
        "year",
        "quarter",
        "day_of_week",
        "day_of_month",
        "day_of_year",
        "week_of_year",
        "is_weekend",
        "is_night",
        "rolling_avg",
        "rolling_std",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_4",
        "lag_5",
        "lag_6",
        "lag_7",
    ]
    assert all(col in app.columns for col in cols)


def test_preprocessing(appliance):
    app = EPR._preprocessing(appliance)
    assert app["energy"].isnull().sum() == 0


def test_get_energy(appliance):
    app = EPR._get_energy(appliance)
    assert pd.api.types.is_numeric_dtype(app.dtype)


def test_split(appliance):
    app = EPR._preprocessing(appliance)
    X, y, X_train_val, y_train_val = EPR._split(app)
    assert X.shape[0] == app.shape[0]
    assert X.shape[1] + 2 == app.shape[1]
    assert y.shape[0] == app.shape[0]
    assert X_train_val.shape[0] == X.shape[0] - int(X.shape[0] * 0.1)
    assert y_train_val.shape[0] == X.shape[0] - int(X.shape[0] * 0.1)


def test_tscv(appliance):
    app = EPR._preprocessing(appliance)
    X, y, _, _ = EPR._split(app)
    pred, model = EPR._tscv(X, y, 2, {})
    assert len(pred) == 2
    assert isinstance(model, XGBRegressor)


def test_tune():
    pass


def test_all_tune(appliance):
    app = EPR._preprocessing(appliance)
    app = app.iloc[:11]
    X, y, X_train_val, y_train_val = EPR._split(app)
    fixed_params = EPR._all_tune(X, X_train_val, y_train_val)
    cols = [
        "objective",
        "tree_method",
        "eval_metric",
        "verbosity",
        "seed",
        "eta",
        "max_depth",
        "min_child_weight",
        "gamma",
        "subsample",
        "colsample_bytree",
        "n_estimators",
        "cols",
    ]
    assert all(col in fixed_params for col in cols)


def test_model_test(appliance):
    app = EPR._preprocessing(appliance)
    app = app.iloc[:21]
    X, y, _, _ = EPR._split(app)
    passed, maes = EPR._model_test(X, y, {})
    assert passed 
    assert len(maes) == 3
    assert all(np.issubdtype(type(num), np.number) for num in maes)


def test_best_params(appliance):
    params, mae = EPR.best_params(appliance)
    cols = ["cols", "eta", "nr_maes"]
    assert all(col in params for col in cols)
    assert np.issubdtype(type(mae), np.number)
