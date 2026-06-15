"""第 7 章：显式 Network、调度、run_regularly、store 和 restore。

完整讲解见 tutorials/07_network_control.md。
"""

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

# (shared) 让整个群体共用一个 drive，而不是每个神经元各存一份。
neurons.drive = 1.05

# run_regularly 会在仿真期间每 2 ms 执行一次字符串语句。
# when="start" 表示它发生在该时间步其他更新之前。
neurons.run_regularly("v += 0.02*rand()", dt=2 * ms, when="start")
spikes = SpikeMonitor(neurons)
state = StateMonitor(neurons, "v", record=[0])

# 前几章依赖 Brian2 自动收集对象，这里显式列出网络成员。
# 显式 Network 更适合复杂实验，因为运行、保存和分析对象都很明确。
network = Network(neurons, spikes, state)

# store() 保存所有网络状态、时钟和监视器数据，形成实验共同起点。
network.store("initial")
network.run(50 * ms, profile=True)
first_count = spikes.num_spikes

# restore() 默认不会恢复随机数生成器状态。这里显式设为 True，
# 让两次运行使用相同的随机扰动序列，从而只比较 drive 的影响。
network.restore("initial", restore_random_state=True)
neurons.drive = 1.25
network.run(50 * ms, profile=True)
second_count = spikes.num_spikes

print("低驱动脉冲数:", first_count)
print("恢复后高驱动脉冲数:", second_count)

# profile=True 收集各 Brian2 对象的耗时，profiling_summary 用于找性能瓶颈。
print(profiling_summary(network, show=5))

# restore 后监视器也回到保存点，所以图中只包含第二次高驱动实验。
plt.plot(state.t / ms, state.v[0])
plt.xlabel("time (ms)")
plt.ylabel("v[0]")
plt.title("Explicit Network after restore")
plt.tight_layout()
plt.savefig(output_path("07_network_control.png"))
