"""第 3 章：突触变量、连接索引、突触事件和延迟。

完整讲解见 tutorials/03_synapses.md。
"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(3)

# SpikeGeneratorGroup 用明确的“神经元编号 + 时刻”制造可控脉冲。
# 这里 5 个源神经元依次在 5、10、15、20、25 ms 放电。
source = SpikeGeneratorGroup(
    5,
    indices=[0, 1, 2, 3, 4],
    times=[5, 10, 15, 20, 25] * ms,
)

# 靶神经元没有外部驱动，v 只会按 8 ms 时间常数衰减。
target = NeuronGroup(5, "dv/dt = -v/(8*ms) : 1", method="exact")

# w 是每条突触自己的状态变量。
# on_pre 在突触前神经元放电并经过 delay 后执行；
# v_post 指向突触后神经元的 v。
synapses = Synapses(source, target, "w : 1", on_pre="v_post += w")

# i 是突触前编号，j 是突触后编号。两个等长列表建立五条一对一连接。
synapses.connect(i=[0, 1, 2, 3, 4], j=[0, 1, 2, 3, 4])

# Brian2 会为每条突触计算表达式，所以权重和延迟随源编号增大。
synapses.w = "0.2 + 0.1*i"
synapses.delay = "i*ms"

# 记录全部五个靶神经元，比较权重和延迟如何改变响应高度与出现时刻。
state = StateMonitor(target, "v", record=True)
run(50 * ms)

print("连接数量:", len(synapses))
print("权重:", synapses.w[:])
print("延迟:", synapses.delay[:])

for index in range(5):
    plt.plot(state.t / ms, state.v[index], label=f"target {index}")
plt.xlabel("time (ms)")
plt.ylabel("v")
plt.legend()
plt.title("Synaptic weights and delays")
plt.tight_layout()
plt.savefig(output_path("03_synapses.png"))
