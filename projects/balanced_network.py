"""综合项目：带外部输入的兴奋/抑制平衡网络。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(42)

# 将 200 个神经元按 4:1 分为兴奋性和抑制性群体。
N_E = 160
N_I = 40
tau = 20 * ms

# 全部神经元使用同一个漏积分模型。它们自身只会衰减，
# 必须依靠外部输入和循环突触把 v 推过阈值。
neurons = NeuronGroup(
    N_E + N_I,
    "dv/dt = -v/tau : 1",
    threshold="v > 1",
    reset="v = 0",
    refractory=2 * ms,
    method="exact",
)
neurons.v = "rand()"

# 切片不会复制神经元，而是创建指向原群体的两个子组视图。
excitatory = neurons[:N_E]
inhibitory = neurons[N_E:]

# 每个神经元接收 100 路独立泊松输入，提供维持网络活动的外部驱动。
external = PoissonInput(neurons, "v", N=100, rate=12 * Hz, weight=0.05)

# 兴奋性突触使 v 增加。p=0.08 表示每个可能连接以 8% 概率建立。
# 1.5 ms 延迟近似脉冲沿轴突传播和突触传递所需时间。
exc_synapses = Synapses(excitatory, neurons, on_pre="v_post += 0.06")
exc_synapses.connect(p=0.08)
exc_synapses.delay = 1.5 * ms

# 抑制性突触使 v 降低，单次作用强于兴奋性突触。
# “平衡”不是两类连接数量相等，而是总体兴奋与总体抑制动态制衡。
inh_synapses = Synapses(inhibitory, neurons, on_pre="v_post -= 0.25")
inh_synapses.connect(p=0.08)
inh_synapses.delay = 0.8 * ms

# SpikeMonitor 用于栅格图和逐神经元计数；
# 两个 PopulationRateMonitor 分别观察 E/I 群体的瞬时活跃程度。
spikes = SpikeMonitor(neurons)
rate_e = PopulationRateMonitor(excitatory)
rate_i = PopulationRateMonitor(inhibitory)
run(500 * ms)

# 总脉冲数 / 神经元数 / 仿真时长 = 每个神经元的平均放电率。
mean_rate_e = spikes.count[:N_E].sum() / N_E / (0.5 * second)
mean_rate_i = spikes.count[N_E:].sum() / N_I / (0.5 * second)
print("兴奋性群体平均放电率:", mean_rate_e)
print("抑制性群体平均放电率:", mean_rate_i)
print("兴奋性连接数:", len(exc_synapses))
print("抑制性连接数:", len(inh_synapses))

# 上图是单个脉冲的时空分布，红线分隔 E/I 神经元；
# 下图是两个群体经 5 ms 窗平滑后的总体放电率。
fig, axes = plt.subplots(2, 1, sharex=True)
axes[0].scatter(spikes.t / ms, spikes.i, s=2)
axes[0].axhline(N_E, color="tab:red", linestyle="--")
axes[0].set_ylabel("neuron index")
axes[1].plot(rate_e.t / ms, rate_e.smooth_rate(width=5 * ms) / Hz, label="E")
axes[1].plot(rate_i.t / ms, rate_i.smooth_rate(width=5 * ms) / Hz, label="I")
axes[1].set_xlabel("time (ms)")
axes[1].set_ylabel("rate (Hz)")
axes[1].legend()
fig.suptitle("Excitatory-inhibitory balanced network")
fig.tight_layout()
fig.savefig(output_path("project_balanced_network.png"))
