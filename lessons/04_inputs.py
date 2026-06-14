"""第 4 章：PoissonGroup、PoissonInput、SpikeGeneratorGroup 和 TimedArray。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(4)

# TimedArray 是分段恒定的时间函数。每 20 ms 取下一个值，
# 因而本例依次提供弱、强、弱、更强、弱的公共驱动。
stimulus = TimedArray([0.1, 0.9, 0.2, 1.1, 0.1], dt=20 * ms)

# stimulus(t) 在方程中像普通函数一样按当前仿真时刻取值。
neurons = NeuronGroup(
    20,
    """
    dv/dt = (-v + stimulus(t))/(10*ms) : 1
    """,
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)

# PoissonInput 不显式创建 20 x 20 条突触，而是高效地为每个
# 靶神经元叠加 20 路、频率 10 Hz、单次增量 0.04 的泊松输入。
poisson_input = PoissonInput(
    neurons,
    target_var="v",
    N=20,
    rate=10 * Hz,
    weight=0.04,
)

# SpikeGeneratorGroup 适合已知准确时刻的实验提示信号。
# connect() 不给条件时，会把这个单一提示源连接到全部靶神经元。
cue = SpikeGeneratorGroup(1, indices=[0, 0], times=[35, 75] * ms)
cue_synapse = Synapses(cue, neurons, on_pre="v_post += 0.3")
cue_synapse.connect()

# PoissonGroup 创建真正会随机放电的源神经元。每个源的频率随 i 增大，
# 再以 25% 概率连接到靶群体，展示稀疏随机背景网络。
background = PoissonGroup(5, rates="5*Hz + i*2*Hz")
background_synapse = Synapses(background, neurons, on_pre="v_post += 0.05")
background_synapse.connect(p=0.25)

# 记录所有脉冲，但只记录 0 号神经元的连续 v，控制数据量。
spikes = SpikeMonitor(neurons)
state = StateMonitor(neurons, "v", record=[0])
run(100 * ms)

print("总脉冲数:", spikes.num_spikes)
# 45 ms 落在第三个 20 ms 区间，因此这里应读到 0.2。
print("TimedArray 在 45 ms 的值:", stimulus(45 * ms))

# 上图看单个神经元怎样整合输入，下图看整个群体何时放电。
fig, axes = plt.subplots(2, 1, sharex=True)
axes[0].plot(state.t / ms, state.v[0])
axes[0].set_ylabel("v[0]")
axes[1].scatter(spikes.t / ms, spikes.i, s=6)
axes[1].set_xlabel("time (ms)")
axes[1].set_ylabel("index")
fig.suptitle("Four input mechanisms")
fig.tight_layout()
fig.savefig(output_path("04_inputs.png"))
