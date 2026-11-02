"""Single source of truth for the paper text. All numbers are read from outputs/tables/*.csv|json."""
import json, pandas as pd
from config import TAB, FIG
R = pd.read_csv(TAB / "model_comparison.csv").set_index("model")
PR = pd.read_csv(TAB / "dataset_profile.csv", index_col=0)["value"]
ST = json.load(open(TAB / "paper_stats.json")); ES = pd.to_numeric(pd.read_csv(TAB / "error_summary.csv", index_col=0).iloc[:, 0], errors="coerce")
EX = json.load(open(TAB / "experiment_summary.json")); TU = pd.read_csv(TAB / "hyperparameter_tuning.csv")
AB = pd.read_csv(TAB / "ablation_decision_tree.csv"); PI = pd.read_csv(TAB / "permutation_importance_tree.csv").sort_values("rmse_increase", ascending=False); SG = pd.read_csv(TAB / "error_by_folder_direction.csv", index_col=0)
HR = pd.read_csv(TAB / "mae_by_hour.csv", index_col=0).iloc[:, 0]
def m(name, k): return R.loc[name, k]
LIN, POL, KNN, DT, MLP = "Linear Regression", "Polynomial Regression (deg 2)", "k-NN Regressor", "Decision Tree", "MLP Regressor"
SEG, PER, MEAN = "Baseline: segment historical mean", "Baseline: previous interval (persistence)", "Baseline: training mean"
f3 = lambda x: f"{x:.3f}"
rmse_gain = (m(SEG, "RMSE") - m(MLP, "RMSE")) / m(SEG, "RMSE") * 100
mae_gain = (m(SEG, "MAE") - m(MLP, "MAE")) / m(SEG, "MAE") * 100
n = lambda k: f"{int(PR[k]):,}"
T = f"{n('modelling_samples')}"; NTR, NTE = f"{EX['n_train']:,}", f"{EX['n_test']:,}"
peak_h = HR.idxmax()

B = []   # blocks
def H1(t): B.append(("h1", t))
def H2(t): B.append(("h2", t))
def P(t): B.append(("p", t))
def FIGB(f, cap, w=8.3): B.append(("fig", str(FIG / f), cap, w))

TITLE = (
    "Predicting Consecutive-Record Travel Intervals of Delhi City Buses "
    "Using Node-Level Timestamp Data and Machine Learning"
)
AUTHOR = "Muskan Sharma"
AFFIL = (
    "Department of Computer Science, "
    "Ramanujan College, University of Delhi, New Delhi, India"
    " | Exam Roll No.: 24020570020"
    " | College Roll No.: 24570040"
)
COURSE = (
    "Course: Machine Learning (B.Sc. (Hons.) Computer Science)"
    " | Supervisor: Mr. Nikhil"
    " | Problem No. 49 (Transport)"
    " | Article Type: Original Research Article"
)
ABSTRACT = (f"<b>Abstract.</b> This paper examines how much can be learned from the bus-record files supplied for Problem 49. The aim is to estimate the time between two consecutive observations of the same vehicle at adjacent node codes. "
 f"We analyse {n('raw_records')} timestamped node-passing records of {n('distinct_bus_ids')} buses supplied as {n('workbooks_read')} Excel workbooks covering three months and two route-group folders. "
 "The files contain a node code, vehicle identifier, direction and time of day, but no verified stop map, GPS trace or calendar date. The target is therefore a consecutive-record interval, not a validated stop-to-stop ETA. "
 f"Instead we predict the time between two consecutive records of the same bus at adjacent node codes ({T} samples, median {float(PR['target_median_min']):.2f} min). "
 f"Five regressors (linear, polynomial, k-NN, decision tree, MLP) were compared with three baselines using a month-folder-based holdout split (train: Months 1–2, test: Month 3). "
 f"The MLP gave the lowest test error (MAE {f3(m(MLP,'MAE'))} min, RMSE {f3(m(MLP,'RMSE'))} min, R² {f3(m(MLP,'R2'))}), but the decision tree was within {m(DT,'RMSE')-m(MLP,'RMSE'):.3f} min RMSE and the linear model reached R² {f3(m(LIN,'R2'))}. "
 f"Compared with a segment-wise historical mean, the best model lowered RMSE by {rmse_gain:.1f}% and MAE by {mae_gain:.1f}%. Predicting the previous interval was worse than predicting the training mean. "
 "The results suggest that these fields contain a useful but limited signal. A passenger-facing ETA system would still require verified stop locations, GPS observations and timetable information.")
