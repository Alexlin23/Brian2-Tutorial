# 第 7 章：把一次演示变成可重复、可比较的仿真实验

对应实验：[lessons/07_network_control.py](../lessons/07_network_control.py)

输出图片：[outputs/07_network_control.png](../outputs/07_network_control.png)

## 这一章解决什么问题

前面的脚本通常：

1. 创建对象。
2. 调用一次 `run()`。
3. 画图。

真正的实验经常需要：

- 从同一个初始状态比较多个参数。
- 分训练期和测试期运行。
- 在运行中按固定频率执行操作。
- 控制对象执行先后顺序。
- 确认运行时间花在哪里。

本章把“能跑”升级成“能做公平实验”。

## 1. magic network 与显式 Network

简单写法：

```python
neurons = NeuronGroup(...)
spikes = SpikeMonitor(neurons)
run(50*ms)
```

Brian2 会收集当前作用域中的可见对象，组成默认网络。这种方式简洁，常称为 magic network。

显式写法：

```python
network = Network(neurons, spikes, state)
network.run(50*ms)
```

此时网络包含什么由你明确列出。

### 为什么复杂实验更适合显式 Network

- 对象可能保存在列表或自定义类中，自动收集不一定看得到。
- 可能同时维护两个互不影响的网络。
- `store`、`restore`、`run` 和性能报告都明确属于哪个网络。
- 阅读代码时更容易审计实验边界。

显式并不代表结果更“科学”，而是控制关系更清楚。

## 2. `(shared)` 变量为什么只存一份

方程：

```text
drive : 1 (shared)
```

普通变量：

```text
drive : 1
```

会为 10 个神经元各存一个值。

shared 变量只为整个群体存一个值：

```python
neurons.drive = 1.05
```

所有神经元读取同一个 drive。

适合：

- 全局刺激强度。
- 同一群体共享的实验条件。
- 运行阶段之间统一切换的参数。

不适合表达个体差异。若每个神经元需要不同 drive，就不能标记 shared。

## 3. `run_regularly` 是什么

代码：

```python
neurons.run_regularly(
    "v += 0.02*rand()",
    dt=2 * ms,
    when="start",
)
```

它创建一个周期操作：

- 每 2 ms 执行一次。
- 对群体中的每个神经元执行字符串语句。
- 每次给 v 加一个 0 到 0.02 的随机增量。

这不是微分方程的一部分，也不是突触事件。它更像仿真时钟触发的定时任务。

适合：

- 周期更新控制变量。
- 离散时间规则。
- 定期归一化。
- 简单实验协议。

如果操作需要任意 Python 逻辑，也可以使用 `network_operation`，但纯 Brian2 表达式通常更容易被代码生成器优化。

## 4. `dt=2*ms` 与默认时间步的关系

神经元状态可能每 0.1 ms 更新一次，而 `run_regularly` 每 2 ms 执行一次。

也就是大约每 20 个默认时间步执行一次随机增量。

对象可以拥有不同 Clock：

- 快速膜动力学使用小 dt。
- 慢控制变量使用大 dt。
- Monitor 可以降低采样频率。

这样可以节省计算和内存，但多个时钟的对齐需要谨慎。

## 5. `when="start"` 为什么重要

一个时间步不是一个不可分割动作。Brian2 会按调度槽依次执行对象。

常见槽位大致包括：

```text
start
groups
thresholds
synapses
resets
end
```

本例 `run_regularly(..., when="start")` 表示随机增量发生在该时间步较早阶段，然后状态更新和阈值检测再看到新的 v。

如果把同一操作放到 `end`：

- 本时间步阈值检测可能还看不到它。
- 它会影响下一个时间步。

当你关心事件相差一个 dt 时，调度不是实现细节，而是模型定义的一部分。

## 6. `store()` 保存什么

代码：

```python
network.store("initial")
```

它把当前网络状态保存为名为 `initial` 的快照。

包括：

- 神经元状态变量。
- 突触状态与连接信息。
- 时钟时间。
- 延迟队列等内部状态。
- 已纳入网络对象的内部状态。

它不会替你重建 Python 对象。恢复之前，网络结构对象仍然必须存在。

本例在 t=0、尚未运行时保存，所以两次条件都可以从同一初始状态开始。

## 7. `restore()` 与随机数状态的关键细节

本章使用：

```python
network.restore(
    "initial",
    restore_random_state=True,
)
```

为什么显式传 True？

`restore()` 默认会恢复网络状态，但默认不恢复随机数生成器状态。

如果保持默认：

- v 和时钟回到初始状态。
- 第二次运行继续使用后续随机数。
- 两次 `run_regularly` 得到不同随机扰动。

这样比较 drive=1.05 与 drive=1.25 时，同时改变了：

- drive。
- 随机输入序列。

