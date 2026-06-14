"""第 10 章：代码生成目标、性能分析和 C++ standalone 入口。"""

from pathlib import Path
import shutil
import sys
import time

from brian2 import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(10)
prefs.codegen.target = "numpy"

neurons = NeuronGroup(
    1000,
    "dv/dt = (1.1-v)/(10*ms) : 1",
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)
spikes = SpikeMonitor(neurons)
network = Network(neurons, spikes)

started = time.perf_counter()
network.run(100 * ms, profile=True)
elapsed = time.perf_counter() - started

compiler = shutil.which("cl") or shutil.which("g++")
report = [
    f"NumPy target wall time: {elapsed:.3f} s",
    f"Spikes: {spikes.num_spikes}",
    f"C++ compiler: {compiler or 'not found'}",
    "",
    "Acceleration path:",
    "1. Prototype with prefs.codegen.target = 'numpy'.",
    "2. Install a compatible compiler and try target = 'cython'.",
    "3. For large fixed experiments, call set_device('cpp_standalone').",
    "4. Build outside a cloud-synced or unusual-character path when compiler tools object.",
    "",
    str(profiling_summary(network, show=5)),
]
text = "\n".join(report)
print(text)
output_path("10_codegen_performance.txt").write_text(text, encoding="utf-8")