KEYWORDS = "<b>Keywords:</b> bus travel time; Delhi; regression; k-NN; decision tree; MLP; month-folder holdout validation; SDG 9; SDG 11"

H1("1 Introduction")
P("When buses arrive unpredictably, commuters lose time at stops and many switch to private vehicles, which increases congestion and emissions. "
  "Accurate travel-time estimates are therefore linked to SDG 11 (Sustainable Cities and Communities) and SDG 9 (Industry, Innovation and Infrastructure). "
  "Our allocated problem (No. 49) asks for bus travel-time prediction for Delhi from time of day, route, stop sequence and position information.")
P("The supplied files are much simpler than a complete public-transport feed. Each row records a vehicle identifier, a numbered node, a direction and a time of day. Coordinates, verified stop names, schedules and calendar dates are not included. "
  "We therefore define a narrower and honest target, the <i>consecutive-record interval</i>, and keep it separate from true stop-to-stop ETA. "
  "The work has four practical parts: (i) a repeatable process for converting 184 workbooks into interval samples; (ii) a month-folder holdout comparison of five syllabus-level regressors and three baselines; "
  "(iii) an error analysis by hour of day; and (iv) a clear statement of what the data cannot support. Sections 2–3 cover related work and data, Sections 4–5 the method and set-up, Section 6 the results, and Section 7 the discussion.")

H1("2 Related Work")
P("Bus arrival time (BAT) prediction has a large literature. Singh and Kumar [1] review artificial-intelligence methods applied to BAT, and Abdi and Amrit [2] give a taxonomy of travel- and arrival-time prediction methods on road networks, "
  "discussing the factors that affect accuracy. Agafonov and Yumaganov [3] compare machine-learning methods, including neural networks and support-vector regression, for public-transport arrival time and note that the best choice depends on the input data used. "
  "Most such studies use GPS positions, schedules or traffic information, which are not available in our files. "
  "Because our observations are ordered in time, we avoid random shuffling and evaluate on a later period, in line with the cautions about cross-validation for time-ordered data discussed by Bergmeir and Benítez [4]. "
  "All models were implemented with scikit-learn [5]; the algorithms follow standard texts [6]. The k-NN rule goes back to Cover and Hart [7], regression trees to Breiman et al. [8], and the MLP is trained with the Adam optimiser [9].")

H1("3 Dataset and Preprocessing")
H2("3.1 Source and description")
P(f"The data were supplied as three archives (Month_1, Month_2, Month_3) containing {n('workbooks_read')} Excel workbooks, one per day, inside two sub-folders named 425 and 534. "
  "The original provider could not be independently confirmed. The allocation sheet points to the Delhi Open Transit Data portal, but the files we received are not GTFS tables and we did not verify their provenance, so we do not attribute them to any agency. "
  "We also do not know whether the folder names are bus route numbers; we call them <i>route-group folders</i>. All workbooks were read programmatically (no unreadable files). "
  f"After removing the index column, every workbook has four fields (Table 1). In total there are {n('raw_records')} records, {n('distinct_bus_ids')} distinct bus identifiers, {n('distinct_node_codes')} node codes and two directions (up, down). "
  f"Records fall between 04:48 and 22:00. Folder 425 has {ST['nodes_by_group']['425']} node codes and {ST['buses_by_group']['425']} buses; folder 534 has {ST['nodes_by_group']['534']} node codes and {ST['buses_by_group']['534']} buses.")
