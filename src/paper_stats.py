import sys, json, pandas as pd, numpy as np
from load_data import load_raw; from preprocess import clean, build_intervals; from config import TAB
raw=load_raw(); c,_=clean(raw); full,pair=build_intervals(c)
S={}
S['recs_by_month_group']={f"{k[0]}_{k[1]}":int(v) for k,v in raw.groupby(['month','group']).size().items()}
S['pairs_by_month']=pair.groupby('month').size().to_dict()
S['target_by_month']=pair.groupby('month').target_min.agg(['mean','median','std']).round(3).to_dict('index')
S['quantiles']=pair.target_min.quantile([.05,.25,.5,.75,.95,.99]).round(3).to_dict()
S['peak_median']=pair.groupby('is_peak').target_min.median().round(3).to_dict()
S['dir_median']=pair.groupby('dir').target_min.median().round(3).to_dict()
S['group_median']=pair.groupby('group').target_min.agg(['median','mean']).round(3).to_dict('index')
S['pairs_by_group']=pair.groupby('group').size().to_dict()
S['nodes_by_group']=c.groupby('group').Node.nunique().to_dict(); S['buses_by_group']=c.groupby('group').bus.nunique().to_dict()
S['prev_missing_share']=float(pair.prev_interval_s.isna().mean())
S['non_adjacent_share']=float((full.node_step!=1).mean()); S['neg_time_pairs']=int((full.interval_s<0).sum())
S['hours']=[int(c.hour.min()),int(c.hour.max())]
S['iqr_outliers_share']=float((pair.target_min>pair.target_min.quantile(.75)+1.5*(pair.target_min.quantile(.75)-pair.target_min.quantile(.25))).mean())
S['files_by_month']=raw.groupby('month').file.nunique().to_dict()
S['dups_ignoring_file']=int(c.duplicated(['Number','Route','Node','Time','month','day','group']).sum())
json.dump(S,open(TAB/'paper_stats.json','w'),indent=1,default=str); print(json.dumps(S,indent=1,default=str))
