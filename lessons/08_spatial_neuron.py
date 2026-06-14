"""第 8 章：SpatialNeuron 多区室电缆模型。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()

morphology = Cylinder(length=200 * um, diameter=2 * um, n=20)
gL = 1e-4 * siemens / cm**2
EL = -70 * mV

neuron = SpatialNeuron(
    morphology=morphology,
    model="""
    Im = gL*(EL-v) : amp/meter**2
    I : amp (point current)
    """,
    Cm=1 * ufarad / cm**2,
    Ri=150 * ohm * cm,
    method="exponential_euler",
)
neuron.v = EL
neuron.I[0] = 0.1 * nA

state = StateMonitor(neuron, "v", record=[0, 5, 10, 19])
run(20 * ms)

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
