from sklearn.metrics import mean_absolute_error
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


def main():
    """
        function to calculate the MAE for all appliances, users, and total
    """
    data = pd.read_csv("results/data/real_data.csv")
    PE_data = pd.read_csv("results/data/PowerEye_data.csv")
    data = fix_index(data)
    PE_data = fix_index(PE_data)

    maes = {}
    for name in data.columns:
        maes[name] = mean_absolute_error(data[name], PE_data[name]).round(3)
    maes_series = pd.Series(maes)
    user_10 = maes_series[maes_series.index.str.endswith("10")].mean().round(3)
    user_20 = maes_series[maes_series.index.str.endswith("20")].mean().round(3)
    user_30 = maes_series[maes_series.index.str.endswith("30")].mean().round(3)

    total = maes_series.mean().round(3)
    print(f"total MAE: {total}")
    print(f"user1: Ayat MAE: {user_10}")
    print(f"user2: Qater Alnada MAE: {user_20}")
    print(f"user3: Ward MAE: {user_30}")
    print("all appliances MAEs")
    print(maes_series)


main()