B.append(("table", "Table 1. Fields in the supplied workbooks and their use in this study.", ["Field", "Type", "Distinct", "Missing", "Use"],
  [["Node", "integer", "56", "0", "segment position (from-node)"], ["Number", "text", "202", "0", "groups records by bus"], ["Route", "up / down", "2", "0", "direction feature"],
   ["Time", "time string", "–", "0", "hour features; interval target"], ["Folder path", "folder names", "3 / 2 / 1–31", "–", "split; folder feature"]], [1.3, 1.6, 1.4, 1.2, 2.8]))
import numpy as np
def _fold(g): return [g, f"{sum(v for k, v in ST['recs_by_month_group'].items() if k.endswith('_'+g)):,}", str(ST['buses_by_group'][g]), str(ST['nodes_by_group'][g]), f"{ST['pairs_by_group'][g]:,}", f"{ST['group_median'][g]['mean']:.2f}", f"{ST['group_median'][g]['median']:.2f}"]
B.append(("table", "Table 2. Summary of the two route-group folders (all three months).", ["Folder", "Records", "Buses", "Nodes", "Samples", "Mean (min)", "Median (min)"], [_fold("425"), _fold("534")], [1.0, 1.3, 1.0, 1.1, 1.3, 1.2, 1.4]))
H2("3.2 Missing values, duplicates and interval construction")
P(f"There are no missing cells and no duplicate records (Fig. 2), so the main quality problems lie in the structure of the sequences. Within one bus, direction and day, the node code usually advances by one; "
  f"{ST['non_adjacent_share']*100:.1f}% of consecutive pairs are not adjacent (a skipped node, a new trip or a direction change) and were excluded. "
  f"Of the adjacent pairs, {int(PR['pairs_non_positive_interval'])} had a non-positive interval (time wrap-around between trips) and {int(PR['pairs_over_max_interval'])} exceeded 30 minutes, which we treat as layovers or logging gaps rather than travel. "
  f"This leaves <b>{T}</b> samples ({ST['pairs_by_month']['Month_1']:,} / {ST['pairs_by_month']['Month_2']:,} / {ST['pairs_by_month']['Month_3']:,} in Months 1/2/3). "
  "The 30-minute cut-off is a judgement call; intervals are short (Fig. 5), so it removes very little.")
FIGB("fig1_monthwise.png", "<b>Fig. 1.</b> Number of records per month folder and route-group folder. Folder 534 contributes about four times as many records as folder 425 in every month.")
FIGB("fig2_missing_quality.png", "<b>Fig. 2.</b> Missing-value and data-quality checks. The raw fields are complete; the only notable issue is non-adjacent node pairs.")
H2("3.3 Exploratory analysis")
P(f"Time of day (Fig. 3): records rise sharply after 05:00, peak in the 08:00 hour and decline through the evening. Node frequency (Fig. 4) is fairly even up to the high 30s and lower for higher codes, and codes above 41 occur only in folder 534; "
  "a few nodes (around code 22 and codes 27–29) have clearly fewer records, which may mean they are logged less reliably, but we did not investigate this. "
  f"The target (Fig. 5) is right-skewed: median {ST['quantiles']['0.5']:.2f} min, 5th–95th percentiles {ST['quantiles']['0.05']:.2f}–{ST['quantiles']['0.95']:.2f} min, and about {ST['iqr_outliers_share']*100:.1f}% of intervals lie above the IQR upper fence. "
  "These long intervals look like genuine delays or dwell times, so they were kept and no winsorisation was applied to the target; the metrics are therefore sensitive to them (Section 6). "
  "In the correlation matrix (Fig. 6) no single variable has a strong linear relationship with the interval (largest |r| = 0.13, for hour of day), which anticipates the moderate R² reported later.")
