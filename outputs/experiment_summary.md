# Experiment summary
- Files read: 184 workbooks, 0 unreadable; records: 924,375; buses: 202; node codes: 56; duplicates: 0; missing cells: 0
- Modelling samples (adjacent node step, 0 < interval <= 30 min): 867,574; train 585,678 (Month_1+2), test 281,896 (Month_3); seed 42
- Features: from_node, dir, group_id, hour_sin, hour_cos, is_peak, pos_in_run, seg_hist_mean, prev_interval_min, prev_missing

| model                                     | setting            |    MAE |   RMSE |      R2 |   fit_secs |
|:------------------------------------------|:-------------------|-------:|-------:|--------:|-----------:|
| Baseline: training mean                   | -                  | 1.1117 | 1.9668 | -0.0005 |        0   |
| Baseline: segment historical mean         | -                  | 0.6857 | 1.5327 |  0.3924 |        0   |
| Baseline: previous interval (persistence) | -                  | 1.4222 | 2.5131 | -0.6335 |        0   |
| Linear Regression                         | default            | 0.6764 | 1.4949 |  0.422  |        0.3 |
| Polynomial Regression (deg 2)             | deg2               | 0.6435 | 1.4686 |  0.4421 |        7.5 |
| k-NN Regressor                            | k=50,uniform       | 0.5987 | 1.4317 |  0.4699 |       36.8 |
| Decision Tree                             | depth=14,leaf=50   | 0.5975 | 1.4283 |  0.4724 |        2.8 |
| MLP Regressor                             | h=(128, 64),a=0.01 | 0.5958 | 1.4259 |  0.4741 |      686.3 |

Caveats: target is the consecutive-record interval, not verified stop-to-stop ETA; no calendar dates, GPS or verified stop mapping; data source unconfirmed;
single seed, no significance tests; ablation/importance use the decision tree only.
