"""第 7 章：显式 Network、调度、run_regularly、store 和 restore。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(7)

neurons = NeuronGroup(
    10,
    """
    dv/dt = (drive-v)/(10*ms) : 1
    drive : 1 (shared)
    """,
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)
neurons.drive = 1.05
neurons.run_regularly("v += 0.02*rand()", dt=2 * ms, when="start")
spikes = SpikeMonitor(neurons)
state = StateMonitor(neurons, "v", record=[0])

network = Network(neurons, spikes, state)
network.store("initial")
network.run(50 * ms, profile=True)
first_count = spikes.num_spikes

network.restore("initial")
neurons.drive = 1.25
network.run(50 * ms, profile=True)
second_count = spikes.num_spikes

print("低驱动脉冲数:", first_count)
print("恢复后高驱动脉冲数:", second_count)
print(profiling_summary(network, show=5))

plt.plot(state.t / ms, state.v[0])
plt.xlabel("time (ms)")
plt.ylabel("v[0]")
plt.title("Explicit Network after restore")
plt.tight_layout()
plt.savefig(output_path("07_network_control.png"))