FIGB("fig3_timeofday.png", "<b>Fig. 3.</b> Number of records by hour of day (all months and both folders).")
FIGB("fig4_nodefreq.png", "<b>Fig. 4.</b> Record frequency per node code and direction. Codes above 41 occur only in folder 534.")
FIGB("fig5_interval_hist.png", "<b>Fig. 5.</b> Distribution of consecutive-record intervals (clipped at 10 min for display; the dashed line is the median).")
FIGB("fig6_corr.png", "<b>Fig. 6.</b> Pearson correlation matrix of the target and the main numeric variables (all months, n = " + T + ").", 8.0)
H2("3.4 Feature engineering")
P("For each sample the following features are available at prediction time (Table 3): the from-node code, direction, route-group folder, cyclic hour-of-day encoding (sin, cos of 2πt/86400 s), a peak-hour flag (08–10 h and 17–19 h, a choice we made without verifying Delhi's peak periods), "
  "the number of consecutive adjacent records already seen in the current run, the previous interval of the same bus (median-imputed when unavailable, with a missing-indicator; "
  f"{ST['prev_missing_share']*100:.1f}% of samples), and the historical mean interval of the same segment (folder, direction, from-node) computed on the training data only. Features are standardised for the models that need it, with the scaler fitted on training data inside each pipeline.")
B.append(("table", "Table 3. Features used by the models (10 in total).", ["Feature", "Description"],
  [["from_node", "node code at the start of the segment"], ["dir, group_id", "direction (up = 1); folder (425 / 534)"], ["hour_sin, hour_cos, is_peak", "cyclic time of day; peak-hour flag"],
   ["pos_in_run", "adjacent records already seen in this run"], ["prev_interval_min, prev_missing", "previous interval (imputed); missing flag"], ["seg_hist_mean", "training-set mean interval of the segment"]], [3.2, 5.1]))

H1("4 Methodology")
P("Fig. 7 summarises the workflow. Let <b>x</b> be the feature vector of a segment and <i>y</i> the interval in minutes. Three baselines are used: the training mean, the segment historical mean, and persistence (the previous interval of the same bus).")
FIGB("fig7_pipeline.png", "<b>Fig. 7.</b> Methodology pipeline. Everything after the split is fitted on training data only.", 8.0)
P("<b>Linear regression</b> fits ŷ = <b>w</b><super>T</super><b>x</b> + b by least squares. <b>Polynomial regression</b> expands the standardised features to all degree-2 terms (squares and pairwise products) before the same fit. "
  "<b>k-NN regression</b> averages the targets of the k nearest training points under Euclidean distance on standardised features. The <b>decision tree</b> recursively splits the feature space to minimise squared error within nodes, with maximum depth and minimum leaf size as controls. "
  "The <b>MLP</b> has two ReLU hidden layers, an L2 penalty α, early stopping on a 10% validation split and the Adam optimiser. Performance is measured by")
B.append(("eq", "MAE = (1/n) Σ |y − ŷ|,   RMSE = √[(1/n) Σ (y − ŷ)²],   R² = 1 − Σ (y − ŷ)² / Σ (y − ȳ)²", "(1)"))

H1("5 Experimental Setup")
P(f"<b>Split.</b> Data are split by month folder, not at random: training = Month_1 + Month_2 ({NTR} samples), test = Month_3 ({NTE}). Month_3 was never used for tuning or for fitting any feature statistic. "
  "The files contain no calendar dates. Month_3 is treated as a held-out folder, but the folder labels do not establish a calendar sequence or a seasonal comparison. "
  f"<b>Tuning.</b> Hyper-parameters were chosen by fitting on a {EX['n_tune_fit']:,}-sample random subset of Month_1 and minimising RMSE on a {EX['n_tune_val']:,}-sample subset of Month_2; the selected settings were then refitted on all training data (Table 4). "
  f"<b>Environment.</b> Python 3, scikit-learn, pandas, NumPy and Matplotlib; random seed {EX['seed']}. The complete code regenerates every number and figure in this paper (run_all.bat on Windows or python src/main.py); the README lists the steps and the order of the scripts.")
def tune_best(name): 
    t = TU[TU.model == name]; return t.loc[t.val_RMSE.idxmin()]
