"""第 5 章：状态、脉冲、脉冲时刻状态和群体放电率记录。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(5)

neurons = NeuronGroup(
    50,
    "dv/dt = (1.05 + 0.15*randn() - v)/(10*ms) : 1",
    threshold="v > 1",
    reset="v = 0",
    method="euler",
)
neurons.v = "rand()"

state = StateMonitor(neurons, "v", record=[0, 1, 2])
spikes = SpikeMonitor(neurons, variables="v")
rate = PopulationRateMonitor(neurons)
run(200 * ms)

smoothed = rate.smooth_rate(window="gaussian", width=5 * ms)
print("记录到的脉冲数:", spikes.num_spikes)
print("各神经元脉冲计数前 10 项:", spikes.count[:10])

fig, axes = plt.subplots(3, 1, sharex=True)
for index in range(3):
    axes[0].plot(state.t / ms, state.v[index], label=str(index))
axes[0].set_ylabel("v")
axes[0].legend()
axes[1].scatter(spikes.t / ms, spikes.i, s=4)
axes[1].set_ylabel("index")
axes[2].plot(rate.t / ms, smoothed / Hz)
axes[2].set_ylabel("rate (Hz)")
axes[2].set_xlabel("time (ms)")
fig.suptitle("State, spike, and population rate monitors")
fig.tight_layout()
fig.savefig(output_path("05_monitors.png"))
