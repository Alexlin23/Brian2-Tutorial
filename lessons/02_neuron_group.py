"""第 2 章：神经元群体、噪声、异质参数和子组。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(2)

N = 100
tau = 10 * ms
sigma = 0.18
equations = """
dv/dt = (mu - v)/tau + sigma*xi/sqrt(tau) : 1 (unless refractory)
mu : 1
"""

neurons = NeuronGroup(
    N,
    equations,
    threshold="v > 1",
    reset="v = 0",
    refractory=2 * ms,
    method="euler",
)
neurons.v = "rand()"
neurons[:50].mu = 0.9
neurons[50:].mu = 1.1

spikes = SpikeMonitor(neurons)
run(200 * ms)

print("低驱动组脉冲数:", sum(spikes.count[:50]))
print("高驱动组脉冲数:", sum(spikes.count[50:]))

plt.scatter(spikes.t / ms, spikes.i, s=4)
plt.axhline(50, color="tab:red", linestyle="--")
plt.xlabel("time (ms)")
plt.ylabel("neuron index")
plt.title("Heterogeneous noisy neuron groups")
plt.tight_layout()
plt.savefig(output_path("02_neuron_group.png"))
