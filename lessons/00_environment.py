"""第 0 章：认识当前 Brian2 运行环境。"""

import platform
import shutil

import brian2
import numpy
from brian2 import get_device, prefs


print("Python:", platform.python_version())
print("Brian2:", brian2.__version__)
print("NumPy:", numpy.__version__)
print("当前设备:", type(get_device()).__name__)
print("默认代码生成目标:", prefs.codegen.target)
print("C++ 编译器:", shutil.which("cl") or shutil.which("g++") or "未发现")
print("\n没有 C++ 编译器也能使用 NumPy 目标学习前九章。")

