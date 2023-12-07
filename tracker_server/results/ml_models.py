from bson import ObjectId
import pickle
import sys
import os

sys.path.append("D:\\PowerEye-backend\\tracker_server")

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from dotenv import load_dotenv
import pandas as pd
import numpy as np

from app.external_dependencies.mongo import Mongo
from app.recommender import Recommender as EPR
from app.types_classes import EType

load_dotenv(os.path.join(".secrets", ".env"))

def get_powers(user_id, db):
    """
    Get power data for a specific user from the database.
    Args:
        user_id (str): The user ID.
        db: The database object.
    Returns:
        powers (pd.DataFrame): DataFrame containing power data with timestamp as the index.
    """
    query = {"user": ObjectId(user_id)}
    projection = {"user": 0, "_id": 0}
    data = db.get_docs("Powers", query, projection)
    data = list(data)
    if len(data):
        powers = pd.DataFrame(data)
        powers["timestamp"] = pd.to_datetime(powers["timestamp"], errors="coerce")
        powers["timestamp"] = powers["timestamp"].apply(
            lambda x: x.replace(second=0, microsecond=0)
        )
        powers = powers.sort_values(by=["timestamp"])
        powers = powers.set_index("timestamp")
        return powers

def get_params(user_id, app_id):
    """
    Get parameters for the forecasting model of a specific user and appliance.
    Args:
        user_id (str): The user ID.
        app_id (str): The appliance ID.
    Returns:
        params: Parameters for the forecasting model, or None if the file is not found.
    """
    try:
        file_path = f"./models_filesystem/forecast_models/{user_id}/{app_id}.pkl"
        file = open(file_path, "rb")
        params = pickle.load(file)
        file.close()
        return params
    except:
        return None
   
def get_silhouette(powers):
    """
    Calculate the Silhouette score for the clustering of power readings.
    Args:
        powers (pd.Series): A pandas Series containing power readings.
    Returns:
        score: The Silhouette score, or None if the data is insufficient or the score is below a threshold.
    """
    powers = powers.dropna()
    if powers.shape[0] < EPR.CLUSTER_THRESHOLD:
        return None
    value_counts = powers.value_counts()
    total_count = value_counts.sum()
    weights = value_counts / total_count
    powers = powers.drop_duplicates()
    if powers.shape[0] < 2:
        return None
    X = powers.values.reshape(-1, 1)
    kmeans = KMeans(n_clusters=2, n_init=10)
    kmeans.fit(X, sample_weight=weights)
    score = silhouette_score(X, kmeans.labels_)
    if score < EPR.SILHOUETTE_THRESHOLD:
        return None
    return score

def test_model(X, y, params):
    """
    Test a time-series forecasting model.
    Args:
        X (pd.DataFrame): Features for training the model.
        y (pd.Series): Target variable for training the model.
        params (_type_): Model parameters.
    Returns:
        Tuple: A tuple containing a boolean indicating whether the model passed the test,
               root mean squared error (RMSE), and mean absolute error (MAE).
    """
    test_size = int(X.shape[0] * 0.1)
    pred_series, _ = EPR._tscv(X, y, test_size, params)
    test_series = y[-test_size:]
    pred_series = pd.Series(pred_series, index=test_series.index)
    mse = mean_squared_error(test_series, pred_series)
    mae = mean_absolute_error(pred_series, test_series)
    rmse = np.sqrt(mse)
    passed = mse < EPR.MSE_THRESHOLD
    return passed, rmse, mae
    
def get_rmse_mae(powers, params):
    """
    Get root mean squared error (RMSE) and mean absolute error (MAE) for a given appliance.
    Args:
        powers (pd.DataFrame): Power consumption data for the appliance.
        params (dict): Model parameters.
    Returns:
        Tuple: A tuple containing RMSE and MAE if the model passes the test; otherwise, (None, None).
    """
    app = EPR._preprocessing(powers)
    if app is None:
        return None, None
    X, y, _, _ = EPR._split(app)
    cols = params.pop("cols", None)
    X = X[cols]
    passed, rmse, mae = test_model(X, y, params)
    if passed:
        return rmse, mae
    return None, None

def main():
    """
        function that calculate ML scores for the user appliances
    """
    URL = os.getenv("DB_URL")
    database_name = "hemsproject"
    ayat = '64d1548894895e0b4c1bc07f'
    qater = '64d154d494895e0b4c1bc081'
    ward = '64d154bc94895e0b4c1bc080'
    users = [ayat, qater, ward]
    db = Mongo(URL, database_name)
    
    for user in users:
        print(f'user {user} scores:')
        user_doc = db.get_doc('Users', {'_id': ObjectId(user)})
        powers = get_powers(user, db)
        appliances = user_doc['appliances']
        scores = []
        for app in appliances:
            app_id = str(app['_id'])
            params = get_params(user, app_id)
            row = {'name': app['name']}
            if app['e_type'] == EType.PHANTOM.value:
                row['silhouette'] = get_silhouette(powers[app_id])
            if params != None:
                rmse, mae = get_rmse_mae(powers[app_id], params)
                row['rmse'] = rmse
                row['mae'] = mae
            scores.append(row)
        print(pd.DataFrame(scores))
        
main()