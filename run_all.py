from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent

# 文件名以两位数字开头，因此排序后就是课程的学习顺序。
# 最后再运行综合项目，检查前面学到的组件能否一起工作。
SCRIPTS = [
    *sorted((ROOT / "lessons").glob("[0-9][0-9]_*.py")),
    ROOT / "projects" / "balanced_network.py",
]


def main():
    failures = []
    for script in SCRIPTS:
        print(f"\n=== Running {script.relative_to(ROOT)} ===")

        # 每章放在独立 Python 进程中运行。这样某一章创建的 Brian2
        # 对象、随机状态和全局时钟不会污染下一章。
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT)
        if result.returncode:
            failures.append(script)

    # 不在第一处错误立刻退出，便于一次看到所有失败章节。
    if failures:
        print("\nFailed examples:")
        for script in failures:
            print(f"- {script.relative_to(ROOT)}")
        raise SystemExit(1)

    print("\nAll Brian2 examples completed successfully.")


if __name__ == "__main__":
    main()
