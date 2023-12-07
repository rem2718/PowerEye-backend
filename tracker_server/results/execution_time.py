from datetime import datetime
import pickle
import random
import time
import sys

sys.path.append("D:\\PowerEye-backend\\tracker_server")

import matplotlib.pyplot as plt
import pandas as pd

from app.recommender import Recommender as EPR
from app.types_classes import EType

shiftable = [EType.SHIFTABLE.value, EType.PHANTOM.value]


def get_model(type):
    """
    Load a pre-trained machine learning model from the specified type.
    Args:
        type (str): The type of the model to load.
    Returns:
        model: The pre-trained machine learning model loaded from the filesystem.
    """
    file_path = f"./models_filesystem/{type}_models/64d154bc94895e0b4c1bc080/64d165e693d44252699aa227.pkl"
    file = open(file_path, "rb")
    model = pickle.load(file)
    file.close()
    return model


def get_powers():
    """
    Reads power data from a CSV file, processes the timestamp column, sorts the DataFrame based on the timestamp,
    sets the timestamp column as the index, and returns a specific column 'office_strip_30' from the DataFrame.
    Returns:
        pd.Series: The power data for the 'office_strip_30' column with a timestamp index.
    """
    powers = pd.read_csv("results/data/64d154bc94895e0b4c1bc080.csv")
    powers["timestamp"] = pd.to_datetime(powers["timestamp"], errors="coerce")
    powers["timestamp"] = powers["timestamp"].apply(
        lambda x: x.replace(second=0, microsecond=0)
    )
    powers = powers.sort_values(by=["timestamp"])
    powers = powers.set_index("timestamp")
    return powers["office_strip_30"]


def modified_notify_goal(user, cur_energy):
    """
        modified version of Checker._notify_goal() without flags
    """
    goal = user["energy_goal"]
    if goal > 0:
        month_enegry = user["current_month_energy"] + cur_energy
        percentage = EPR.check_goal(month_enegry, goal)
        if percentage:
            # notify goal
            pass


def modified_notify_peak(app):
    """
        modified version of Checker._notify_peak() without flags
    """
    status = app["status"]
    e_type = app["e_type"]
    if EPR.check_peak(datetime.now().hour, status, e_type, shiftable):
        # notify peak
        pass


def modified_notify_phantom(app, power):
    """
        modified version of Checker._notify_phantom() without flags
    """
    status = app["status"]
    model = get_model("cluster")
    if model and EPR.check_phantom(model, power, status):
        # notify phantom
        pass


def modified_notify_baseline(app, powers):
    """
        modified version of Checker._notify_baseline() without flags
    """
    baseline = app["baseline_threshold"]
    if baseline > 0:
        params = get_model("forecast")
        if params and EPR.check_baseline(baseline, powers, params):
            # notify baseline
            pass


def modified_checker(user, appliances):
    """
        modified version of Checker.run() without all dependencies 
    """
    cur_energy = 0
    powers = get_powers()
    for app in appliances:
        cur_energy += app["energy"]
        modified_notify_peak(app)
        if app["e_type"] == EType.PHANTOM.value:
            modified_notify_phantom(app, app["power"])
        modified_notify_baseline(app, powers)
    modified_notify_goal(user, cur_energy)


def generate_rand_data():
    """
    Generates random data for a user and an appliance for testing or simulation purposes.
    Returns:
        tuple: A tuple containing a user dictionary and an appliance dictionary with randomly generated data.
    """
    user = {
        "energy_goal": random.uniform(0, 20),
        "current_month_energy": random.uniform(0, 20),
    }
    appliance = {
        "energy": random.uniform(0, 5),
        "e_type": random.choice(
            [EType.SHIFTABLE.value, EType.PHANTOM.value, EType.NONE.value]
        ),
        "baseline_threshold": random.uniform(0, 5),
        "status": random.choice([False, True]),
        "power": random.uniform(0, 200),
    }
    return user, appliance


def measure_time_execution(user, appliances):
    """
    Measures the execution time for the 'modified_checker'.
    Args:
        user (dict): A dictionary representing user data.
        appliances (list): A list of dictionaries, each representing appliance data.
    Returns:
        float: The time taken for the execution of the 'modified_checker' function in seconds.
    """
    start_time = time.time()
    modified_checker(user, appliances)
    end_time = time.time()
    return end_time - start_time


def main():
    """
        function to measure the excution time for Checker.run() across different values of N
    """
    appliances = []
    N = []
    times = []
    for n in range(1, 51):
        user, appliance = generate_rand_data()
        appliances.append(appliance)
        time = measure_time_execution(user, appliances)
        N.append(n)
        times.append(time)
    mid = int(len(N) / 2)
    print(f"min at {N[0]}: {times[0]} secs")
    print(f"mid at {N[mid]}: {times[mid]} secs")
    print(f"max at {N[-1]}: {times[-1]} secs")
    plt.plot(N, times, label="Line Plot")
    plt.xlabel("N")
    plt.ylabel("Execution Time(s)")
    plt.title("Checker.run() Exceution Time")
    plt.show()


main()