rows = []
grids = {LIN: "none", POL: "degree 2", KNN: "k ∈ {15, 50, 100}", DT: "depth {6,10,14} × leaf {50,200}", MLP: "layers {(64,32),(128,64)} × α {1e-4, 1e-2}"}
for k in [LIN, POL, KNN, DT, MLP]:
    b = tune_best(k); rows.append([k.replace(" Regressor", "").replace("Regression (deg 2)", "(deg 2)"), grids[k], R.loc[k, "setting"].replace(",uniform", ""), f"{b.val_RMSE:.3f}"])
B.append(("table", "Table 4. Hyper-parameter grids, selected settings and validation RMSE (min; fit Month_1, validate Month_2 subset).", ["Model", "Grid searched", "Selected", "Val. RMSE"], rows, [2.0, 3.4, 2.0, 0.9]))

H1("6 Results")
H2("6.1 Model comparison")
rows = []
for k, lab in [(MEAN, "Training mean"), (SEG, "Segment hist. mean"), (PER, "Persistence"), (LIN, "Linear"), (POL, "Polynomial (deg 2)"), (KNN, "k-NN (k = 50)"), (DT, "Decision tree"), (MLP, "MLP (128-64)")]:
    rows.append([lab, f3(R.loc[k, "MAE"]), f3(R.loc[k, "RMSE"]), f3(R.loc[k, "R2"]), f"{R.loc[k,'fit_secs']:.1f}"])
P(f"Table 5 and Fig. 8 show that all five learned models beat the three baselines on every metric. The MLP is best (MAE {f3(m(MLP,'MAE'))}, RMSE {f3(m(MLP,'RMSE'))}, R² {f3(m(MLP,'R2'))}), but the decision tree (RMSE {f3(m(DT,'RMSE'))}) and k-NN ({f3(m(KNN,'RMSE'))}) are practically tied with it; "
  f"the differences among these three are at most {m(KNN,'RMSE')-m(MLP,'RMSE'):.3f} min in RMSE, much smaller than the typical error, and we did not test their statistical significance. "
  f"The MLP needed {m(MLP,'fit_secs'):.0f} s to fit against {m(DT,'fit_secs'):.1f} s for the tree, so the tree is the better practical choice here. "
  f"The linear model (R² {f3(m(LIN,'R2'))}) and the degree-2 model ({f3(m(POL,'R2'))}) are somewhat weaker, which suggests mild non-linearity (for example, interactions between node and time of day).")
B.append(("table", f"Table 5. Test-set results on Month_3 (n = {NTE}). MAE and RMSE in minutes; fit time in seconds on one CPU core. Best model in bold.", ["Model", "MAE", "RMSE", "R²", "Fit (s)"], rows, [2.7, 1.2, 1.2, 1.2, 1.4], 7))
P(f"The strongest baseline is the segment historical mean (RMSE {f3(m(SEG,'RMSE'))}); the best model improves on it by {rmse_gain:.1f}% in RMSE and {mae_gain:.1f}% in MAE. The gain in MAE is larger than in RMSE because a few very long intervals dominate squared error and none of the models can anticipate them. "
  f"Persistence performs worst (R² {f3(m(PER,'R2'))}): presumably because a single previous interval is a noisy proxy for the next one, and a negative R² means it is worse than always predicting the mean.")
FIGB("fig8_model_comparison.png", "<b>Fig. 8.</b> Test (a) MAE, (b) RMSE and (c) R² of the three baselines (grey) and the five regressors (blue) on Month_3.", 8.2)
B.append(("table", "Table 6. Interval statistics (min) by month folder; the test month has the largest spread.", ["Month", "Samples", "Mean", "Median", "Std. dev."],
  [[k.replace("_", " "), f"{ST['pairs_by_month'][k]:,}", f"{v['mean']:.3f}", f"{v['median']:.3f}", f"{v['std']:.3f}"] for k, v in ST['target_by_month'].items()], [1.8, 1.6, 1.3, 1.3, 1.4]))
