"""Shared configuration for the Delhi city-bus interval-prediction project."""
from pathlib import Path
SEED = 42
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"          # place Month_1, Month_2, Month_3 folders (unzipped) here
OUT = ROOT / "outputs"
FIG = OUT / "figures"
TAB = OUT / "tables"
for p in (FIG, TAB):
    p.mkdir(parents=True, exist_ok=True)
MAX_VALID_INTERVAL_S = 1800   # intervals above 30 min between adjacent nodes treated as non-travel gaps
TRAIN_MONTHS = ["Month_1", "Month_2"]
TEST_MONTHS = ["Month_3"]
