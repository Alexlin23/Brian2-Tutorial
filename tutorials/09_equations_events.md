# 第 9 章：把方程组织成模块，并定义 spike 之外的事件

对应实验：[lessons/09_equations_events.py](../lessons/09_equations_events.py)

输出图片：[outputs/09_equations_events.png](../outputs/09_equations_events.png)

## 这一章解决什么问题

到目前为止，方程大多直接写在 `NeuronGroup` 中。模型变复杂后会遇到：

- 同一组方程需要复用。
- 方程需要由多个模块组合。
- 某些量只是其他变量的即时计算结果。
- 除了 spike，还需要检测“进入高状态”“越过钙浓度阈值”等事件。

本章学习三个能力：

1. 用 `Equations` 对象组织模型。
2. 用子表达式表示派生量。
3. 用自定义事件触发动作并记录事件。

## 1. 为什么需要 Equations 对象

直接字符串适合小模型：

```python
NeuronGroup(10, "dv/dt = -v/tau : 1", ...)
```

复杂模型可能由多个部分组成：

```text
膜电位模块
适应变量模块
突触电流模块
代谢或能量模块
```

`Equations` 把方程从具体 NeuronGroup 创建动作中分离出来：

```python
equations = Equations(
    """
    dv/dt = (drive-v)/tau : 1
    energy = v**2 : 1
    drive : 1
    """
)
```

这样可以：

- 先检查和阅读方程。
- 在多个群体中复用。
- 组合方程模块。
- 程序化替换变量名或参数。

本例规模很小，但展示的是大型模型的组织方式。

## 2. 三种方程行分别是什么

### 微分方程

```text
dv/dt = (drive-v)/tau : 1
```

v 是动态状态，Brian2 随时间积分。

### 子表达式

```text
energy = v**2 : 1
```

energy 由当前 v 即时计算。

它不是一个拥有独立动力学的状态：

- 没有初始值。
- 不会单独积分。
- v 改变时 energy 随之改变。

### 参数声明

```text
drive : 1
```

drive 是可赋值变量，但没有自动时间演化规则。

这三类变量必须区分：

```text
状态变量：有自己的时间演化
子表达式：由其他变量即时计算
参数变量：由实验者或其他机制赋值
```

## 3. `energy=v**2` 真的是生物能量吗

不是。

它只是一个教学用派生量，用来展示：

- 子表达式如何声明。
- Monitor 如何同时记录状态与派生量。
- EventMonitor 如何保存事件时的派生量。

真实代谢能量模型需要更明确的物理量、单位和生物机制。

给变量起一个直观名字有助于教学，但不能用名字代替模型依据。

## 4. 命名空间中的 tau

方程引用：

```text
tau
```

Python 代码中定义：

```python
tau = 10 * ms
```

tau 没有在 Equations 内声明为每个神经元的变量，因此它从外部命名空间解析。

两种设计：

### 外部常量

```python
tau = 10*ms
```

适合所有神经元共享且实验中不需要频繁改变的常量。

### 群体变量

```text
tau : second
```

然后：

```python
neurons.tau = ...
```

适合每个神经元不同或运行阶段需要改变的参数。

模型组织不仅是语法选择，也决定参数属于哪个层级。

## 5. spike 事件本身也是一种事件

普通神经元使用：

```python
threshold="v > 1"
reset="v = 0"
```

当 threshold 条件成立时，Brian2 触发名为 `spike` 的默认事件，然后执行 reset，并通知：

- SpikeMonitor。
- 以该群体为 source 的突触 `on_pre`。
- 以该群体为 target 的突触 `on_post`。

因此 spike 不是特殊到无法推广的机制。Brian2 允许你定义其他事件。

## 6. 自定义 `high` 事件

代码：

```python
events={"high": "v > 0.8"}
```

这为群体增加名为 high 的事件。

每个时间步检查：

```text
v > 0.8 ?
```

条件为真时触发 high。

重要细节：

> 自定义事件条件不是只在“从假变真”的瞬间自动触发一次。只要条件在后续检查时仍为真，就可能再次触发。

本例的事件动作会把 v 降低 0.15，通常将其推回阈值下，因此形成间隔触发。

如果事件动作没有让条件变假，high 可能每个时间步都触发。

## 7. `run_on_event` 在做什么

代码：

```python
neurons.run_on_event(
    "high",
    "v -= 0.15",
)
```

含义：

```text
当 high 事件发生时，立即把对应神经元的 v 减少 0.15。
```

它类似 reset，但绑定到自定义事件而不是 spike。

于是一个神经元现在有两套事件：

| 事件 | 条件 | 动作 |
|---|---|---|
| `high` | `v > 0.8` | `v -= 0.15` |
| `spike` | `v > 1` | `v = 0` |

因为 high 在更低阈值触发并降低 v，它会阻碍 v 达到 spike 阈值。

这相当于一个离散负反馈控制器。

## 8. 三个 drive 条件如何影响事件

```python
neurons.drive = [0.9, 1.05, 1.2]
```

### drive=0.9

平衡点高于 high 阈值 0.8，但低于 spike 阈值 1。

