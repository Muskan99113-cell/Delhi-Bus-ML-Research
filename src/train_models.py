"""Train and evaluate 5 regressors + baselines on consecutive-record intervals.
Split is chronological by data folder: train = Month_1+Month_2, test = Month_3.
Hyper-parameters are chosen by fitting on Month_1 and validating on Month_2 (never on the test month)."""
import time, json, itertools, numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from config import SEED, TAB, TRAIN_MONTHS, TEST_MONTHS

BASE = ["from_node", "dir", "group_id", "hour_sin", "hour_cos", "is_peak", "pos_in_run"]
def seg_key(d): return d["group_id"].astype(str) + "_" + d["dir"].astype(str) + "_" + d["from_node"].astype(str)

def make_features(train, other_list):
    """Segment-historical mean target-encoded from `train` only (no leakage); lag imputed with train median."""
    seg = train.assign(k=seg_key(train)).groupby("k")["target_min"].mean()
    gm = train["target_min"].mean(); med = train["prev_interval_s"].median()
    def f(d):
        X = d[BASE].copy()
        X["seg_hist_mean"] = seg_key(d).map(seg).fillna(gm).values
        X["prev_interval_min"] = (d["prev_interval_s"].fillna(med) / 60).values
        X["prev_missing"] = d["prev_interval_s"].isna().astype(int).values
        return X
    return f(train), [f(o) for o in other_list]

def metrics(y, p):
    return dict(MAE=mean_absolute_error(y, p), RMSE=float(np.sqrt(mean_squared_error(y, p))), R2=r2_score(y, p))

def candidates():
    return {
     "Linear Regression": [("default", lambda: make_pipeline(StandardScaler(), LinearRegression()))],
     "Polynomial Regression (deg 2)": [("deg2", lambda: make_pipeline(StandardScaler(), PolynomialFeatures(2, include_bias=False), LinearRegression()))],
     "k-NN Regressor": [(f"k={k},{w}", (lambda k=k, w=w: make_pipeline(StandardScaler(), KNeighborsRegressor(k, weights=w, n_jobs=-1)))) for k in (15, 50, 100) for w in ("uniform",)],
     "Decision Tree": [(f"depth={d},leaf={l}", (lambda d=d, l=l: DecisionTreeRegressor(max_depth=d, min_samples_leaf=l, random_state=SEED))) for d in (6, 10, 14) for l in (50, 200)],
     "MLP Regressor": [(f"h={h},a={a}", (lambda h=h, a=a: make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=h, alpha=a, early_stopping=True, max_iter=60, random_state=SEED)))) for h in ((64, 32), (128, 64)) for a in (1e-4, 1e-2)],
    }

def run(pair):
    rng = np.random.RandomState(SEED)
    tr = pair[pair.month.isin(TRAIN_MONTHS)].reset_index(drop=True)
    te = pair[pair.month.isin(TEST_MONTHS)].reset_index(drop=True)
    m1, m2 = tr[tr.month == "Month_1"], tr[tr.month == "Month_2"]
    # --- tuning: fit Month_1 (sub-sampled), validate Month_2 (sub-sampled)
    s1 = m1.sample(min(120000, len(m1)), random_state=SEED).reset_index(drop=True)
    s2 = m2.sample(min(100000, len(m2)), random_state=SEED).reset_index(drop=True)
    Xs1, (Xs2,) = make_features(m1, [s2]); Xs1 = make_features(m1, [s1])[1][0]
    best, tune_rows = {}, []
    for name, cands in candidates().items():
        scores = []
        for lab, mk in cands:
            t0 = time.time(); mdl = mk().fit(Xs1, s1.target_min); p = mdl.predict(Xs2)
            r = metrics(s2.target_min, p); scores.append((r["RMSE"], lab, mk))
            tune_rows.append(dict(model=name, setting=lab, val_MAE=r["MAE"], val_RMSE=r["RMSE"], val_R2=r["R2"], secs=round(time.time()-t0, 1)))
            print(name, lab, round(r["RMSE"], 4), flush=True)
        best[name] = min(scores, key=lambda x: x[0])
    pd.DataFrame(tune_rows).to_csv(TAB / "hyperparameter_tuning.csv", index=False)
    # --- final fit on Month_1+2, evaluate Month_3
    Xtr, (Xte,) = make_features(tr, [te]); ytr, yte = tr.target_min.values, te.target_min.values
    res, preds = [], {}
    # baselines
    gm = ytr.mean(); base = {"Baseline: training mean": np.full(len(yte), gm),
                             "Baseline: segment historical mean": Xte["seg_hist_mean"].values,
                             "Baseline: previous interval (persistence)": Xte["prev_interval_min"].values}
    for n, p in base.items(): res.append(dict(model=n, setting="-", **metrics(yte, p), fit_secs=0.0)); preds[n] = p
    for name, (v, lab, mk) in best.items():
        t0 = time.time(); mdl = mk().fit(Xtr, ytr); p = mdl.predict(Xte)
        res.append(dict(model=name, setting=lab, **metrics(yte, p), fit_secs=round(time.time()-t0, 1))); preds[name] = p
        print("FINAL", name, lab, res[-1], flush=True)
    R = pd.DataFrame(res); R.to_csv(TAB / "model_comparison.csv", index=False)
    out = te[["month", "group", "day", "bus", "Route", "from_node", "hour", "target_min"]].copy()
    for n, p in preds.items(): out[n] = p
    out.to_pickle(TAB / "test_predictions.pkl")
    Xtr.assign(target=ytr).describe().to_csv(TAB / "feature_summary_train.csv")
    json.dump(dict(seed=SEED, n_train=len(tr), n_test=len(te), n_tune_fit=len(s1), n_tune_val=len(s2), features=list(Xtr.columns),
                   chosen={k: v[1] for k, v in best.items()}), open(TAB / "experiment_summary.json", "w"), indent=2)
    return R, out
