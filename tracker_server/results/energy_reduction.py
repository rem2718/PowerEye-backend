import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def fix_index(df):
    """
    Fixes the index of the DataFrame by converting the 'date' column to datetime format, sorting the DataFrame based on the 'date', and setting the 'date' column as the new index.
    Args:
        df (pd.DataFrame): The DataFrame to be processed.
    Returns:
        pd.DataFrame: The DataFrame with the corrected index.
    """
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(by=["date"])
    df = df.set_index("date")
    return df


def plot_data(before, after, names):
    """
    Plot two bar charts for each user, comparing energy consumption before and after the experiment.

    Args:
        before: data before experiment
        after: data after experiment
        name: user name.
    """
    num_appliances = len(before.index)
    positions = np.arange(num_appliances)
    width = 0.35
    plt.bar(
        positions - width / 2,
        before,
        width=width,
        label="Before",
        color="r",
    )
    plt.bar(
        positions + width,
        after,
        width=width,
        label="After Experiment",
        color="b",
    )
    plt.xticks(positions, after.index)
    plt.legend()
    plt.grid(True)
    plt.title(f"Before vs After Experiment - {names} User")
    plt.xlabel("Appliance")
    plt.ylabel("Energy Consumption (kWh)")
    plt.show()


def main():
    """
    function to calculate the energy reduction for each user
    """
    data = pd.read_csv("results/data/experiment_energy.csv")
    data = fix_index(data)

    suffixes = ["10", "20", "30"]
    names = ["Ayat", "Qater", "Ward"]

    for i in range(len(names)):
        total = data.filter(like=suffixes[i]).sum(axis=1)
        print(f"total energy for {names[i]} User")
        print(total)

    for i in range(len(names)):
        before_data = data.filter(like=suffixes[i]).iloc[0]
        after_data = data.filter(like=suffixes[i]).iloc[1]
        plot_data(before_data, after_data, names[i])


main()
