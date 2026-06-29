# 🛰️ 传感器管线

Genesis 传感器建模的是**机器人控制视角**下的传感器：应用代码从机器人板载软件中查询到的值，而不是模拟模拟电路导线上的瞬时信号。本页解释这一抽象、逐步生成用户可见测量值的管线，以及让 `read()` 成为常数时间内存查询的缓冲方案。

如需实现自己的传感器，请参见 [实现自定义传感器](custom_sensors.md)。

## 抽象：写入共享内存的嵌入式采样器

真实机器人不会在每个控制循环迭代中从模拟导线上拉取数值。数据流更接近：

```text
sensor hardware -> (analog wire, ADC, electronics noise, sensor bandwidth/response)
                -> firmware-level signal processing
                -> embedded firmware writes a digital snapshot into shared memory
                -> sensor.read() queries shared memory
```

机器人的 `read()` 是一次**内存查询**。它不会触发传感器采集。传感器由以自身频率运行的嵌入式过程异步采样，读到的值可能是几毫秒前写入的。同一个控制步内两次调用 `read()` 应返回**相同的值**，因为期间没有新快照写入。

这一点决定了管线中的误差分层：

- **物理层误差**是仿真器没有建模的底层物理现象随机波动，例如真实物理量的漂移、确定性场上的细尺度湍动等。它影响传感器实际“看到”的现象，并会通过传感器响应模型传播到后续步骤，因此位于 **measured** 时间线环上；GT 保留原始仿真现象。它被打包进 `_update_current_timestep_data`，传感器可以把“原始信号 + 噪声”融合到一个 kernel pass 中。
- **硬件层误差**是传感器读出阶段的属性，例如电子噪声、ADC 量化和传感器输出漂移。它应用在每步工作缓冲区上，**不写入 timeline ring**。这样，`_apply_transform` 中的状态递推读取的是干净的历史槽位，不会把上一帧硬件噪声重复放大。
- **延迟和抖动**表示快照相对于“现在”的陈旧程度。`delay = D` 表示控制时间 `t` 的读数来自 `t - D - jitter_t` 时捕获的最终值。默认采样规则是 zero-order hold，适合 bool、uint8、量化 float 等任意返回类型。
- **同一步内读数幂等。** 如果某种设计让同一步多次读取得到不同值，就违背了这个抽象。
- **历史读取**返回最近 `N` 个**最终测量值**，也就是经过延迟、硬件误差和类型转换后的快照。

## 类层次

```text
Sensor                       (最小契约)
└── SimpleSensor             (标准管线；大多数 Genesis 传感器继承它)
    ├── ContactSensor
    ├── ContactForceSensor
    ├── IMUSensor
    ├── ProximitySensor
    ├── RaycasterSensor
    ├── KinematicContactProbe
    ├── ElastomerDisplacementSensor
    └── TemperatureGridSensor

Camera (RasterizerCameraSensor, RaytracerCameraSensor, BatchRendererCameraSensor)
直接继承 Sensor，因为它有自己的渲染路径，不使用 SimpleSensor 管线。
```

`Sensor` 是最小定制契约：一个抽象逐步计算方法 `_update_shared_cache`，四个规格访问器（实例方法 `_get_return_format` / `_get_intermediate_format` 定义 shape，类方法 `_get_cache_dtype` / `_get_intermediate_dtype` 定义 dtype），一个默认恒等的 `_post_process` 投影，以及类级能力标志 `uses_ring_pipeline: ClassVar[bool] = True`。这个标志告诉 manager 是否需要为该类分配逐步 timeline rings（GT + measured）。

`SimpleSensor` 在其上构建标准管线，并暴露以下可重写 hook：`_update_raw_data`、`_update_current_timestep_data`、`_apply_physics_imperfections`、`_apply_transform`、`_apply_hardware_imperfections`。其中 `_update_raw_data` 与 `_apply_physics_imperfections` 被打包在 `_update_current_timestep_data` 内，因此需要把两者融合进单个 kernel pass 的传感器可以只重写这个 hook。

## 逐步管线

每个仿真步中，`SimpleSensor` 的编排器执行：

```text
_update_current_timestep_data
  raw -> GT intermediate cache，镜像到 GT timeline slot 0 和 measured timeline slot 0
  _apply_physics_imperfections(measured slot 0)

GT 分支:
  _apply_transform(GT slot 0, timeline=GT timeline, is_measured=False)
  _post_process(GT intermediate, timeline=GT return ring, is_measured=False)
  写入 GT return-space ring slot 0
  读取 slot 0 -> GT return cache

measured 分支:
  _apply_transform(measured slot 0, timeline=measured timeline, is_measured=True)
  copy measured slot 0 -> per-dtype intermediate cache
  _apply_hardware_imperfections(intermediate cache)
  _post_process(intermediate cache, timeline=measured return ring, is_measured=True)
  写入 measured return-space ring slot 0
  从 measured return ring 按 delay + jitter 采样 -> measured return cache
```

读路径是常数时间查询：

- `Sensor.read()` 返回该传感器 measured return cache 的 view；有延迟时已完成延迟采样。
- `Sensor.read_ground_truth()` 返回 GT 一侧的对应值；GT 不使用延迟。
- `Sensor.read(history_length=N)` 从 return-space ring 中聚合最近 `N` 个快照，返回新张量。
- `SensorManager.read_sensors()` 按传感器类别返回新张量；无 history 时来自 per-class return cache，有 history 时来自 per-class return-space ring。

## intermediate 与 return 的分离