P(f"The test error is higher than the validation error used for tuning (RMSE {tune_best(MLP).val_RMSE:.3f} on the Month_2 subset against {f3(m(MLP,'RMSE'))} on Month_3; R² {tune_best(MLP).val_R2:.3f} against {f3(m(MLP,'R2'))}). Table 6 shows a likely contributing factor: the spread of the target grows from Month_1 to Month_3 "
  f"(standard deviation {ST['target_by_month']['Month_2']['std']:.2f} in Month_2, {ST['target_by_month']['Month_3']['std']:.2f} in Month_3), so the last month is somewhat harder. Differences in subsampling may also play a role; we did not separate the two effects.")
H2("6.2 Error analysis")
P(f"For the MLP, {ES['share_abs_err_lt_0.5min']*100:.0f}% of test predictions are within 0.5 min and {ES['share_abs_err_lt_1min']*100:.0f}% within 1 min of the observed interval; the median absolute error is {ES['median_abs_err']:.2f} min but the 95th percentile is {ES['p95_abs_err']:.2f} min. "
  f"The mean residual is +{ES['residual_mean']:.2f} min, i.e. a slight average under-prediction. Fig. 9 shows good agreement for intervals below about 3 min and a wide scatter above them: very long observed intervals are rarely predicted. "
  "The residual plot (Fig. 10) shows the same asymmetry; its sharp lower edge is a property of the data, because an interval cannot be shorter than about 0.1 min, so the residual cannot fall below −ŷ.")
FIGB("fig9_actual_vs_pred.png", "<b>Fig. 9.</b> Observed versus predicted interval for the MLP on the test month (density of points, axes clipped at 10 min).", 8.0)
FIGB("fig10_residuals.png", "<b>Fig. 10.</b> Residuals of the MLP: (left) against the predicted value; (right) histogram (clipped to −6…10 min).", 8.4)
P(f"Error also depends on the time of day (Fig. 11): the MAE rises from {HR.min():.2f} min in the early morning to {HR.max():.2f} min at {int(peak_h)}:00 and falls again after the evening peak. "
  "We did not investigate the cause (for example traffic, boarding time or fewer samples); the pattern should be read as descriptive only.")
FIGB("fig11_mae_by_hour.png", "<b>Fig. 11.</b> Test MAE of the MLP by hour of day.", 8.0)

H2("6.3 Feature importance and ablation")
P(f"To see which inputs matter, we used the decision tree because it is fast enough to refit several times (the MLP takes {m(MLP,'fit_secs')/60:.0f} min). Permutation importance on a 60,000-sample subset of the test month (Fig. 12) is dominated by the segment historical mean (RMSE rises by {PI.iloc[0].rmse_increase:.2f} min when it is shuffled), "
  f"followed by the hour-of-day features, the previous interval and the from-node code; direction, folder, run position and the peak flag matter little. "
  "Importance of correlated features is shared and should be read with care.")
FIGB("fig12_importance.png", "<b>Fig. 12.</b> Permutation importance of the ten features for the decision tree on a subset of the test month (error bars: standard deviation over three repeats).", 8.0)
ab = lambda k: AB.set_index("setting").loc[k]
P(f"The ablation in Table 7 gives a complementary view. Removing the hour-of-day features hurts most (RMSE {ab('– time of day (hour, peak)').RMSE:.3f} against {ab('All features').RMSE:.3f} with all features). "
  f"Removing the segment historical mean costs less ({ab('– segment historical mean').RMSE:.3f}) than its permutation importance suggests, because the tree can rebuild much of it from node, direction and folder; the same holds for the previous interval ({ab('– previous interval (+flag)').RMSE:.3f}). "
  "Removing node/run position or direction/folder changes almost nothing. In short, time of day and segment identity carry most of the usable signal.")
B.append(("table", "Table 7. Feature-group ablation for the decision tree (test month; “–” means the group is removed and the tree is refitted).", ["Setting", "MAE", "RMSE", "R²"],
  [[r.setting, f3(r.MAE), f3(r.RMSE), f3(r.R2)] for r in AB.itertuples()], [3.6, 1.2, 1.2, 1.2]))
