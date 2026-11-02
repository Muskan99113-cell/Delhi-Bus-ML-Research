"""Result figures built from outputs/tables/model_comparison.csv and test_predictions.pkl (real values only)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import TAB, SEED
from plotstyle import setup, save
setup()
R = pd.read_csv(TAB / "model_comparison.csv")
short = {"Baseline: training mean": "Mean", "Baseline: segment historical mean": "Seg. mean", "Baseline: previous interval (persistence)": "Persist.",
         "Linear Regression": "Linear", "Polynomial Regression (deg 2)": "Poly-2", "k-NN Regressor": "k-NN", "Decision Tree": "Tree", "MLP Regressor": "MLP"}
R["lab"] = R.model.map(short); cols = ["#9aa5b1"] * 3 + ["#1f3a68"] * 5
for i, (m, t) in enumerate([("MAE", "MAE (min)"), ("RMSE", "RMSE (min)"), ("R2", "R²")]):
    fig, ax = plt.subplots(figsize=(5, 3.2)); b = ax.bar(R.lab, R[m], color=cols)
    ax.set_xlabel("Model (grey = baselines)"); ax.margins(y=0.12); ax.axhline(0, color="k", lw=.5); ax.set_ylabel(t); ax.set_title(f"Test-set {m if m!='R2' else 'R²'} by model (Month_3)")
    for r, v in zip(b, R[m]): ax.text(r.get_x() + r.get_width() / 2, v + (0.01 if v >= 0 else -0.01), f"{v:.3f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=6.5)
    plt.xticks(rotation=30, ha="right"); save(f"fig8{'abc'[i]}_{m.lower()}")
fig, axs = plt.subplots(3, 1, figsize=(5, 6.2), sharex=True)
for ax, (m, t, pn) in zip(axs, [("MAE", "MAE (min)", "(a)"), ("RMSE", "RMSE (min)", "(b)"), ("R2", "R²", "(c)")]):
    b = ax.bar(R.lab, R[m], color=cols); ax.set_ylabel(t); ax.set_title(f"{pn} Test {m if m!='R2' else 'R²'} by model (Month_3)", fontsize=8); ax.margins(y=0.15); ax.axhline(0, color="k", lw=.5)
    for r, v in zip(b, R[m]): ax.text(r.get_x() + r.get_width() / 2, v + (0.01 if v >= 0 else -0.01), f"{v:.3f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=6.5)
axs[-1].set_xlabel("Model (grey = baselines, blue = the five required regressors)"); plt.setp(axs[-1].get_xticklabels(), rotation=30, ha="right"); save("fig8_model_comparison")
P = pd.read_pickle(TAB / "test_predictions.pkl"); best = R[R.model.isin(list(short)[3:])].sort_values("RMSE").iloc[0].model
y, p = P.target_min.values, P[best].values
fig, ax = plt.subplots(figsize=(5, 3.8)); hb = ax.hexbin(y, p, gridsize=60, extent=(0, 10, 0, 10), bins="log", cmap="viridis", mincnt=1)
ax.plot([0, 10], [0, 10], color="#c0392b", lw=1, label="perfect prediction"); fig.colorbar(hb, label="log10(count)")
ax.set_xlabel("Observed interval (min)"); ax.set_ylabel("Predicted interval (min)"); ax.set_title(f"Observed vs predicted ({best}, axes clipped at 10 min)"); ax.legend(); save("fig9_actual_vs_pred")
res = y - p
fig, axs = plt.subplots(1, 2, figsize=(7, 3.2))
axs[0].hexbin(p, res, gridsize=60, extent=(0, 6, -6, 10), bins="log", cmap="viridis", mincnt=1); axs[0].axhline(0, color="#c0392b", lw=1)
axs[0].set_xlabel("Predicted interval (min)"); axs[0].set_ylabel("Residual (observed − predicted, min)"); axs[0].set_title("Residuals vs predictions")
axs[1].hist(res.clip(-6, 10), bins=80, color="#1f3a68"); axs[1].set_xlabel("Residual (min, clipped to [−6, 10])"); axs[1].set_ylabel("Number of intervals"); axs[1].set_title("Residual distribution")
save("fig10_residuals")
# error by hour (extra)
e = pd.DataFrame({"hour": P.hour, "ae": np.abs(res)}).groupby("hour").ae.mean()
fig, ax = plt.subplots(figsize=(5, 3.2)); ax.plot(e.index, e.values, marker="o", color="#1f3a68"); ax.set_xticks(range(4, 23, 2)); ax.set_xlabel("Hour of day"); ax.set_ylabel("MAE (min)"); ax.set_title(f"Test MAE by hour of day ({best})"); save("fig11_mae_by_hour")
e.to_csv(TAB / "mae_by_hour.csv")
pd.Series({"best_model": best, "residual_mean": res.mean(), "residual_std": res.std(), "share_abs_err_lt_1min": (np.abs(res) < 1).mean(),
           "share_abs_err_lt_0.5min": (np.abs(res) < .5).mean(), "median_abs_err": np.median(np.abs(res)), "p95_abs_err": np.quantile(np.abs(res), .95)}).to_csv(TAB / "error_summary.csv")
print(open(TAB / "error_summary.csv").read()); print(e.round(3).to_dict())
