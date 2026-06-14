# 调研记录

## 2026-06-14 注释盘点

- 11 个课程脚本和综合项目目前只有章节级 docstring，主体代码几乎没有行内教学注释。
- 最需要解释的内容是方程字符串、单位、积分方法、突触事件、监视器、调度时机和结果图。
- `lesson_utils.py` 与 `run_all.py` 也需要简短流程注释，帮助学习者理解输出目录和批量执行机制。
- 本轮只补注释，不调整模型结构、参数或输出。

## 当前已知

- 工作区中尚无 Brian2 教程项目。
- 用户希望放慢节奏，以教学为主，同时了解 Brian2 的完整功能。
- 当前系统为 Windows PowerShell，项目路径包含中文字符。
- 本机为 Python 3.11.9，已安装 Matplotlib，尚未安装 Brian2。
- 本机命令行未发现 `cl`、`gcc` 或 `g++` 编译器。

## 版本与兼容性

- 截至 2026-06-14，PyPI 最新稳定版是 Brian2 2.10.1，发布于 2025-12-05。
- Brian2 2.10.1 要求 Python >= 3.12 和 NumPy >= 2.0。
- Brian2 2.9.0 发布于 2025-05-14，要求 Python >= 3.10，并提供 CPython 3.11 Windows wheel。
- 因此本项目在当前机器锁定 `Brian2==2.9.0`；升级 Python 后可改用 2.10.1。
- Brian2 2.9.0 在本机不能与 NumPy 2.4.6 导入运行，因为它仍使用已移除的 `numpy.ndarray.ptp`；项目锁定 NumPy 1.26.4。
- NumPy 代码生成目标下运行 `SpatialNeuron` 需要 SciPy，项目锁定 SciPy 1.14.1。
- 没有 C++ 编译器时，仍可使用 NumPy 运行目标；Cython/C++ standalone 章节以功能说明和环境检测为主。

## 官方功能地图

官方用户指南的主功能包括：

- 物理单位系统
- 神经元模型、噪声、阈值、重置、不应期、子组、共享及链接变量
- 数值积分方法
- 方程字符串、函数、特殊变量、事件驱动方程和 `Equations`
- 突触模型、连接语法、延迟、权重矩阵、求和变量、多重突触和多路径
- 泊松输入、脉冲生成、显式输入方程、`TimedArray` 和网络操作
- 脉冲、状态、事件值和群体放电率记录
- `Network`、时间步、调度、性能分析和 `store/restore`
- 多区室形态与 `SpatialNeuron`
- 运行时代码生成、standalone 代码生成和编译器设置

## 官方资料

- 用户指南：https://brian2.readthedocs.io/en/stable/user/index.html
- 教程：https://brian2.readthedocs.io/en/stable/resources/tutorials/index.html
- PyPI：https://pypi.org/project/Brian2/

## 教学原则

- 每次只引入少量新概念。
- 每章先解释“为什么”，再解释 API，最后运行实验。
- 明确区分生物模型假设、数值仿真设置和 Brian2 语法。
- 用小网络快速验证，再逐步扩展规模。
