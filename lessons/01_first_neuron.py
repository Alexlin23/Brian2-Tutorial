"""第 1 章：单位、微分方程、阈值、重置和记录。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(1)
defaultclock.dt = 0.1 * ms

tau = 10 * ms
neurons = NeuronGroup(
    1,
    "dv/dt = (1.1 - v)/tau : 1",
    threshold="v > 1",
    reset="v = 0",
    refractory=2 * ms,
    method="exact",
)
state = StateMonitor(neurons, "v", record=True)
spikes = SpikeMonitor(neurons)

run(100 * ms)

print("脉冲数量:", spikes.count[0])
print("脉冲时刻:", spikes.t[:])

plt.plot(state.t / ms, state.v[0])
plt.xlabel("time (ms)")
plt.ylabel("v")
plt.title("Leaky integrate-and-fire neuron")
plt.tight_layout()
plt.savefig(output_path("01_first_neuron.png"))
