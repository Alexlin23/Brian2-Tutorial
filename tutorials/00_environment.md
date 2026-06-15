# 第 0 章：先弄清楚我们到底在运行什么

对应实验：[lessons/00_environment.py](../lessons/00_environment.py)

## 这一章解决什么问题

很多教程一上来就让你输入 `pip install`，然后立即创建神经元。这样虽然可能跑得起来，但一旦报错，你会完全不知道问题属于哪一层。

这一章先建立一张“运行地图”：

1. Python 负责执行你写的教程脚本。
2. Brian2 负责理解神经元方程、检查单位并组织仿真。
3. NumPy、Cython 或 C++ 负责执行 Brian2 生成的数值计算代码。
4. 编译器只在选择需要编译的后端时才需要。

你应该在本章结束后说清楚：

- “Brian2 版本”和“Python 版本”为什么是两回事。
- `device` 与 `codegen target` 分别控制什么。
- 没有 C++ 编译器为什么仍然可以学习本教程。
- 环境错误应该从哪一层开始排查。

## 1. 神经仿真不是普通的逐行 Python 计算

下面这类 Brian2 代码看上去像普通 Python：

```python
neurons = NeuronGroup(
    100,
    "dv/dt = -v/(10*ms) : 1",
    method="exact",
)
run(100*ms)
```

但 Brian2 并不是让 Python 在每个时间步里逐个神经元执行一次字符串。

大致过程是：

1. Python 创建 `NeuronGroup` 对象。
2. Brian2 解析方程字符串。
3. Brian2 检查变量和物理单位。
4. Brian2 根据积分方法生成更新状态的代码。
5. 所选执行后端运行生成的代码。
6. `Monitor` 把你要求的数据记录回来。

因此，Brian2 同时扮演了三种角色：

- **模型描述器**：你写方程、阈值、重置和突触事件。
- **实验调度器**：它决定每个时间步中谁先更新、谁后更新。
- **代码生成器**：它把高层模型翻译成可执行计算。

理解这三层后，你就不会把所有错误都归结为“Python 写错了”。

## 2. Python、Brian2、NumPy 分别是什么

实验开头导入：

```python
import brian2
import numpy
```

### Python

Python 是语言和解释器。它负责：

- 导入模块。
- 创建 Brian2 对象。
- 执行实验控制代码。
- 调用绘图和文件保存逻辑。

不同 Python 版本会影响哪些 Brian2 版本和二进制依赖可以安装。

### Brian2

Brian2 是脉冲神经网络仿真框架。它负责：

- 解析微分方程。
- 检查单位。
- 创建神经元、突触、输入源和监视器。
- 生成并调度仿真代码。

### NumPy

NumPy 是 Python 中的数值数组库。Brian2 的 NumPy 后端会用向量化数组运算更新整群神经元。

“NumPy 后端”不意味着模型变成了普通 NumPy 教程。模型仍由 Brian2 定义，只是底层计算交给 NumPy 执行。

## 3. 为什么要打印版本

实验代码：

```python
print("Python:", platform.python_version())
print("Brian2:", brian2.__version__)
print("NumPy:", numpy.__version__)
```

版本信息是实验可复现性的一部分。

同一份代码在不同机器上失败，常见原因不是模型思想不同，而是：

- Python 版本不同。
- Brian2 API 或依赖要求发生变化。
- NumPy 删除了旧接口。
- 编译器或操作系统不同。

本项目当前验证环境是：

```text
Python: 3.11.9
Brian2: 2.9.0
NumPy: 1.26.4
```

它们不是“永远最好的版本”，而是一组已经共同验证过的版本。

## 4. device 是什么

代码：

```python
from brian2 import get_device

print("当前设备:", type(get_device()).__name__)
```

这里的“设备”不是显卡型号，而是 Brian2 组织整个仿真的方式。

默认的 `RuntimeDevice` 表示：

- 在当前 Python 进程中创建对象。
- 调用 `run()` 时立即生成并执行所需代码。
- 运行结束后立刻可以在 Python 中读取结果。

以后会接触 `cpp_standalone`。它的思路不同：

1. Python 先描述完整实验。
2. Brian2 生成一个独立 C++ 工程。
3. 编译并运行该工程。
4. 再把结果读回。

可以把两者理解为：

- Runtime：一边写实验，一边运行。
- Standalone：先把整份实验编译成独立程序，再运行。

初学阶段使用 Runtime 更容易调试。

## 5. codegen target 是什么

代码：

```python
from brian2 import prefs

print("默认代码生成目标:", prefs.codegen.target)
```

