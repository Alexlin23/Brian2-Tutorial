"""第 3 章：突触变量、连接索引、突触事件和延迟。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(3)

source = SpikeGeneratorGroup(
    5,
    indices=[0, 1, 2, 3, 4],
    times=[5, 10, 15, 20, 25] * ms,
)
target = NeuronGroup(5, "dv/dt = -v/(8*ms) : 1", method="exact")

synapses = Synapses(source, target, "w : 1", on_pre="v_post += w")
synapses.connect(i=[0, 1, 2, 3, 4], j=[0, 1, 2, 3, 4])
synapses.w = "0.2 + 0.1*i"
synapses.delay = "i*ms"

state = StateMonitor(target, "v", record=True)
run(50 * ms)

print("连接数量:", len(synapses))
print("权重:", synapses.w[:])
print("延迟:", synapses.delay[:])

for index in range(5):
    plt.plot(state.t / ms, state.v[index], label=f"target {index}")
plt.xlabel("time (ms)")
plt.ylabel("v")
plt.legend()
plt.title("Synaptic weights and delays")
plt.tight_layout()
plt.savefig(output_path("03_synapses.png"))
