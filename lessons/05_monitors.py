"""第 5 章：状态、脉冲、脉冲时刻状态和群体放电率记录。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(5)

neurons = NeuronGroup(
    50,
    # randn() 每次更新都会产生标准正态随机数，因此每个神经元的
    # 瞬时驱动力持续波动。这里用 Euler 方法逐时间步计算。
    "dv/dt = (1.05 + 0.15*randn() - v)/(10*ms) : 1",
    threshold="v > 1",
    reset="v = 0",
    method="euler",
)
neurons.v = "rand()"

# StateMonitor：按时间记录指定连续变量，这里只选 0、1、2 号神经元。
state = StateMonitor(neurons, "v", record=[0, 1, 2])

# SpikeMonitor：记录放电时刻和编号。variables="v" 还会保存每次
# 触发阈值时的 v，适合分析“事件发生瞬间”的状态。
spikes = SpikeMonitor(neurons, variables="v")

# PopulationRateMonitor：把整个群体的脉冲换算为随时间变化的放电率。
rate = PopulationRateMonitor(neurons)
run(200 * ms)

# 原始瞬时群体率很尖锐，用 5 ms 高斯窗平滑后更容易观察趋势。
smoothed = rate.smooth_rate(window="gaussian", width=5 * ms)
print("记录到的脉冲数:", spikes.num_spikes)
print("各神经元脉冲计数前 10 项:", spikes.count[:10])

# 三层图分别回答：膜电位怎样变化、谁在何时放电、群体总体多活跃。
fig, axes = plt.subplots(3, 1, sharex=True)
for index in range(3):
    axes[0].plot(state.t / ms, state.v[index], label=str(index))
axes[0].set_ylabel("v")
axes[0].legend()
axes[1].scatter(spikes.t / ms, spikes.i, s=4)
axes[1].set_ylabel("index")
axes[2].plot(rate.t / ms, smoothed / Hz)
axes[2].set_ylabel("rate (Hz)")
axes[2].set_xlabel("time (ms)")
fig.suptitle("State, spike, and population rate monitors")
fig.tight_layout()
fig.savefig(output_path("05_monitors.png"))