管线在 `_apply_hardware_imperfections` 之前一直运行在 **intermediate space**：transform、物理误差和硬件误差都读写 intermediate 值。类型转换、阈值、clamp、mask、deadband 等属于 `_post_process`，它把 intermediate space 投影到 **return space**。return-space ring 存储投影后的快照，延迟采样再从这个 ring 的旧槽位写入 per-class return cache。

这种分离是结构性的。`_apply_transform(timeline=...)` 允许 filter 读取 timeline ring 的旧槽位，例如用 `timeline.at(1)` 读取上一帧。旧槽位必须与当前 `data` 处于同一数据空间，否则滤波会混合不同语义的数据并产生错误结果。因此 timeline ring 存储 intermediate-space 值，而 return cache 和 return-space ring 存储 return-space 值。

当 `_post_process` 是恒等映射，并且没有配置 delay/history 时，manager 只分配一个缓冲区，并让 per-class return cache 作为 intermediate slice 的零拷贝 alias view。当 `_post_process` 被重写时，例如 ContactSensor 从 float 投影为 bool，return cache 会成为由 return-space ring 填充的独立缓冲区。

## 为什么 shape 是每实例的，而 dtype 是每类统一的

`_get_return_format` 和 `_get_intermediate_format` 是实例方法，因为传感器选项可以合理地影响返回形状，例如 `Raycaster.pattern.return_shape`、`Camera.res`、`Proximity.probe_local_pos`、`TemperatureGrid.grid_size` 等。manager 会在为缓冲区定尺寸时累计每个实例的贡献。

`_get_cache_dtype` 和 `_get_intermediate_dtype` 是类方法。dtype 必须按传感器类统一，这是 manager 的重要不变量：某一传感器类在 per-dtype intermediate buffer 中对应的 slice 必须连续。如果同一类的不同实例允许不同 dtype，就会把一次每类批量 `_update_shared_cache` 退化成多次 per-(class, dtype) 子批处理。需要不同 dtype 时，应定义不同传感器类。

## 为什么 `_post_process` 是写入时执行，而不是读取时执行

原因有三点：

1. **调用次数确定。** manager 每个仿真步对每个分支调用固定次数的 `_post_process`，不受 controller、logger、visualization 等消费者读取次数影响。
2. **存在真实的 per-class return storage。** 如果投影延迟到读取时执行，`_post_process` 需要每次读取都分配新张量。写入时执行让 manager 拥有可复用的后处理缓冲区。
3. **成本可摊销。** 控制循环中同一传感器常被 controller、logger 和 visualization 多次读取。写入时投影每步只执行一次。

## 存储作用域

manager 拥有所有存储，概念上分为四类：

- **Per-dtype intermediate storage**：每种 dtype 一个缓冲区，保存管线内部值；每个传感器类在其中拥有连续 slice。
- **Per-class return storage**：每个传感器类一个 return-space 缓冲区，形状和 dtype 由 `_get_return_format` / `_get_cache_dtype` 声明。简单情况下它可以是 intermediate 的 alias view。
- **Per-dtype timeline rings**（GT + measured）：intermediate space 中的成对环形缓冲区，保存 post-transform、pre-hardware 的快照。
- **Per-class return-space rings**（GT + measured）：return space 中的成对环形缓冲区，保存 post-`_post_process`、pre-delay-sample 的最终快照。启用 delay、history 或重写 `_post_process` 时会分配。

每个仿真步中，manager 会旋转 timeline rings 和 return-space rings，更新共享上下文，然后对每个传感器类调用一次 `_update_shared_cache`，最后写入 return-space ring 并根据 delay 采样 measured cache。

## 选项语义

`SensorOptions` 提供所有传感器都有的时间相关选项；`SimpleSensorOptions(SensorOptions)` 额外提供 SimpleSensor 分支解释的误差参数。Camera 直接继承 `Sensor`，因此只使用时间相关字段。

| Option | Default | 作用位置 |
|---|---|---|
| `delay` | 0.0 | measured return-space ring 的读偏移，单位秒。延迟读数返回 D 步前产生的最终值。 |
| `jitter` | 0.0 | 每个环境逐步采样的随机附加延迟，`Uniform[0, jitter)`，必须不超过 `delay`。 |
| `history_length` | 0 | 大于 0 时，`read()` 返回最近 `N` 个最终测量值，沿新的 history 轴堆叠。 |
| `noise` | 0.0 | 零均值高斯噪声标准差，在 `_apply_hardware_imperfections` 中每步采样。 |
| `bias` | 0.0 | 传感器输出阶段的常量偏移。 |
| `random_walk` | 0.0 | 随机游走步长标准差；漂移累加器每步推进并加入输出。 |
| `resolution` | 0.0 | 量化步长，输出值会四舍五入到该步长的倍数。 |

`noise`、`bias`、`random_walk`、`resolution` 是通用误差参数。`SimpleSensor._apply_hardware_imperfections` 采用上面描述的“嵌入式采样器”解释；直接继承 `Sensor` 的子类可以用不同方式解释或忽略它们。需要通过响应模型传播的误差应放在 `_apply_physics_imperfections` 中，因为它在 `_apply_transform` 之前作用于 measured timeline slot。

### 为什么误差在捕获时固化

机器人的 `read()` 是内存查询。数字化值一旦进入 ring，噪声就被固定下来；之后读取同一槽位会得到同一个带噪值。这保证了同一个控制步内多次 `read()` 返回相同结果，也让延迟读数携带捕获时刻的误差状态。