H2("6.4 Error by folder and direction")
P(f"For the MLP, errors differ across subgroups (Table 8). Folder 425 has the longer intervals (mean {SG.loc['folder 425','mean_target']:.2f} min against {SG.loc['folder 534','mean_target']:.2f} min) and larger errors (RMSE {SG.loc['folder 425','RMSE']:.2f} against {SG.loc['folder 534','RMSE']:.2f} min); "
  f"the down direction is harder than the up direction (RMSE {SG.loc['down','RMSE']:.2f} against {SG.loc['up','RMSE']:.2f} min, R² {SG.loc['down','R2']:.2f} against {SG.loc['up','R2']:.2f}). A single overall score therefore hides differences between services, which matters if the model were used for passenger information.")
B.append(("table", "Table 8. MLP test error by route-group folder and direction (MAE, RMSE in minutes).", ["Subgroup", "n", "MAE", "RMSE", "R²"],
  [[k, f"{int(r.n):,}", f3(r.MAE), f3(r.RMSE), f3(r.R2)] for k, r in SG.iterrows()], [2.2, 1.6, 1.2, 1.2, 1.2]))
H1("7 Discussion")
P("<b>What the results show.</b> The available fields (segment, direction, folder, time of day and the previous interval) explain a little under half of the variance in interval length, and a historical segment average already captures most of this. "
  "More flexible models add a modest, consistent improvement. Because the three best models are so close, model choice should be guided by speed and simplicity rather than by the last decimal of RMSE.")
P("<b>Practical implications.</b> For an operator, the simplest useful system would be a lookup of the historical mean interval by segment and time of day, refreshed regularly; the learned models improve on it by a small margin and mainly help on typical segments rather than on unusual delays. "
  "A decision tree gives most of the benefit with a fit time of seconds, can be retrained as new months arrive, and can be inspected, which is attractive for a transport department.")
P("<b>Limitations.</b> (i) The target is the interval between consecutive <i>records</i>, not a verified stop-to-stop travel time or arrival time; node codes may be sequence indices rather than stops, and logging could have its own delays. "
  "(ii) The data hold no coordinates, schedule, weather or incident information, and no calendar dates, so weekday, holiday and seasonal effects cannot be modelled. "
  "(iii) The provenance of the data was not verified. (iv) The segment-mean feature is computed on all training rows, including each row's own target; with several thousand rows per segment the effect is small, but out-of-fold encoding would be cleaner. "
  "(v) Hyper-parameter search used subsamples and small grids, and results come from a single run with one seed. (vi) The test period follows the training period only by folder order, so we cannot say how well the models generalise to other seasons or years.")
P("<b>Ethics and SDG relevance.</b> The data contain vehicle identifiers but no passenger information; even so, results should not be used to judge individual drivers. Reliable travel-time information would support SDG 11 (public transport as a practical alternative to private vehicles) and SDG 9 (data-driven transport infrastructure), "
  "but this study is a first step, not a deployable ETA system.")

H1("8 Conclusion and Future Work")
P(f"Using {n('raw_records')} node-passing records of Delhi city buses, we built a reproducible pipeline and compared five classical regressors with three baselines on a held-out month. The best model (MLP) reached MAE {f3(m(MLP,'MAE'))} min and R² {f3(m(MLP,'R2'))}, "
  f"only slightly ahead of a decision tree and k-NN, and about {rmse_gain:.0f}% better in RMSE than a segment-wise historical mean. Future work should obtain a verified stop mapping and GPS-based arrival labels so that real stop-to-stop ETA can be predicted, add weather, calendar and schedule information, "
  "use gradient-boosted trees as an extra comparison, and test across more months.")

