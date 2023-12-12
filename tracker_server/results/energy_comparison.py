from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import pandas as pd


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


def plot_data(real_data_list, pe_data_list, names):
    """
    it plots 3 lineplots one for each user, real data vs PowerEye data
    Args:
        real_data_list: the data we collected form smart plugs cloud
        pe_data_list: the data we collected using PowerEye Tracker Server
    """
    num_users = len(names)
    fig, axes = plt.subplots(num_users, 1, figsize=(12, 8 * num_users), sharex=True)

    for i in range(num_users):
        axes[i].plot(
            real_data_list[i],
            label=f"Real Data",
            marker="o",
            color="r",
            linestyle="--",
            alpha=0.7,
        )
        axes[i].plot(
            pe_data_list[i],
            label=f"PowerEye Data",
            marker="o",
            color="b",
        )

        axes[i].set_title(f"Real Data vs PowerEye Data - {names[i]} User")
        axes[i].legend()
        axes[i].grid(True)

    axes[1].set_ylabel("Energy Consumption (kWh)")
    axes[-1].set_xlabel("Date")

    plt.show()


def main():
    """
    function to calculate the MAE for all appliances, users, and total
    """
    data = pd.read_csv("results/data/real_data.csv")
    pe_data = pd.read_csv("results/data/PowerEye_data.csv")
    data = fix_index(data)
    pe_data = fix_index(pe_data)

    maes = {}
    suffixes = ["10", "20", "30"]
    names = ["Ayat", "Qater", "Ward"]

    for name in data.columns:
        maes[name] = mean_absolute_error(data[name], pe_data[name]).round(3)

    maes_series = pd.Series(maes)
    total = maes_series.mean().round(3)
    print(f"total MAE: {total}")

    for i in range(len(names)):
        mae = maes_series[maes_series.index.str.endswith(suffixes[i])].mean().round(3)
        print(f"user{i+1}: {names[i]} MAE: {mae}")

    print("all appliances MAEs")
    print(maes_series)

    user_data_list, user_pe_data_list = [], []
    for suffix in suffixes:
        user_data = data.filter(like=suffix).sum(axis=1)
        user_pe_data = pe_data.filter(like=suffix).sum(axis=1)
        user_data_list.append(user_data)
        user_pe_data_list.append(user_pe_data)

    plot_data(user_data_list, user_pe_data_list, names)


main()
