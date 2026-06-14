"""第 9 章：Equations、子表达式、命名空间和自定义事件。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
prefs.codegen.target = "numpy"

tau = 10 * ms
equations = Equations(
    """
    dv/dt = (drive-v)/tau : 1
    energy = v**2 : 1
    drive : 1
    """
)

neurons = NeuronGroup(
    3,
    equations,
    threshold="v > 1",
    reset="v = 0",
    events={"high": "v > 0.8"},
    method="exact",
)
neurons.drive = [0.9, 1.05, 1.2]
neurons.run_on_event("high", "v -= 0.15")

high_events = EventMonitor(neurons, "high", variables=["v", "energy"])
state = StateMonitor(neurons, ["v", "energy"], record=True)
run(60 * ms)

print("自定义 high 事件数量:", high_events.num_events)
print("事件神经元索引前 10 项:", high_events.i[:10])

for index in range(3):
    plt.plot(state.t / ms, state.v[index], label=f"neuron {index}")
plt.xlabel("time (ms)")
plt.ylabel("v")
plt.legend()
plt.title("Custom events and subexpressions")
plt.tight_layout()
plt.savefig(output_path("09_equations_events.png"))
