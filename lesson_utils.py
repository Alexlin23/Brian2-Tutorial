from pathlib import Path

import matplotlib
from brian2 import prefs

matplotlib.use("Agg")
prefs.codegen.target = "numpy"

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def output_path(filename):
    return OUTPUT_DIR / filename
