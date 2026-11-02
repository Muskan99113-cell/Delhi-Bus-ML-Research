"""Exploratory data analysis: writes dataset_profile.csv and the EDA figures."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import FIG, TAB, MAX_VALID_INTERVAL_S
from plotstyle import setup, save
setup()

def profile(raw, clean_df, n_dup, full, pair):
    adj = full.node_step == 1
    p = {
        "workbooks_read": raw["file"].nunique(), "raw_records": len(raw), "records_after_dedup": len(clean_df),
        "duplicate_records_removed": n_dup, "missing_cells": int(raw[["Node", "Number", "Route", "Time"]].isna().sum().sum()),
        "distinct_bus_ids": clean_df["bus"].nunique(), "distinct_node_codes": clean_df["Node"].nunique(),
        "route_directions": ", ".join(sorted(clean_df["Route"].unique())), "route_group_folders": ", ".join(sorted(raw["group"].unique())),
        "months": ", ".join(sorted(raw["month"].unique())), "min_sec_of_day": int(clean_df.sec.min()),
        "max_sec_of_day": int(clean_df.sec.max()), "adjacent_node_pairs_total": int(adj.sum()),
        "pairs_non_positive_interval": int((adj & (full.interval_s <= 0)).sum()),
        "pairs_over_max_interval": int((adj & (full.interval_s > MAX_VALID_INTERVAL_S)).sum()),
        "modelling_samples": len(pair), "target_mean_min": round(pair.target_min.mean(), 3),
        "target_median_min": round(pair.target_min.median(), 3), "target_std_min": round(pair.target_min.std(), 3),
    }
    pd.Series(p, name="value").to_csv(TAB / "dataset_profile.csv", header=True)
    return p

def figures(raw, clean_df, full, pair):
    m = raw.groupby(["month", "group"]).size().unstack()
    ax = m.plot(kind="bar", figsize=(5, 3.4), color=["#1f3a68", "#c0392b"], rot=0)
    ax.set_xlabel("Data folder"); ax.set_ylabel("Number of records"); ax.set_title("Month-wise record counts by route-group folder")
    ax.legend(title="Folder"); save("fig1_monthwise")
    cols = ["Node", "Number", "Route", "Time"]
    adj = full.node_step == 1
    q = pd.Series({**{c: raw[c].isna().mean() * 100 for c in cols},
                   "Duplicate rows": (1 - len(clean_df) / len(raw)) * 100,
                   "Non-adjacent node pairs": (full.node_step != 1).mean() * 100,
                   "Adjacent pairs >30 min or <=0": (adj & ~full.interval_s.between(1, MAX_VALID_INTERVAL_S)).mean() * 100})
    fig, ax = plt.subplots(figsize=(5, 3.4)); q[::-1].plot(kind="barh", ax=ax, color="#1f3a68")
    ax.set_xlabel("Percentage of records (%)"); ax.set_ylabel("Variable / quality check"); ax.set_title("Missing values and data-quality checks")
    for i, v in enumerate(q[::-1]): ax.text(v + .2, i, f"{v:.2f}", va="center", fontsize=7)
    save("fig2_missing_quality")
    fig, ax = plt.subplots(figsize=(5, 3.4)); h = clean_df.groupby("hour").size()
    ax.bar(h.index, h.values, color="#1f3a68"); ax.set_xticks(range(4, 23, 2)); ax.set_xlabel("Hour of day"); ax.set_ylabel("Number of records"); ax.set_title("Time-of-day distribution of records")
    save("fig3_timeofday")
    fig, ax = plt.subplots(figsize=(5, 3.4)); f = clean_df.groupby(["Node", "Route"]).size().unstack(fill_value=0)
    ax.bar(f.index - .2, f["up"], .4, label="up", color="#1f3a68"); ax.bar(f.index + .2, f["down"], .4, label="down", color="#c0392b")
    ax.set_xlabel("Node code"); ax.set_ylabel("Number of records"); ax.set_title("Record frequency per node code and direction"); ax.legend()
    save("fig4_nodefreq")
    fig, ax = plt.subplots(figsize=(5, 3.4)); ax.hist(pair.target_min.clip(upper=10), bins=60, color="#1f3a68")
    ax.axvline(pair.target_min.median(), color="#c0392b", ls="--", label=f"median = {pair.target_min.median():.2f} min")
    ax.set_xlabel("Interval between consecutive records (min, clipped at 10)"); ax.set_ylabel("Number of intervals"); ax.set_title("Distribution of consecutive-record intervals"); ax.legend()
    save("fig5_interval_hist")
    cols = ["target_min", "from_node", "hour", "dir", "pos_in_run", "prev_interval_s", "is_peak", "group_id"]
    c = pair[cols].corr(); fig, ax = plt.subplots(figsize=(5, 4.2))
    im = ax.imshow(c, cmap="RdBu_r", vmin=-1, vmax=1); ax.set_xticks(range(len(cols))); ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right"); ax.set_yticklabels(cols)
    for i in range(len(cols)):
        for j in range(len(cols)): ax.text(j, i, f"{c.iloc[i,j]:.2f}", ha="center", va="center", fontsize=6)
    fig.colorbar(im, ax=ax, shrink=.8); ax.set_title("Pearson correlation of modelling variables"); ax.set_xlabel("Variable"); ax.set_ylabel("Variable")
    save("fig6_corr"); c.to_csv(TAB / "correlation_matrix.csv")