H1("Declarations")
P(f"<b>Data availability.</b> The analysed files are the three supplied archives (Month_1, Month_2, Month_3; {n('workbooks_read')} workbooks). Their original source has not been independently confirmed and they are not redistributed with this paper. Code, figures and result tables are in the project folder.")
P("<b>Conflict of interest.</b> The author declares no conflict of interest. <b>Funding.</b> None.")
P("<b>Use of AI tools.</b> ChatGPT (OpenAI) was used for assistance with code troubleshooting and language editing. The dataset processing, model runs, numerical results and figures are drawn from the supplied project files and saved experiment outputs. The author is responsible for reviewing the analysis and confirming that the final paper accurately represents the work.")

REFS = [
 "N. Singh and K. Kumar, “A review of bus arrival time prediction using artificial intelligence,” <i>WIREs Data Mining and Knowledge Discovery</i>, vol. 12, no. 4, 2022, doi: 10.1002/widm.1457.",
 "A. Abdi and C. Amrit, “A review of travel and arrival-time prediction methods on road networks: classification, challenges and opportunities,” <i>PeerJ Computer Science</i>, vol. 7, Art. no. e689, 2021, doi: 10.7717/peerj-cs.689.",
 "A. A. Agafonov and A. S. Yumaganov, “Performance comparison of machine learning methods in the bus arrival time prediction problem,” in <i>Proc. ITNT-2019</i>, CEUR Workshop Proceedings, vol. 2416, 2019.",
 "C. Bergmeir and J. M. Benítez, “On the use of cross-validation for time series predictor evaluation,” <i>Information Sciences</i>, vol. 191, pp. 192–213, 2012, doi: 10.1016/j.ins.2011.12.028.",
 "F. Pedregosa <i>et al.</i>, “Scikit-learn: Machine learning in Python,” <i>Journal of Machine Learning Research</i>, vol. 12, pp. 2825–2830, 2011.",
 "T. Hastie, R. Tibshirani and J. Friedman, <i>The Elements of Statistical Learning: Data Mining, Inference, and Prediction</i>, 2nd ed. New York, NY, USA: Springer, 2009.",
 "T. M. Cover and P. E. Hart, “Nearest neighbor pattern classification,” <i>IEEE Transactions on Information Theory</i>, vol. 13, no. 1, pp. 21–27, 1967.",
 "L. Breiman, J. H. Friedman, R. A. Olshen and C. J. Stone, <i>Classification and Regression Trees</i>. Belmont, CA, USA: Wadsworth, 1984.",
 "D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,” in <i>Proc. ICLR</i>, 2015 (arXiv:1412.6980).",
]
APPX = ("Appendix A. Validation tuning results", ["Model", "Setting", "Val. MAE", "Val. RMSE", "Val. R²"],
        [[r.model.replace(" Regressor", "").replace("Regression (deg 2)", "(deg 2)"), r.setting, f3(r.val_MAE), f3(r.val_RMSE), f3(r.val_R2)] for r in TU.itertuples()])

# Appendix B uses the saved hourly MAE table. The prediction pickle is deliberately
# not loaded here: it is version-sensitive and is not needed to build the paper.
APPX_B = ("Appendix B. Test error by hour of day",
          "MLP test mean absolute error by hour. The same hourly MAE values are shown in Fig. 11.",
          ["Hour", "MAE (min)"],
          [[f"{h:02d}:00", f3(v)] for h, v in HR.items()])
APPX_C = ("Appendix C. Reproducibility",
          "The project folder contains <i>src/</i> (load_data, preprocess, eda, train_models, make_result_figures, make_pipeline_figure, extra_analysis, paper_stats, build_pdf, build_docx, main), "
          "<i>outputs/figures</i> (all figures as 300-dpi PNG), <i>outputs/tables</i> (model_comparison.csv, dataset_profile.csv, hyperparameter_tuning.csv, ablation and importance tables) and the paper in PDF and DOCX form. "
          "After placing the three unzipped Month folders in <i>data/</i>, running <i>run_all.bat</i> (Windows) or <i>python src/main.py</i> repeats every step; the MLP stage is the slowest (about 11 min on one CPU core). "
          "Random seed 42 is fixed for sampling, trees and the MLP.")
