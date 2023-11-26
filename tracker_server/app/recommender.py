import math

from sklearn.metrics import mean_squared_error, silhouette_score, mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from xgboost import XGBRegressor
from mango import Tuner
import pandas as pd
import numpy as np


class Recommender:
    """
    A class for providing personalized recommendation based on the user appliances power usage.
    """

    CLUSTER_THRESHOLD = 1000
    SILHOUETTE_THRESHOLD = 0.5
    HOUR_THRESHOLD = 1 / 2 * 60
    ENERGY_THRESHOLD = 1000
    POWER_THRESHOLD = ENERGY_THRESHOLD * 60
    NR_MAE_THRESHOLD = 0.75
    MSE_THRESHOLD = 0.6
    PEAK_START = 13
    PEAK_END = 17

    @staticmethod
    def check_goal(month_enegry: float, goal: float):
        """
        Check if the monthly energy consumption meets a specified goal.
        Args:
            month_energy (float): The current month energy consumption.
            goal (float): The energy consumption goal.
        Returns:
            int: The percentage of goal achievement as an integer value (0-200).
        """
        percentage = month_enegry / goal
        if percentage > 2:
            percentage += 1
        rounded = math.floor(percentage * 4) / 4
        return int(rounded * 100) if rounded <= 2 else 0

    @staticmethod
    def check_peak(cur_hour, status, e_type, types):
        """
        Check if a shiftable device is on during peak time.
        Args:
            cur_hour (int): Current hour.
            status (boolean): The status (ON/OFF) of the device.
            e_type (int): The energy type of the device.
            types (list): A list of shiftable devices types.
        Returns:
            bool: True if the device is shiftable and on, False otherwise.
        """
        is_peak = Recommender.PEAK_START <= cur_hour < Recommender.PEAK_END
        return is_peak and status and e_type in types

    @staticmethod
    def check_phantom(model, power, status):
        """
        Check if a device is in phantom mode based on a machine learning model prediction.
        Args:
            model (sklearn.cluster.KMeans): The machine learning model (k-mean cluster) for prediction.
            power (float): The power consumption of the device.
            status (boolean): The status (ON/OFF) of the device.
        Returns:
            bool: True if the device is in phantom mode, False otherwise.
        """
        if model and status:
            predicted_labels = model.predict([[0], [power]])
            return predicted_labels[0] == predicted_labels[1]
        return False

    @staticmethod
    def check_baseline(mae, powers, params):
        """
        Check if the model's prediction deviates significantly from the actual value and if the normalized
        relative mean absolute error (NR_MAE) exceeds a predefined threshold.
        Args:
            mae (float): Mean Absolute Error (MAE) of the model.
            powers (pd.DataFrame): Input data containing timestamp and energy values.
            params (dict): Parameters used to configure the XGBoost model.
        Returns:
            bool: True if the model's prediction deviates significantly and NR_MAE exceeds the threshold, False otherwise.
        """
        app = Recommender._preprocessing(powers)
        if app is None:
            return False
        y = app["energy"].iloc[:-1]
        X = app.drop(columns=["timestamp", "energy"])
        X_test = pd.DataFrame(X.iloc[-1]).transpose()
        y_test = Recommender._get_energy(powers)
        X = X.iloc[:-1]
        max_nr_mae, min_nr_mae = params["nr_maes"]
        del params["nr_maes"]
        del params["cols"]
        model = XGBRegressor(**params)
        model.fit(X, y)
        pred = model.predict(X_test)
        nr_mae = abs(pred - y_test) / mae
        nr_mae = (nr_mae - min_nr_mae) / (max_nr_mae - min_nr_mae)
        return y_test > pred and nr_mae > Recommender.NR_MAE_THRESHOLD

    @staticmethod
    def cluster(appliance):
        """
        Cluster appliance data using the KMeans algorithm.
        Args:
            appliance (pd.Series): A pandas Series representing the appliance data.
        Returns:
            KMeans or False: If clustering is successful, returns the KMeans model. Otherwise, returns False.
        """
        appliance = appliance.dropna()
        if appliance.shape[0] < Recommender.CLUSTER_THRESHOLD:
            return False

        value_counts = appliance.value_counts()
        total_count = value_counts.sum()
        weights = value_counts / total_count

        appliance = appliance.drop_duplicates()
        if appliance.shape[0] < 2:
            return False
        X = appliance.values.reshape(-1, 1)

        kmeans = KMeans(n_clusters=2, n_init=10)
        kmeans.fit(X, sample_weight=weights)

        score = silhouette_score(X, kmeans.labels_)
        if score < Recommender.SILHOUETTE_THRESHOLD:
            return False

        return kmeans

    @staticmethod
    def _fill_na(app):
        """
        Fill missing values in appliance DataFrame and then tesample it hourly.
        Args:
            app (pd.DataFrame): The DataFrame containing powers consumption data.
        Returns:
            pd.DataFrame: The DataFrame after the processing.
        """
        app = app.ffill(limit=5)
        hourly_null_count = app.resample("H").apply(lambda x: x.isnull().sum())
        app = app.fillna(0)

        app = app.apply(lambda power: (power / 1000) * (1 / 60))
        app = app.resample("H").sum()
        last = app.index[-1]
        for hour, count in hourly_null_count.items():
            if hour == last:
                continue
            if count > Recommender.HOUR_THRESHOLD:
                app.loc[hour] = None
        app = app.ffill(limit=3)
        return app

    @staticmethod
    def _normalize(app):
        """
        Normalize the given time series data in the DataFrame `app`.
        Args:
            app (pd.Series): The time series data to be normalized.
        Returns:
            Tuple[pd.Series, StandardScaler]: A tuple containing the normalized time series data and the fitted StandardScaler.
        """
        test_size = int(app.shape[0] * 0.2)
        app_train = app.iloc[:-test_size]
        app_test = app.iloc[-test_size:]
        scaler = StandardScaler()
        train_df = app_train.to_frame()
        test_df = app_test.to_frame()
        train_df = scaler.fit_transform(train_df)
        test_df = scaler.transform(test_df)
        app_train = pd.Series(train_df.flatten(), index=app_train.index)
        app_test = pd.Series(test_df.flatten(), index=app_test.index)
        app = pd.concat([app_train, app_test], axis=0)
        return app

    @staticmethod
    def _feature_engineering(df):
        """
        Perform feature engineering on the given DataFrame `df`.
        Args:
            df (pd.DataFrame): The DataFrame containing the timestamp and energy data.
        Returns:
            pd.DataFrame: The DataFrame with additional engineered features.
        """
        df["hour"] = df["timestamp"].dt.hour
        df["month"] = df["timestamp"].dt.month
        df["year"] = df["timestamp"].dt.year
        df["quarter"] = df["timestamp"].dt.quarter
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["day_of_month"] = df["timestamp"].dt.day
        df["day_of_year"] = df["timestamp"].dt.dayofyear
        df["week_of_year"] = df["timestamp"].dt.isocalendar().week
        df["week_of_year"] = df["week_of_year"].astype("int32")
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        df["is_night"] = df["hour"].apply(
            lambda hour: 1 if 0 <= hour < 6 or 18 <= hour <= 23 else 0
        )
        df["rolling_avg"] = df["energy"].rolling(window=24).mean()
        df["rolling_std"] = df["energy"].rolling(window=24).std()
        for i in range(1, 8):
            df[f"lag_{i}"] = df["energy"].shift(i)
        return df

    @staticmethod
    def _preprocessing(powers):
        """
        Perform preprocessing on the given power consumption data.
        Args:
            powers (pd.DataFrame): The DataFrame containing timestamp and power consumption data.
        Returns:
            Tuple[pd.DataFrame, StandardScaler]: A tuple containing the preprocessed DataFrame with engineered features
            and the fitted StandardScaler.
        """
        app = powers.copy()
        if app.shape[0] < Recommender.POWER_THRESHOLD:
            return None, None
        app = Recommender._fill_na(app)
        if app.shape[0] < Recommender.ENERGY_THRESHOLD:
            return None, None
        app = Recommender._normalize(app)
        app = pd.DataFrame(app)
        app = app.dropna()
        app = app.reset_index()
        app.columns = ["timestamp", "energy"]
        app = Recommender._feature_engineering(app)
        return app

    @staticmethod
    def _get_energy(powers):
        """
        Extract the energy consumption at the latest timestamp from the given power consumption data.
        Args:
            powers (pd.DataFrame): The DataFrame containing timestamp and power consumption data.
        Returns:
            float: The energy consumption at the latest timestamp.
        """
        app = powers.ffill(limit=5)
        app = app.fillna(0)
        app = app.apply(lambda power: (power / 1000) * (1 / 60))
        app = app.resample("H").sum()
        return app.iloc[-1]

    @staticmethod
    def _split(df):
        """
        Extract the energy consumption at the latest timestamp from the given power consumption data.
        Args:
            powers (pd.DataFrame): The DataFrame containing timestamp and power consumption data.
        Returns:
            float: The energy consumption at the latest timestamp.
        """
        y = df["energy"]
        X = df.drop(columns=["timestamp", "energy"])
        test_size = int(X.shape[0] * 0.1)
        X_train_val = X.iloc[:-test_size]
        y_train_val = y.iloc[:-test_size]
        return X, y, X_train_val, y_train_val

    @staticmethod
    def _tscv(X, y, n_splits, params):
        """
        Extract the energy consumption at the latest timestamp from the given power consumption data.
        Args:
            powers (pd.DataFrame): The DataFrame containing timestamp and power consumption data.
        Returns:
            float: The energy consumption at the latest timestamp.
        """
        cv = TimeSeriesSplit(n_splits=n_splits, test_size=1)
        preds = []
        for train_index, val_index in cv.split(X):
            X_train = X.iloc[train_index]
            y_train = y.iloc[train_index]
            X_val = X.iloc[val_index]
            model = XGBRegressor(**params)
            model.fit(X_train, y_train)
            pred = model.predict(X_val)
            preds.append(pred[0])
        return preds, model

    @staticmethod
    def _tune(X, y, test_size, fixed_params, param_space, num_iteration):
        """
        Tune the XGBoost model using Bayesian optimization.
        Parameters:
            X (pd.DataFrame): Features.
            y (pd.Series): Target variable.
            test_size (int): Size of the validation set.
            fixed_params (dict): Fixed parameters for the XGBoost model.
            param_space (dict): Search space for the hyperparameters.
            num_iteration (int): Number of iterations for Bayesian optimization.
        Returns:
            dict: The best hyperparameters found during tuning.
        """
        conf_Dict = {"num_iteration": num_iteration}

        def objective(args_list):
            results = []
            params_evaluated = []

            for params in args_list:
                try:
                    params_t = params.copy()
                    params_t.update(fixed_params)
                    pred, _ = Recommender._tscv(X, y, test_size, params)
                    y_val = y[-test_size:]
                    pred = pd.Series(pred, index=y_val.index)
                    mse = mean_squared_error(y_val, pred)
                    params_evaluated.append(params)
                    results.append(mse)
                except:
                    params_evaluated.append(params)
                    results.append(1e5)
            return params_evaluated, results

        tuner = Tuner(param_space, objective, conf_Dict)
        results = tuner.minimize()
        print("best parameters:", results["best_params"])
        print("best loss:", results["best_objective"])
        return results["best_params"]

    @staticmethod
    def _all_tune(X, X_train_val, y_train_val):
        """
        Tune multiple hyperparameters of an XGBoost model using a series of Bayesian optimization steps.

        Args:
            X (pd.DataFrame): Features for the entire dataset.
            X_train_val (pd.DataFrame): Features for the training and validation sets.
            y_train_val (pd.Series): Target variable for the training and validation sets.

        Returns:
            Dict: The tuned hyperparameters for the XGBoost model.
        """
        fixed_params = {
            "objective": "reg:squarederror",
            "tree_method": "hist",
            "eval_metric": "rmse",
            "verbosity": 0,
            "seed": 21,
        }
        model = XGBRegressor(**fixed_params)
        model.fit(X_train_val, y_train_val)
        feature_importance_scores = model.feature_importances_
        sorted_feature_indices = feature_importance_scores.argsort()[::-1]
        cols = X.columns[sorted_feature_indices[:15]]
        X = X[cols]
        X_train_val = X_train_val[cols]

        val_size = 10
        fixed_params["eta"] = 0.1
        fixed_params["max_depth"] = 5
        fixed_params["min_child_weight"] = 1
        fixed_params["gamma"] = 0
        fixed_params["subsample"] = 0.8
        fixed_params["colsample_bytree"] = 0.8
        param_space = {"n_estimators": range(50, 200, 2)}
        best = Recommender._tune(
            X_train_val, y_train_val, val_size, fixed_params, param_space, 30
        )

        fixed_params["n_estimators"] = best["n_estimators"]
        del fixed_params["max_depth"]
        del fixed_params["min_child_weight"]
        param_space = {
            "max_depth": range(3, 10),
            "min_child_weight": range(1, 6),
        }
        best = Recommender._tune(
            X_train_val, y_train_val, val_size, fixed_params, param_space, 30
        )

        fixed_params["max_depth"] = best["max_depth"]
        fixed_params["min_child_weight"] = best["min_child_weight"]
        del fixed_params["gamma"]
        param_space = {"gamma": [0, 0.1, 0.2, 0.3, 0.4, 0.5]}
        best = Recommender._tune(
            X_train_val, y_train_val, val_size, fixed_params, param_space, 15
        )

        fixed_params["gamma"] = best["gamma"]
        del fixed_params["subsample"]
        del fixed_params["colsample_bytree"]
        param_space = {
            "subsample": [i / 10.0 for i in range(5, 10)],
            "colsample_bytree": [i / 10.0 for i in range(5, 10)],
        }
        best = Recommender._tune(
            X_train_val, y_train_val, val_size, fixed_params, param_space, 30
        )

        fixed_params["subsample"] = best["subsample"]
        fixed_params["colsample_bytree"] = best["colsample_bytree"]
        del fixed_params["eta"]
        param_space = {"eta": [0.01, 0.05, 0.1, 0.2, 0.3]}
        best = Recommender._tune(
            X_train_val, y_train_val, val_size, fixed_params, param_space, 15
        )

        fixed_params["eta"] = best["eta"]
        fixed_params["cols"] = cols
        return fixed_params

    def _model_test(X, y, params):
        """
        Test the XGBoost model on a time series cross-validation dataset and calculate evaluation metrics.
        Args:
            X (DataFrame): Features DataFrame for training.
            y (Series): Target Series for training.
            params (dict): Hyperparameters for the XGBoost model.
        Returns:
            Tuple: A tuple containing a boolean indicating whether the model passed the test, and a tuple of
            evaluation metrics (MAE, max normalized MAE, min normalized MAE).
        """
        test_size = int(X.shape[0] * 0.1)
        pred_series, _ = Recommender._tscv(X, y, test_size, params)
        test_series = y[-test_size:]
        pred_series = pd.Series(pred_series, index=test_series.index)
        mse = mean_squared_error(test_series, pred_series)
        mae = mean_absolute_error(pred_series, test_series)
        nr_mae = abs(pred_series - test_series) / mae
        max_nr_mae = np.max(nr_mae)
        min_nr_mae = np.min(nr_mae)
        maes = (mae, max_nr_mae, min_nr_mae)
        passed = mse < Recommender.MSE_THRESHOLD
        return passed, maes

    @staticmethod
    def best_params(powers):
        """
        Find the best hyperparameters for the XGBoost model based on the given power data.
        Args:
            powers (DataFrame): A DataFrame containing power consumption data with a 'timestamp' column.
        Returns:
            Tuple: A tuple containing the best hyperparameters and the corresponding mean absolute error (MAE).
            If the model testing fails, returns (None, None).
        """
        app = Recommender._preprocessing(powers)
        if app is None:
            return None, None
        X, y, X_train_val, y_train_val = Recommender._split(app)
        params = Recommender._all_tune(X, X_train_val, y_train_val)
        cols = params.pop("cols", None)
        passed, maes = Recommender._model_test(X, y, params)
        if passed:
            mae, max_nr_mae, min_nr_mae = maes
            params["nr_maes"] = (max_nr_mae, min_nr_mae)
            params["cols"] = cols
            return params, mae
        else:
            return None, None
