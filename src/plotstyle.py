import matplotlib.pyplot as plt
from config import FIG
def setup():
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "legend.fontsize": 7, "figure.dpi": 150, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
def save(name):
    plt.tight_layout(); plt.savefig(FIG / f"{name}.png", dpi=300); plt.close()
