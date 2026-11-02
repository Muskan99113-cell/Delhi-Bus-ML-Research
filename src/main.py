"""Run the whole project end to end.
    python src/main.py              # full run (retrains all models; the MLP stage takes ~10+ min on one core)
    python src/main.py --skip-train # reuse saved model results/predictions, regenerate everything else"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import TAB
from load_data import load_raw
from preprocess import clean, build_intervals
import eda

def step(msg): print(f"\n=== {msg} ({time.strftime('%H:%M:%S')})", flush=True)

if __name__ == "__main__":
    skip = "--skip-train" in sys.argv
    step("1. Load all workbooks"); raw = load_raw()
    step("2. Clean + build intervals"); c, n_dup = clean(raw); full, pair = build_intervals(c)
    step("3. EDA: dataset_profile.csv + figures 1-6"); print(eda.profile(raw, c, n_dup, full, pair)); eda.figures(raw, c, full, pair)
    if skip and (TAB / "model_comparison.csv").exists() and (TAB / "test_predictions.pkl").exists():
        step("4. Training skipped (--skip-train): using saved results")
    else:
        step("4. Train + evaluate models"); import train_models; print(train_models.run(pair)[0].round(4).to_string())
    step("5. Result figures"); import runpy
    for mod in ("make_result_figures", "make_pipeline_figure"): runpy.run_module(mod, run_name="__main__")
    step("6. Extra analysis (ablation, importance, subgroup errors) + paper statistics")
    for mod in ("extra_analysis", "paper_stats"): runpy.run_module(mod, run_name="__main__")
    step("7. Build paper (PDF + DOCX)")
    import build_pdf; print("PDF pages:", build_pdf.build(str(Path(TAB).parent / "paper.pdf")))
    try:
        import build_docx; build_docx.build(str(Path(TAB).parent / "paper.docx"))
    except ImportError: print("build_docx not found; skipped")
    step("Done. See outputs/")
