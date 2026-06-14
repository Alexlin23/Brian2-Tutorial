from pathlib import Path

import matplotlib
from brian2 import prefs

# 教程通过命令行批量运行，不需要弹出绘图窗口。
# Agg 会把图直接渲染到文件，适合无桌面环境和自动测试。
matplotlib.use("Agg")

# NumPy 后端不依赖本机 C/C++ 编译器，初学阶段最容易复现。
prefs.codegen.target = "numpy"

# 所有章节共用同一个输出目录，避免图片散落在源码目录中。
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def output_path(filename):
    """返回某个教程输出文件的绝对路径。"""
    return OUTPUT_DIR / filename
