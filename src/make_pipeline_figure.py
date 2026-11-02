"""Fig. 7: methodology flow diagram (schematic, contains no data values except counts read from the profile CSV)."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from config import TAB
from plotstyle import setup, save
setup(); P = pd.read_csv(TAB / "dataset_profile.csv", index_col=0)["value"]
steps = [("1  Raw data", f"184 Excel workbooks, {int(P.raw_records):,} records\\nNode, Number, Route, Time"),
         ("2  Cleaning", "parse time, normalise bus IDs\\ndedupe, keep month / folder / day"),
         ("3  Interval construction", f"consecutive records, node step = 1\\n{int(P.modelling_samples):,} samples (0 < Δt ≤ 30 min)"),
         ("4  Chronological split", "train: Month_1 + Month_2\\ntest: Month_3 (never used for tuning)"),
         ("5  Features (train-only fit)", "segment mean, previous interval, hour, node, direction, folder, run position"),
         ("6  Models + validation", "5 regressors, tuned: fit Month_1 → validate Month_2"),
         ("7  Evaluation", "MAE, RMSE, R² vs 3 baselines on Month_3")]
fig, ax = plt.subplots(figsize=(5, 4.2)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(-0.15, 7 * 1.3)
for i, (t, d) in enumerate(steps):
    y = (6 - i) * 1.3
    ax.add_patch(FancyBboxPatch((0.4, y), 9.2, 0.95, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#e8edf5", ec="#1f3a68", lw=1))
    ax.text(0.6, y + 0.66, t.replace("\\n", "\n"), fontsize=8, fontweight="bold", va="center", color="#1f3a68")
    ax.text(0.6, y + 0.27, d.replace("\\n", " | "), fontsize=6.6, va="center")
    if i < 6: ax.annotate("", xy=(5, y - 0.33), xytext=(5, y), arrowprops=dict(arrowstyle="-|>", color="#1f3a68"))
ax.set_title("Methodology pipeline")
save("fig7_pipeline")
