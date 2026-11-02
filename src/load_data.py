"""Recursively read every Excel/CSV workbook under data/ and keep month, route-group and day."""
import re, warnings
import pandas as pd
from config import DATA_DIR, TAB
warnings.filterwarnings("ignore")

def load_raw():
    rows, errors = [], []
    files = sorted(list(DATA_DIR.rglob("*.xlsx")) + list(DATA_DIR.rglob("*.csv")))
    for f in files:
        try:
            d = pd.read_excel(f) if f.suffix == ".xlsx" else pd.read_csv(f)
            d = d.drop(columns=[c for c in d.columns if str(c).startswith("Unnamed")], errors="ignore")
            rel = f.relative_to(DATA_DIR).parts          # Month_x / group / DayN.xlsx
            d["month"], d["group"] = rel[0], rel[1]
            d["day"] = int(re.findall(r"\d+", rel[2])[0])
            d["file"] = "/".join(rel)
            d["row_in_file"] = range(len(d))
            rows.append(d)
        except Exception as e:                            # report, never silently skip
            errors.append((str(f), repr(e)))
    df = pd.concat(rows, ignore_index=True)
    pd.DataFrame(errors, columns=["file", "error"]).to_csv(TAB / "unreadable_files.csv", index=False)
    print(f"Read {len(files)-len(errors)} files, {len(errors)} unreadable, {len(df):,} rows")
    return df

if __name__ == "__main__":
    load_raw().to_pickle(DATA_DIR / "raw.pkl")
