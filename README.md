# Brian2 完整中文教程

这不是一组“运行成功就算学会”的示例代码。

本仓库把每个主题拆成三层：

```text
tutorials/  -> 讲清楚概念、公式由来、代码语义和结果解释
lessons/    -> 可直接运行的最小实验
outputs/    -> 实验产生的图片和报告
```

## 从这里开始

打开：

**[完整课程目录：tutorials/README.md](tutorials/README.md)**

第一次学习请按顺序阅读：

1. [第 0 章：运行环境与代码生成](tutorials/00_environment.md)
2. [第 1 章：第一个漏积分放电神经元](tutorials/01_first_neuron.md)
3. [第 2 章：神经元群体、差异与噪声](tutorials/02_neuron_group.md)
4. [第 3 章：突触、权重与延迟](tutorials/03_synapses.md)
5. [第 4 章：四种输入机制](tutorials/04_inputs.md)
6. [第 5 章：状态、脉冲与群体率记录](tutorials/05_monitors.md)
7. [第 6 章：STDP 可塑性](tutorials/06_stdp.md)
8. [第 7 章：Network、调度与公平对照实验](tutorials/07_network_control.md)
9. [第 8 章：多区室 SpatialNeuron](tutorials/08_spatial_neuron.md)
10. [第 9 章：Equations、子表达式与自定义事件](tutorials/09_equations_events.md)
11. [第 10 章：代码生成与性能分析](tutorials/10_codegen_performance.md)
12. [综合项目：兴奋/抑制循环网络](tutorials/project_balanced_network.md)

## 教程怎样教

每章都包含：

- 这一章在解决什么问题。
- 概念为什么会被提出。
- 数学方程逐项解释。
- Brian2 语法怎样映射到模型。
- 运行前应该预测什么。
- 输出数字和图应该怎样读。
- 常见误区为什么错。
- 可以独立验证理解的实验。

学习目标不是记住 `NeuronGroup`、`Synapses` 等名称，而是能够回答：

> 这条方程描述了什么机制？这段代码改变了谁？为什么会出现当前结果？怎样设计下一次实验验证解释？

## 安装

项目当前验证环境：

```text
Python 3.11
Brian2 2.9.0
NumPy 1.26.4
SciPy 1.14.1
```

在 PowerShell 中执行：

```powershell
cd "D:\重要文件\AI相关\模拟智能\Brian2完整教程"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

检查环境：

```powershell
.\.venv\Scripts\python.exe lessons\00_environment.py
```

## 运行一章

先阅读对应教材，再运行脚本。例如第 1 章：

```powershell
.\.venv\Scripts\python.exe lessons\01_first_neuron.py
```

然后查看：

```text
outputs/01_first_neuron.png
```

运行前先预测：

- 第一次脉冲大约何时出现？
- 相邻脉冲间隔是否相同？
- 改变 `tau` 后曲线怎样变化？

教材会带你从方程推导这些答案。

## 运行全部实验

```powershell
.\.venv\Scripts\python.exe run_all.py
```

批量入口会依次运行第 0 至第 10 章和综合项目。每章使用独立 Python 进程，避免对象、时钟和随机状态互相污染。

## 仓库结构

```text
Brian2完整教程/
├── tutorials/                 # 完整中文教材
│   ├── README.md              # 课程路线
│   ├── 00_environment.md
│   ├── ...
│   └── project_balanced_network.md
├── lessons/                   # 第 0 至第 10 章可运行实验
├── projects/                  # 综合网络项目
├── outputs/                   # 图片和性能报告
├── lesson_utils.py            # 绘图后端与输出路径
├── run_all.py                 # 批量运行入口
└── requirements.txt           # 已验证依赖
```

## 学习规则

每章至少做三遍：

1. **预测**：不运行，先根据方程预测。
2. **验证**：运行原代码，用输出检验预测。
3. **实验**：只改一个参数，解释变化来自哪个机制。

不要同时改多个参数。否则结果变化后，你无法判断原因。

推荐实验记录：

```text
问题：
只改变的参数：
运行前预测：
实际结果：
证据：
解释：
下一步：
```

## 遇到问题时先检查什么

### `DimensionMismatchError`

方程两边单位不一致。检查 `ms`、`mV`、`nA`、`Hz` 等单位，不要把带单位量随意替换成裸数字。

### 没有脉冲

这不一定是程序错误。依次检查：

1. 平衡点是否能达到阈值。
2. 输入强度是否足够。
3. 漏衰减是否过强。
4. 抑制是否过强。
5. 仿真是否足够长。
6. 初始状态和单位是否正确。

### 每次结果不同

模型可能使用 `rand()`、`randn()`、`xi`、泊松输入或随机连接。使用 `seed(...)` 可以复现单次随机序列；统计结论仍应使用多个种子。

### 运行太慢

先减少模型规模和记录量，再查看 `profiling_summary`。确认瓶颈后，才考虑 Cython 或 C++ standalone。

## 官方资料

- [Brian2 用户指南](https://brian2.readthedocs.io/en/stable/user/index.html)
- [Brian2 官方教程](https://brian2.readthedocs.io/en/stable/resources/tutorials/index.html)
- [Brian2 示例库](https://brian2.readthedocs.io/en/stable/examples/index.html)
- [Brian2 API 参考](https://brian2.readthedocs.io/en/stable/reference/index.html)

