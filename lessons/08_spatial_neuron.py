"""第 8 章：SpatialNeuron 多区室电缆模型。

完整讲解见 tutorials/08_spatial_neuron.md。
"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()

# 把一根长 200 um、直径 2 um 的圆柱形神经突分成 20 个区室。
# 区室越多，空间离散越细，但计算量也越大。
morphology = Cylinder(length=200 * um, diameter=2 * um, n=20)

# gL 是单位膜面积的漏电导，EL 是漏电流的反转电位。
gL = 1e-4 * siemens / cm**2
EL = -70 * mV

# SpatialNeuron 除了每个区室的膜方程，还会自动计算相邻区室之间
# 由轴向电阻产生的电流传播。
neuron = SpatialNeuron(
    morphology=morphology,
    # Im 必须是单位面积膜电流；I 使用 (point current)，表示把一个
    # 总电流注入指定区室，Brian2 会负责换算到该区室的面积。
    model="""
    Im = gL*(EL-v) : amp/meter**2
    I : amp (point current)
    """,
    # Cm 是比膜电容，Ri 是细胞内部的轴向电阻率。
    Cm=1 * ufarad / cm**2,
    Ri=150 * ohm * cm,
    method="exponential_euler",
)

# 所有区室从漏电反转电位开始，只向 0 号区室注入 0.1 nA。
neuron.v = EL
neuron.I[0] = 0.1 * nA

# 从注入端到远端选取四个位置，观察电压传播时的衰减和延迟。
state = StateMonitor(neuron, "v", record=[0, 5, 10, 19])
run(20 * ms)

# StateMonitor 的行顺序对应 record 列表的顺序，而不是区室编号本身。
for row, compartment in enumerate([0, 5, 10, 19]):
    plt.plot(state.t / ms, state.v[row] / mV, label=f"compartment {compartment}")
plt.xlabel("time (ms)")
plt.ylabel("membrane potential (mV)")
plt.legend()
plt.title("Passive cable response")
plt.tight_layout()
plt.savefig(output_path("08_spatial_neuron.png"))

print("区室数量:", len(neuron))
print("末端电压:", neuron.v[[0, 5, 10, 19]])
