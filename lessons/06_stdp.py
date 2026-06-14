"""第 6 章：事件驱动突触变量和经典成对 STDP。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(6)

N = 100
taupre = taupost = 20 * ms
Apre = 0.01
Apost = -Apre * 1.05
wmax = 0.08

inputs = PoissonGroup(N, rates=15 * Hz)
target = NeuronGroup(
    1,
    "dv/dt = -v/(10*ms) : 1",
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)

synapses = Synapses(
    inputs,
    target,
    """
    w : 1
    dapre/dt = -apre/taupre : 1 (event-driven)
    dapost/dt = -apost/taupost : 1 (event-driven)
    """,
    on_pre="""
    v_post += w
    apre += Apre
    w = clip(w + apost, 0, wmax)
    """,
    on_post="""
    apost += Apost
    w = clip(w + apre, 0, wmax)
    """,
)
synapses.connect()
synapses.w = "rand()*wmax"
initial_weights = synapses.w[:].copy()

target_spikes = SpikeMonitor(target)
run(1 * second)

print("目标神经元脉冲数:", target_spikes.num_spikes)
print("平均权重: %.4f -> %.4f" % (initial_weights.mean(), mean(synapses.w[:])))

plt.hist(initial_weights, bins=15, alpha=0.6, label="before")
plt.hist(synapses.w[:], bins=15, alpha=0.6, label="after")
plt.xlabel("weight")
plt.ylabel("count")
plt.legend()
plt.title("STDP weight distribution")
plt.tight_layout()
plt.savefig(output_path("06_stdp.png"))
