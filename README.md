# Brian2 完整中文教程

这是一套“边运行、边理解”的 Brian2 学习项目。不要急着一次读完。建议每次只学一章，先预测结果，再运行代码，最后修改一个参数观察变化。

## 1. Brian2 是什么

Brian2 是用 Python 描述和模拟脉冲神经网络（SNN）的框架。它的核心特点不是提供固定神经元，而是让你直接写微分方程、阈值、重置和突触事件。Brian2 会检查物理单位，并将模型转换为可执行代码。

它适合：

- 神经元和突触动力学研究
- 生物可信的脉冲神经网络实验
- STDP 等可塑性规则
- 多区室神经元和树突形态
- 小到中等规模的原型验证
- 通过 Cython 或 C++ standalone 加速大型仿真

它不是以反向传播训练深度神经网络为核心的框架。若目标是大规模 GPU 深度学习，PyTorch/JAX 往往更合适；Brian2 的强项是方程透明、单位严格、实验灵活。

## 2. 安装

当前电脑是 Python 3.11，因此本项目锁定 Brian2 2.9.0。Brian2 2.10.1 要求 Python 3.12 或更高。

在 PowerShell 中运行：

```powershell
cd "D:\重要文件\AI相关\模拟智能\Brian2完整教程"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

验证环境：

```powershell
.\.venv\Scripts\python.exe lessons\00_environment.py
```

## 3. 推荐学习顺序

| 顺序 | 文件 | 你会学到什么 |
|---|---|---|
| 0 | `lessons/00_environment.py` | 版本、设备、代码生成环境 |
| 1 | `lessons/01_first_neuron.py` | 单位、方程、阈值、重置、运行 |
| 2 | `lessons/02_neuron_group.py` | 群体、噪声、参数异质性、子组 |
| 3 | `lessons/03_synapses.py` | 突触状态、连接方式、延迟 |
| 4 | `lessons/04_inputs.py` | 泊松、脉冲序列、时变输入 |
| 5 | `lessons/05_monitors.py` | 状态、脉冲、群体放电率 |
| 6 | `lessons/06_stdp.py` | 事件驱动方程和 STDP |
| 7 | `lessons/07_network_control.py` | 显式网络、调度、保存与恢复 |
| 8 | `lessons/08_spatial_neuron.py` | 多区室电缆模型 |
| 9 | `lessons/09_equations_events.py` | 方程对象、子表达式、自定义事件 |
| 10 | `lessons/10_codegen_performance.py` | 代码生成、性能分析、standalone |
| 综合 | `projects/balanced_network.py` | 兴奋/抑制平衡网络 |

运行全部常规示例：

```powershell
.\.venv\Scripts\python.exe run_all.py
```

结果图片会写入 `outputs/`。

## 4. 先理解这段最小代码

```python
from brian2 import *

start_scope()

tau = 10*ms
group = NeuronGroup(
    1,
    "dv/dt = (1.1 - v)/tau : 1",
    threshold="v > 1",
    reset="v = 0",
    method="exact",
)
spikes = SpikeMonitor(group)
run(100*ms)
print(spikes.count[:])
```

逐行理解：

1. `start_scope()` 清空前一次交互实验收集的 Brian 对象。
2. `10*ms` 是带物理单位的量，不是普通浮点数。
3. `NeuronGroup(1, ...)` 创建一个神经元。
4. 方程字符串定义连续时间动力学。
5. `threshold` 定义何时产生脉冲。
6. `reset` 定义脉冲之后如何更新状态。
7. `method` 选择数值积分方法。
8. Monitor 负责记录；`run` 才真正推进仿真时间。

## 5. 完整功能地图

### 模型表达

- 带单位的变量和常量
- 常微分方程、随机微分方程、代数子表达式
- 参数、共享变量、常量变量、链接变量
- 阈值、重置、不应期和自定义事件
- `Equations` 组合和命名空间
- 用户自定义函数

### 神经元与输入

- `NeuronGroup`
- `PoissonGroup`
- `SpikeGeneratorGroup`
- `PoissonInput`
- `TimedArray`
- `run_regularly` 与 `network_operation`

### 突触

- `Synapses` 的突触变量和动力学
- `connect()` 的全连接、一对一、条件、概率和显式索引
- 突触前/后事件、延迟、多事件路径
- 求和变量、多重突触、结构化权重
- STDP、短时可塑性和自定义学习规则

### 记录与分析

- `StateMonitor`
- `SpikeMonitor`
- `EventMonitor`
- `PopulationRateMonitor`
- 放电率平滑、权重和状态轨迹分析

### 仿真控制

- 魔法网络与显式 `Network`
- `Clock`、`defaultclock.dt`
- 对象调度和 `when`/`order`
- `store()`/`restore()`
- 随机种子、性能分析和对象激活

### 生物物理与性能

- `Morphology`、`Cylinder`、`Soma`、`Section`
- `SpatialNeuron` 和电缆方程
- NumPy、Cython 运行时目标
- C++ standalone 设备
- OpenMP、编译器设置和缓存管理

完整 API 很大。本教程覆盖每一类核心能力，并用代表性示例建立迁移能力；查找具体参数时再配合官方参考文档。

## 6. 学习方法

每章做三遍：

1. 不运行，先读方程并预测曲线或脉冲。
2. 运行原始代码，打开 `outputs/` 中的图。
3. 只改一个参数，例如 `tau`、连接概率或延迟，再解释变化。

最重要的习惯：先检查单位，再检查方程，再检查时间步，最后才怀疑框架。

## 7. 常见问题

`DimensionMismatchError`
: 方程两边单位不一致。不要用裸数字代替 `mV`、`ms`、`nA` 等物理量。

结果每次不同
: 模型使用了 `rand()`、`randn()`、`xi` 或泊松输入。调用 `seed(数字)` 固定随机性。

运行很慢
: 先减小神经元数和仿真时长；再查看 `profiling_summary`；最后考虑 Cython 或 C++ standalone。

没有脉冲
: 检查输入是否足够强、阈值是否合理、初始值和单位是否正确。

## 8. 官方资料

- [稳定版用户指南](https://brian2.readthedocs.io/en/stable/user/index.html)
- [官方教程](https://brian2.readthedocs.io/en/stable/resources/tutorials/index.html)
- [示例库](https://brian2.readthedocs.io/en/stable/examples/index.html)
- [API 参考](https://brian2.readthedocs.io/en/stable/reference/index.html)
- [PyPI](https://pypi.org/project/Brian2/)

