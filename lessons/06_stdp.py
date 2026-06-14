"""第 6 章：事件驱动突触变量和经典成对 STDP。"""

from pathlib import Path
import sys

from brian2 import *
from matplotlib import pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lesson_utils import output_path


start_scope()
seed(6)

# 100 个独立泊松输入共同连接到一个靶神经元。
N = 100

# apre、apost 是最近一次前/后脉冲留下的“时间痕迹”，
# 都按 20 ms 时间常数衰减。两次脉冲越接近，痕迹绝对值越大。
taupre = taupost = 20 * ms

# 前脉冲痕迹为正，后脉冲痕迹略强且为负。
# 这会使“先前后后”增强、“先后后前”减弱，并略偏向整体抑制增长。
Apre = 0.01
Apost = -Apre * 1.05

# clip() 会把权重限制在 0 到 wmax 之间，防止无限增长或变成负数。
wmax = 0.08

inputs = PoissonGroup(N, rates=15 * Hz)
target = NeuronGroup(
    1,
    "dv/dt = -v/(10*ms) : 1",
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)

# 每条输入突触都有独立的权重 w、前脉冲痕迹 apre 和后脉冲痕迹 apost。
# (event-driven) 表示痕迹只在相关脉冲事件发生时解析更新，
# 无需每个时间步都计算，既准确又高效。
synapses = Synapses(
    inputs,
    target,
    """
    w : 1
    dapre/dt = -apre/taupre : 1 (event-driven)
    dapost/dt = -apost/taupost : 1 (event-driven)
    """,
    # 前神经元放电时：
    # 1. 当前权重推动靶神经元；
    # 2. 增加前脉冲痕迹；
    # 3. 用此前留下的负 apost 调整权重。
    on_pre="""
    v_post += w
    apre += Apre
    w = clip(w + apost, 0, wmax)
    """,
    # 靶神经元放电时，所有入突触都增加后脉冲痕迹，
    # 再用各自残留的正 apre 调整权重。
    on_post="""
    apost += Apost
    w = clip(w + apre, 0, wmax)
    """,
)
synapses.connect()

# 每条突触独立随机初始化，保存副本后才能比较学习前后的分布。
synapses.w = "rand()*wmax"
initial_weights = synapses.w[:].copy()

target_spikes = SpikeMonitor(target)
run(1 * second)

print("目标神经元脉冲数:", target_spikes.num_spikes)
print("平均权重: %.4f -> %.4f" % (initial_weights.mean(), mean(synapses.w[:])))

# 直方图不追踪单条突触，而是观察整个权重群体是否向 0 或 wmax 移动。
plt.hist(initial_weights, bins=15, alpha=0.6, label="before")
plt.hist(synapses.w[:], bins=15, alpha=0.6, label="after")
plt.xlabel("weight")
plt.ylabel("count")
plt.legend()
plt.title("STDP weight distribution")
plt.tight_layout()
plt.savefig(output_path("06_stdp.png"))
