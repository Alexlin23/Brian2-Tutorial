"""第 10 章：代码生成目标、性能分析和 C++ standalone 入口。

完整讲解见 tutorials/10_codegen_performance.md。
"""

from pathlib import Path
import shutil
import sys
import time

from brian2 import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(10)

# NumPy 目标启动快、无需编译器，适合开发和调试。
# 同一个 Brian2 模型以后可以切换到 Cython 或 C++ standalone 加速。
prefs.codegen.target = "numpy"

# 这里故意建立 1000 个相同神经元，让性能报告有可测量的工作量。
neurons = NeuronGroup(
    1000,
    "dv/dt = (1.1-v)/(10*ms) : 1",
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)
spikes = SpikeMonitor(neurons)
network = Network(neurons, spikes)

# perf_counter 测量真实经过时间；profile=True 还会让 Brian2
# 分别统计各个内部对象花费的时间。
started = time.perf_counter()
network.run(100 * ms, profile=True)
elapsed = time.perf_counter() - started

# Windows 常见编译器是 cl，其他环境常见 g++。
# 检测不到编译器不影响当前 NumPy 示例，只影响后续加速路线。
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

# 保存文本报告，便于比较改变神经元数量或代码生成目标后的性能。
output_path("10_codegen_performance.txt").write_text(text, encoding="utf-8")
