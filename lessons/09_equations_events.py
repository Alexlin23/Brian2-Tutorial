"""第 9 章：Equations、子表达式、命名空间和自定义事件。

完整讲解见 tutorials/09_equations_events.md。
"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
prefs.codegen.target = "numpy"

tau = 10 * ms

# Equations 对象适合复用、组合或程序化构造方程。
# energy 没有微分方程，是由 v 即时计算的子表达式；
# 它不会作为独立状态被积分。
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
    # 除默认 spike 事件外，再定义一个名为 high 的事件。
    # 每当某个时间步结束时 v > 0.8，该神经元就触发此事件。
    events={"high": "v > 0.8"},
    method="exact",
)

# 三个神经元共享同一方程，但使用不同的恒定驱动力。
neurons.drive = [0.9, 1.05, 1.2]

# high 事件触发时降低 v，相当于加入一个自定义的负反馈动作。
neurons.run_on_event("high", "v -= 0.15")

# EventMonitor 与 SpikeMonitor 类似，但记录指定的自定义事件。
# variables 列表会额外保存事件发生瞬间的 v 和 energy。
high_events = EventMonitor(neurons, "high", variables=["v", "energy"])
state = StateMonitor(neurons, ["v", "energy"], record=True)
run(60 * ms)

print("自定义 high 事件数量:", high_events.num_events)
print("事件神经元索引前 10 项:", high_events.i[:10])

# 比较不同 drive 下，负反馈事件怎样把 v 拉低并形成不同节律。
for index in range(3):
    plt.plot(state.t / ms, state.v[index], label=f"neuron {index}")
plt.xlabel("time (ms)")
plt.ylabel("v")
plt.legend()
plt.title("Custom events and subexpressions")
plt.tight_layout()
plt.savefig(output_path("09_equations_events.png"))
