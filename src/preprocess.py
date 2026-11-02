"""Clean raw records and build consecutive-record intervals + leakage-free features."""
import numpy as np, pandas as pd
from config import MAX_VALID_INTERVAL_S

def clean(df):
    df = df.copy()
    t = df["Time"].str.split(":", expand=True).astype(int)
    df["sec"] = t[0] * 3600 + t[1] * 60 + t[2]
    df["hour"] = df["sec"] // 3600
    df["bus"] = df["Number"].str.replace(r"\s+", "", regex=True)
    df["dir"] = (df["Route"] == "up").astype(int)
    n0 = len(df)
    df = df.drop_duplicates(["file", "bus", "Route", "Node", "Time"])
    return df, n0 - len(df)

def build_intervals(df):
    """One row per pair of consecutive records of the same bus/direction/day-file.
    Only pairs whose node index advances by exactly 1 and whose gap is 1..MAX seconds are modelling samples."""
    df = df.sort_values(["file", "bus", "Route", "row_in_file"]).reset_index(drop=True)
    keys = ["file", "bus", "Route"]
    g = df.groupby(keys, sort=False)
    df["prev_sec"], df["prev_node"] = g["sec"].shift(), g["Node"].shift()
    df["interval_s"] = df["sec"] - df["prev_sec"]
    df["node_step"] = df["Node"] - df["prev_node"]
    g = df.groupby(keys, sort=False)
    df["prev_interval_s"] = g["interval_s"].shift()          # previous observed interval, known at prediction time
    df["prev_step"] = g["node_step"].shift()
    newrun = (df["node_step"] != 1)
    df["run_id"] = newrun.groupby([df[k] for k in keys]).cumsum()
    df["pos_in_run"] = df.groupby(keys + ["run_id"]).cumcount()
    ok = (df["node_step"] == 1) & (df["interval_s"] > 0) & (df["interval_s"] <= MAX_VALID_INTERVAL_S)
    pair = df[ok].copy()
    good_prev = (pair.prev_step == 1) & (pair.prev_interval_s > 0) & (pair.prev_interval_s <= MAX_VALID_INTERVAL_S)
    pair.loc[~good_prev, "prev_interval_s"] = np.nan
    pair["target_min"] = pair["interval_s"] / 60.0
    pair["from_node"] = pair["prev_node"].astype(int)
    pair["to_node"] = pair["Node"].astype(int)
    pair["group_id"] = pair["group"].astype(int)
    pair["month_idx"] = pair["month"].str.extract(r"(\d+)")[0].astype(int)
    pair["hour_sin"] = np.sin(2 * np.pi * pair["sec"] / 86400)
    pair["hour_cos"] = np.cos(2 * np.pi * pair["sec"] / 86400)
    pair["is_peak"] = pair["hour"].isin([8, 9, 10, 17, 18, 19]).astype(int)
    return df, pair
