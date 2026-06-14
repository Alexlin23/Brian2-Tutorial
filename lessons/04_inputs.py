"""第 4 章：PoissonGroup、PoissonInput、SpikeGeneratorGroup 和 TimedArray。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(4)

stimulus = TimedArray([0.1, 0.9, 0.2, 1.1, 0.1], dt=20 * ms)
neurons = NeuronGroup(
    20,
    """
    dv/dt = (-v + stimulus(t))/(10*ms) : 1
    """,
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)

poisson_input = PoissonInput(
    neurons,
    target_var="v",
    N=20,
    rate=10 * Hz,
    weight=0.04,
)

cue = SpikeGeneratorGroup(1, indices=[0, 0], times=[35, 75] * ms)
cue_synapse = Synapses(cue, neurons, on_pre="v_post += 0.3")
cue_synapse.connect()

background = PoissonGroup(5, rates="5*Hz + i*2*Hz")
background_synapse = Synapses(background, neurons, on_pre="v_post += 0.05")
background_synapse.connect(p=0.25)

spikes = SpikeMonitor(neurons)
state = StateMonitor(neurons, "v", record=[0])
run(100 * ms)

print("总脉冲数:", spikes.num_spikes)
print("TimedArray 在 45 ms 的值:", stimulus(45 * ms))

fig, axes = plt.subplots(2, 1, sharex=True)
axes[0].plot(state.t / ms, state.v[0])
axes[0].set_ylabel("v[0]")
axes[1].scatter(spikes.t / ms, spikes.i, s=6)
axes[1].set_xlabel("time (ms)")
axes[1].set_ylabel("index")
fig.suptitle("Four input mechanisms")
fig.tight_layout()
fig.savefig(output_path("04_inputs.png"))