加入 `restore_random_state=True` 后：

- 两次从相同状态开始。
- 两次使用相同随机序列。
- 唯一有意改变的是 drive。

这叫配对或共同随机数设计，可以降低随机波动对条件差异的干扰。

## 8. 两次实验的完整流程

### 保存共同起点

```python
network.store("initial")
```

### 条件 A

```python
neurons.drive = 1.05
network.run(50*ms, profile=True)
first_count = spikes.num_spikes
```

### 回到起点

```python
network.restore(
    "initial",
    restore_random_state=True,
)
```

### 条件 B

```python
neurons.drive = 1.25
network.run(50*ms, profile=True)
second_count = spikes.num_spikes
```

如果高驱动条件脉冲更多，我们才更有理由把差异归因于 drive。

## 9. 为什么恢复后 Monitor 数据也回到快照

快照在运行前创建，当时 Monitor 尚未记录数据。

恢复后：

- 网络时钟回到 0。
- Monitor 内部记录也回到保存时状态。
- 第二次运行的图只包含第二个条件。

因此不能在 restore 后还指望同一个 Monitor 自动保留第一次实验供绘图比较。

脚本在恢复前先把：

```python
first_count = spikes.num_spikes
```

复制到普通 Python 变量中，所以第一次的总数不会丢失。

若要比较完整轨迹，可以：

- 恢复前复制数组。
- 每个条件使用独立分析结果。
- 运行后保存到文件。

## 10. 为什么高 drive 会产生更多脉冲

方程：

```text
dv/dt = (drive-v)/(10*ms)
```

drive 是平衡点。

- drive=1.05：仅略高于阈值 1。
- drive=1.25：明显高于阈值。

从 reset 值 0 到阈值的理论时间为：

```text
t = tau * ln(drive / (drive-1))
```

drive 越高，达到阈值越快。

随机增量在两次实验中保持相同，因此它像一组相同的扰动背景，帮助我们更公平地观察 drive 的影响。

## 11. `profile=True` 在做什么

```python
network.run(50 * ms, profile=True)
```

让 Brian2统计不同代码对象的运行耗时。

随后：

```python
profiling_summary(network, show=5)
```

输出最耗时的对象，例如：

- state updater。
- threshold detector。
- resetter。
- StateMonitor。
- SpikeMonitor。

性能报告帮助回答：

> 时间花在模型计算，还是花在记录数据？

不要看到 StateMonitor 很慢就立刻删除它。应先判断它是否是研究问题必需的证据。

## 12. 性能测量中的第一次运行效应

某些代码生成后端第一次运行还包括：

- 方程解析。
- 代码生成。
- 编译。
- 缓存建立。

本章使用 NumPy 后端时编译开销较少，但一般性能实验仍应区分：

- 初始化时间。
- 构建时间。
- 实际仿真时间。

第 10 章会进一步讨论。

## 13. 常见误区

### 误区一：store 会把整个 Python 项目序列化

它保存网络状态，不会保存任意 Python 控制逻辑或替你重建对象。

### 误区二：restore 默认让随机实验精确重放

必须显式使用 `restore_random_state=True` 才恢复 Brian2/NumPy 随机状态。

### 误区三：两次运行都设置了 seed 就一定公平

seed 的设置位置和对象初始化过程也会消耗随机数。使用快照恢复通常更清晰。

### 误区四：when 只是性能选项

when 改变同一时间步内对象看到的数据，可能改变模型行为。

### 误区五：profile 中最慢的对象一定是错误设计

最慢可能只是最必要的计算或记录。优化要以研究目标为约束。

## 14. 动手实验

### 实验 A：关闭随机状态恢复

把 `restore_random_state=True` 改为 False，多次比较两条件差异。观察随机序列改变后差值是否更波动。

### 实验 B：加入第三个条件

比较 drive=1.05、1.15、1.25。每次都从 initial 恢复。

### 实验 C：比较 start 与 end

把 `run_regularly` 的 when 改成 end，观察脉冲时刻是否出现一个时间步级别的变化。

### 实验 D：降低 StateMonitor 采样率

设置：

```python
StateMonitor(..., dt=1*ms)
```

比较图、数据点数量和 profiling。

### 实验 E：查看调度表

调用 Brian2 的 `scheduling_summary()`，为每个对象标注：

- Clock。
- when。
- order。

## 本章小结

公平对照实验需要同时控制：

```text
相同网络结构
相同初始状态
相同仿真时长
相同随机序列
只改变目标参数
```

显式 Network、store/restore 和调度控制让这套流程可实现、可审计。

下一章将改变神经元表示本身：不再用一个 v 代表整个细胞，而是把神经突分成多个空间区室。

## 官方参考

- [运行、Network、store/restore、调度与 profiling](https://brian2.readthedocs.io/en/stable/user/running.html)