它可以反复触发 high，却很难产生普通 spike。

### drive=1.05

没有 high 负反馈时可以越过 spike 阈值。

但每到 0.8 附近就被减去 0.15，可能一直被限制在 spike 阈值下。

### drive=1.2

恢复上升更快，因此 high 事件更频繁。

是否还能达到 spike 阈值取决于：

- 事件调度。
- dt。
- 每次减少量。
- 驱动力。

运行前应预测 high 事件数随 drive 增大而增加。

## 9. EventMonitor 与 SpikeMonitor 的关系

代码：

```python
high_events = EventMonitor(
    neurons,
    "high",
    variables=["v", "energy"],
)
```

EventMonitor 需要指定事件名称。

它记录：

- `high_events.t`：事件时刻。
- `high_events.i`：神经元编号。
- `high_events.v`：事件调度点的 v。
- `high_events.energy`：同一时刻的派生量。

SpikeMonitor 可以看作专门用于 `spike` 事件的便捷监视器。

当研究对象不是脉冲，而是：

- 高状态进入。
- 阈值跨越。
- 内部控制事件。

EventMonitor 更合适。

## 10. 事件记录值与事件动作的先后

同一事件可能同时关联：

- EventMonitor。
- `run_on_event` 动作。
- 突触路径。

它们在调度中有具体的 when 和 order。

因此看到事件记录的 v 时，不应仅凭直觉断言它一定是“减 0.15 之前”或“之后”。默认调度通常让事件监视和事件执行位于相应事件槽，但精确顺序应通过：

- 对象的 when/order。
- `scheduling_summary()`。
- 一个最小测试。

来确认。

这条原则适用于所有离散仿真框架：事件发生在同一时间标签，不代表内部执行没有顺序。

## 11. 为什么还要 StateMonitor

```python
state = StateMonitor(
    neurons,
    ["v", "energy"],
    record=True,
)
```

EventMonitor 只记录 high 事件时刻。

StateMonitor 记录完整时间轨迹，可以看到：

1. v 怎样向 drive 上升。
2. 达到 high 条件。
3. 被事件动作向下拉。
4. 再次上升。

两类数据结合才能解释事件机制。

## 12. 图中锯齿与第 1 章有什么不同

第 1 章：

- 到 v>1 触发 spike。
- reset 到 0。
- 大幅下降。

本章：

- 到 v>0.8 触发 high。
- 只减去 0.15。
- 小幅下降。

因此会形成围绕 high 阈值附近的较小锯齿。

这说明离散事件不一定代表神经元放电。它可以是任意满足模型需求的状态转换。

## 13. 子表达式何时值得使用

适合子表达式：

- 多处重复使用的公式。
- 需要记录的派生量。
- 提高方程可读性。
- 由当前状态完全决定的瞬时量。

不适合：

- 需要自己保存历史的量。
- 具有独立时间常数的状态。
- 事件后需要单独修改的变量。

如果 energy 需要累积或衰减，就应写成微分方程，而不是 `energy=v**2`。

## 14. 常见误区

### 误区一：子表达式会被独立积分

它由当前变量即时计算。

### 误区二：自定义事件只在越过阈值瞬间触发

条件每个时间步检查；若持续为真，可能连续触发。

### 误区三：high 事件自动等价于 spike

只有 spike 会自动参与标准脉冲传播语义。其他事件需要显式配置相关动作或突触事件路径。

### 误区四：事件条件与动作可以不考虑调度

同一时间步内先后顺序可能改变记录值和后续条件。

### 误区五：变量名有生物含义就代表模型生物可信

可信度来自方程、单位、参数来源和验证，不来自命名。

## 15. 动手实验

### 实验 A：删除负反馈动作

暂时移除 `run_on_event`，观察 high 是否在条件持续为真时频繁触发。

### 实验 B：改变事件阈值

测试 0.6、0.8、0.95，预测事件频率和 spike 机会。

### 实验 C：改变事件动作幅度

比较：

```text
v -= 0.05
v -= 0.15
v -= 0.5
```

解释恢复时间和事件间隔变化。

### 实验 D：验证 energy

检查事件记录中：

```text
energy ≈ v**2
```

并讨论浮点误差和调度时刻。

### 实验 E：建立第二个自定义事件

例如定义 low 事件，在 v<0.2 时增加 drive。注意防止条件持续为真导致每步触发。

## 本章小结

模型变量可分为：

```text
动态状态：需要积分
参数：由实验者赋值
子表达式：由当前状态即时计算
```

模型事件可分为：

```text
spike：标准脉冲事件
自定义事件：由任意条件触发的离散转换
```

下一章会解释 Brian2 怎样把这些高层方程和事件翻译成 NumPy、Cython 或独立 C++ 程序，以及性能数字应该怎样测量。

## 官方参考

- [方程、子表达式与 Equations](https://brian2.readthedocs.io/en/stable/user/equations.html)
- [神经元模型与自定义事件](https://brian2.readthedocs.io/en/stable/user/models.html)
- [记录自定义事件](https://brian2.readthedocs.io/en/stable/user/recording.html)

