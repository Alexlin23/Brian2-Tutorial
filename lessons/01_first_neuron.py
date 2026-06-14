"""第 1 章：单位、微分方程、阈值、重置和记录。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


# 清除 Brian2 在当前进程中此前收集的对象，保证本章可重复运行。
start_scope()

# 固定随机种子是神经仿真实验的好习惯。本章没有随机项，但先养成习惯。
seed(1)

# 仿真每 0.1 ms 更新一次。时间步越小通常越精确，但计算量越大。
defaultclock.dt = 0.1 * ms

# 膜电位以 10 ms 的时间常数向 1.1 靠近。
# 这里的 v 是无量纲变量，tau 则必须带有时间单位。
tau = 10 * ms
neurons = NeuronGroup(
    # 只创建一个神经元，方便先看懂完整的放电循环。
    1,
    # dv/dt 描述连续变化；": 1" 声明 v 是无量纲量。
    "dv/dt = (1.1 - v)/tau : 1",
    # v 越过 1 时记录一次脉冲，然后把 v 重置为 0。
    threshold="v > 1",
    reset="v = 0",
    # 放电后的 2 ms 内不允许再次触发阈值。
    refractory=2 * ms,
    # 这个线性方程有解析更新式，因此可使用 exact 方法。
    method="exact",
)

# StateMonitor 记录连续状态轨迹；SpikeMonitor 只记录离散放电事件。
# record=True 表示记录这个群体中的全部神经元。
state = StateMonitor(neurons, "v", record=True)
spikes = SpikeMonitor(neurons)

# 创建对象只是定义实验，run() 才真正推进仿真时钟。
run(100 * ms)

print("脉冲数量:", spikes.count[0])
print("脉冲时刻:", spikes.t[:])

# 横轴除以 ms 后变成普通数值，便于 Matplotlib 使用毫秒作刻度。
plt.plot(state.t / ms, state.v[0])
plt.xlabel("time (ms)")
plt.ylabel("v")
plt.title("Leaky integrate-and-fire neuron")
plt.tight_layout()
plt.savefig(output_path("01_first_neuron.png"))
