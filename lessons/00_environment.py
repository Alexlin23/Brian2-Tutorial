"""第 0 章：认识当前 Brian2 运行环境。"""

import platform
import shutil

import brian2
import numpy
from brian2 import get_device, prefs


# 这一章不建立神经网络，只确认后续示例依赖的运行环境。
# get_device() 表示 Brian2 当前怎样执行仿真；默认通常是运行时设备。
print("Python:", platform.python_version())
print("Brian2:", brian2.__version__)
print("NumPy:", numpy.__version__)
print("当前设备:", type(get_device()).__name__)

# codegen target 决定方程被翻译成哪种执行代码。
# NumPy 最容易直接运行；Cython/C++ 通常更快，但需要编译器。
print("默认代码生成目标:", prefs.codegen.target)
print("C++ 编译器:", shutil.which("cl") or shutil.which("g++") or "未发现")
print("\n没有 C++ 编译器也能使用 NumPy 目标学习前九章。")
