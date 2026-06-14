"""综合项目：带外部输入的兴奋/抑制平衡网络。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(42)

N_E = 160
N_I = 40
tau = 20 * ms

neurons = NeuronGroup(
    N_E + N_I,
    "dv/dt = -v/tau : 1",
    threshold="v > 1",
    reset="v = 0",
    refractory=2 * ms,
    method="exact",
)
neurons.v = "rand()"
excitatory = neurons[:N_E]
inhibitory = neurons[N_E:]

external = PoissonInput(neurons, "v", N=100, rate=12 * Hz, weight=0.05)

exc_synapses = Synapses(excitatory, neurons, on_pre="v_post += 0.06")
exc_synapses.connect(p=0.08)
exc_synapses.delay = 1.5 * ms

inh_synapses = Synapses(inhibitory, neurons, on_pre="v_post -= 0.25")
inh_synapses.connect(p=0.08)
inh_synapses.delay = 0.8 * ms

spikes = SpikeMonitor(neurons)
rate_e = PopulationRateMonitor(excitatory)
rate_i = PopulationRateMonitor(inhibitory)
run(500 * ms)

mean_rate_e = spikes.count[:N_E].sum() / N_E / (0.5 * second)
mean_rate_i = spikes.count[N_E:].sum() / N_I / (0.5 * second)
print("兴奋性群体平均放电率:", mean_rate_e)
print("抑制性群体平均放电率:", mean_rate_i)
print("兴奋性连接数:", len(exc_synapses))
print("抑制性连接数:", len(inh_synapses))

fig, axes = plt.subplots(2, 1, sharex=True)
axes[0].scatter(spikes.t / ms, spikes.i, s=2)
axes[0].axhline(N_E, color="tab:red", linestyle="--")
axes[0].set_ylabel("neuron index")
axes[1].plot(rate_e.t / ms, rate_e.smooth_rate(width=5 * ms) / Hz, label="E")
axes[1].plot(rate_i.t / ms, rate_i.smooth_rate(width=5 * ms) / Hz, label="I")
axes[1].set_xlabel("time (ms)")
axes[1].set_ylabel("rate (Hz)")
axes[1].legend()
fig.suptitle("Excitatory-inhibitory balanced network")
fig.tight_layout()
fig.savefig(output_path("project_balanced_network.png"))
