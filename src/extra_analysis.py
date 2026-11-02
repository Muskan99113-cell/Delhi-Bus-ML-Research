"""Extra analyses: feature-group ablation + permutation importance (decision tree, fast) and error by folder/direction (saved MLP predictions)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from load_data import load_raw; from preprocess import clean, build_intervals
from train_models import make_features
from config import SEED, TAB, TRAIN_MONTHS, TEST_MONTHS
from plotstyle import setup, save
setup()
pair = build_intervals(clean(load_raw())[0])[1]
tr = pair[pair.month.isin(TRAIN_MONTHS)].reset_index(drop=True); te = pair[pair.month.isin(TEST_MONTHS)].reset_index(drop=True)
Xtr, (Xte,) = make_features(tr, [te]); ytr, yte = tr.target_min.values, te.target_min.values
mk = lambda: DecisionTreeRegressor(max_depth=14, min_samples_leaf=50, random_state=SEED)
def ev(cols):
    p = mk().fit(Xtr[cols], ytr).predict(Xte[cols]); return mean_absolute_error(yte, p), float(np.sqrt(mean_squared_error(yte, p))), r2_score(yte, p)
allc = list(Xtr.columns)
groups = {"All features": [], "– segment historical mean": ["seg_hist_mean"], "– previous interval (+flag)": ["prev_interval_min", "prev_missing"],
          "– time of day (hour, peak)": ["hour_sin", "hour_cos", "is_peak"], "– node / run position": ["from_node", "pos_in_run"], "– direction, folder": ["dir", "group_id"]}
rows = []
for k, drop in groups.items():
    a, r, s = ev([c for c in allc if c not in drop]); rows.append(dict(setting=k, MAE=a, RMSE=r, R2=s))
A = pd.DataFrame(rows); A.to_csv(TAB / "ablation_decision_tree.csv", index=False); print(A.round(4))
mdl = mk().fit(Xtr, ytr); idx = np.random.RandomState(SEED).choice(len(Xte), 60000, replace=False)
pi = permutation_importance(mdl, Xte.iloc[idx], yte[idx], scoring="neg_root_mean_squared_error", n_repeats=3, random_state=SEED)
I = pd.DataFrame({"feature": allc, "rmse_increase": pi.importances_mean, "std": pi.importances_std}).sort_values("rmse_increase"); I.to_csv(TAB / "permutation_importance_tree.csv", index=False); print(I)
fig, ax = plt.subplots(figsize=(5, 3.3)); ax.barh(I.feature, I.rmse_increase, xerr=I["std"], color="#1f3a68")
ax.set_xlabel("Increase in test RMSE when the feature is permuted (min)"); ax.set_ylabel("Feature"); ax.set_title("Permutation importance (decision tree, Month_3 subset)"); save("fig12_importance")
P = pd.read_pickle(TAB / "test_predictions.pkl"); P["err"] = P.target_min - P["MLP Regressor"]
def sm(d): return pd.Series(dict(n=len(d), MAE=d.err.abs().mean(), RMSE=np.sqrt((d.err**2).mean()), R2=1 - (d.err**2).sum() / ((d.target_min - d.target_min.mean())**2).sum(), mean_target=d.target_min.mean()))
G = pd.concat({"folder " + str(k): sm(d) for k, d in P.groupby("group")}, axis=1).T
D = pd.concat({k: sm(d) for k, d in P.assign(Route=P.Route).groupby("Route")}, axis=1).T
pd.concat([G, D]).to_csv(TAB / "error_by_folder_direction.csv"); print(pd.concat([G, D]).round(3))