`codegen target` 决定 Runtime 模式下，一段状态更新代码由谁执行。

常见目标：

| 目标 | 大致机制 | 优点 | 代价 |
|---|---|---|---|
| `numpy` | 生成 NumPy 数组运算 | 无需编译器，启动简单 | 大模型可能较慢 |
| `cython` | 生成并编译 Cython/C++ 扩展 | 循环密集型计算通常更快 | 首次运行需要编译 |
| `auto` | Brian2 自动选择 | 配置省事 | 环境问题不够直观 |

本教程的共享工具把正式实验固定到 `numpy`，目的是先减少环境变量。等你确认模型正确，再学习性能优化。

这体现一个重要工程原则：

> 先让模型正确、可解释、可复现，再让它更快。

## 6. 编译器在什么时候才需要

代码：

```python
compiler = shutil.which("cl") or shutil.which("g++")
```

`shutil.which()` 会在系统的 `PATH` 中寻找可执行程序：

- `cl` 通常是 Microsoft C/C++ 编译器。
- `g++` 通常是 GNU C++ 编译器。

如果打印“未发现”，你仍然可以：

- 使用 NumPy 目标。
- 创建神经元和突触。
- 运行本教程的全部默认示例。
- 画图并分析结果。

你暂时不能顺利使用的主要是：

- Cython 目标的本地编译。
- C++ standalone。
- 依赖本地编译器的加速方案。

所以“没有编译器”和“Brian2 完全不能运行”是两件不同的事。

## 7. 逐段阅读本章实验

### 导入普通环境工具

```python
import platform
import shutil
```

- `platform` 用来查询 Python 和操作系统信息。
- `shutil.which` 用来查询命令是否存在。

### 导入数值仿真组件

```python
import brian2
import numpy
from brian2 import get_device, prefs
```

这里没有使用 `from brian2 import *`，因为本章只需要两个明确对象。后续实验为了让方程代码紧凑，会使用星号导入；在大型工程中通常更推荐显式导入。

### 输出诊断信息

其余代码只读取环境，不会启动仿真。因此本章：

- 不需要 `start_scope()`。
- 不需要 `NeuronGroup`。
- 不需要 `run()`。

## 8. 怎样运行

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe lessons\00_environment.py
```

不要在 `lessons` 目录内部运行整套教程。后面的脚本会按仓库根目录寻找共享工具和输出目录。

## 9. 怎样阅读输出

输出示例：

```text
Python: 3.11.9
Brian2: 2.9.0
NumPy: 1.26.4
当前设备: RuntimeDevice
默认代码生成目标: auto
C++ 编译器: 未发现
```

逐项解释：

- 前三行回答“当前依赖组合是什么”。
- `RuntimeDevice` 回答“仿真是在当前 Python 进程运行，还是先生成独立工程”。
- `auto` 回答“Runtime 代码优先尝试什么执行目标”。
- “未发现”只说明当前终端找不到 C++ 编译器。

## 10. 常见误区

### 误区一：能导入 Brian2 就说明环境完全正确

导入成功只证明基础模块可加载。某些功能还可能需要：

- SciPy。
- Matplotlib。
- C++ 编译器。
- 与当前 Python 匹配的二进制包。

因此环境检查要分功能层次进行。

### 误区二：最快的后端永远最好

小实验中，编译时间可能比仿真本身还长。开发阶段使用 NumPy，最终批量实验再切换后端，通常更合理。

### 误区三：版本越新越好

科研代码首先追求的是可复现。未经验证地升级某一个依赖，可能破坏整组兼容关系。

## 11. 动手实验

1. 运行脚本，把输出保存到实验记录中。
2. 在 Python 中执行 `import sys; print(sys.executable)`，确认当前解释器来自 `.venv`。
3. 执行 `where.exe python`，观察系统可能同时存在多少个 Python。
4. 把 `prefs.codegen.target` 临时打印为 `"numpy"`，理解“偏好设置”和“当前检测结果”的区别。
5. 查找本机是否存在 `clang++`，但不要急着修改教程配置。

## 本章小结

你还没有模拟神经元，但已经建立了后续排错所需的地图：

```text
教程脚本
  -> Brian2 解析模型和调度实验
  -> 代码生成目标执行数值更新
  -> Monitor 返回结果
```

下一章开始建立第一个神经元。届时最重要的问题不是记住 API，而是理解：一条连续微分方程怎样与离散脉冲事件组合起来。

## 官方参考

- [单位系统](https://brian2.readthedocs.io/en/stable/user/units.html)
- [代码生成与执行后端](https://brian2.readthedocs.io/en/stable/user/computation.html)
