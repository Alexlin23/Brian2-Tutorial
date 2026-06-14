"""第 2 章：神经元群体、噪声、异质参数和子组。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(2)

# 用 100 个神经元观察同一模型在不同参数和噪声下的群体差异。
N = 100
tau = 10 * ms
sigma = 0.18

# mu 决定平均驱动力，-v/tau 使状态向 mu 回落。
# xi 是 Brian2 提供的白噪声，量纲为 1/sqrt(second)；
# 除以 sqrt(tau) 后，整个噪声项与 dv/dt 的单位一致。
# 第二行声明 mu 是每个神经元都可以拥有不同值的无量纲参数。
equations = """
dv/dt = (mu - v)/tau + sigma*xi/sqrt(tau) : 1 (unless refractory)
mu : 1
"""

neurons = NeuronGroup(
    N,
    equations,
    threshold="v > 1",
    reset="v = 0",
    refractory=2 * ms,
    # 含白噪声的随机微分方程不能使用 exact，这里用 Euler 离散积分。
    method="euler",
)

# 字符串赋值会对每个神经元分别计算 rand()，产生不同初始状态。
neurons.v = "rand()"

# 切片得到 NeuronGroup 的子组。前后两组只在平均驱动力 mu 上不同。
neurons[:50].mu = 0.9
neurons[50:].mu = 1.1

spikes = SpikeMonitor(neurons)
run(200 * ms)

print("低驱动组脉冲数:", sum(spikes.count[:50]))
print("高驱动组脉冲数:", sum(spikes.count[50:]))

# 栅格图中每个点代表一次脉冲：横轴是时刻，纵轴是神经元编号。
# 红色虚线把低驱动组和高驱动组分开。
plt.scatter(spikes.t / ms, spikes.i, s=4)
plt.axhline(50, color="tab:red", linestyle="--")
plt.xlabel("time (ms)")
plt.ylabel("neuron index")
plt.title("Heterogeneous noisy neuron groups")
plt.tight_layout()
plt.savefig(output_path("02_neuron_group.png"))
