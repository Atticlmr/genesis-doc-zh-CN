# 🧰 实现自定义传感器

本页面面向希望添加自定义传感器类型的高级用户。它是 [传感器管线](sensor_pipeline.md) 的作者视角配套文档：管线页面解释运行时如何执行，本页关注需要重写哪些 hook、它们必须满足什么 shape/dtype 契约，以及自动插件注册如何工作。

大多数情况下，从 `SimpleSensor` 派生，并且**只重写你需要的 hook**。直接从 `Sensor` 派生只适合完全绕过标准管线的传感器，内置相机就是这种情况。

## 添加传感器需要写什么

| Artifact | 位置 | 作用 |
|---|---|---|
| `<Name>` 选项类 | `genesis/options/sensors/<name>.py` 或插件包中 | 面向用户的 dataclass，携带每个传感器实例的参数。继承 `SimpleSensorOptions` 或合适的 mixin，并用传感器类作为前向引用泛型参数。 |
| `<Name>SharedMetadata` | 传感器实现旁边 | 该传感器类所有实例共享的运行时状态。继承 `SimpleSensorMetadata`，或非 Simple 传感器使用 `SharedSensorMetadata`。 |
| `<Name>Sensor` | 传感器实现旁边 | 传感器类本身。通常继承 `SimpleSensor[<Name>, None, <Name>SharedMetadata]`，并重写 `_get_return_format`、`_get_cache_dtype`、`_update_raw_data`，以及按需重写其他 hook。 |
| 可选的 `NamedTuple` 返回类型 | 传感器实现旁边 | 如果传感器返回多个张量，例如 IMU 返回 `lin_acc`、`ang_vel`、`mag`，声明一个 `NamedTuple` 并作为第四个泛型参数传入。 |
| 可选的 `SharedSensorContext` 子类 | 传感器实现旁边 | 只有当多个不同传感器类型需要共享昂贵资源时才需要，例如共享碰撞 BVH。 |

只要选项类和传感器类所在模块都已导入，Genesis 会自动把二者配对。用户只需要创建选项实例并传给 `scene.add_sensor(...)`。

## 自动注册

传感器不需要手动注册。定义一个用选项类参数化的 `Sensor` 子类就足够了；类体执行时，框架会记录这组配对。

支持两种放置方式：

- **内置传感器**：选项在 `genesis/options/sensors/*.py`，传感器在 `genesis/engine/sensors/*.py`，包的 `__init__` 已负责导入。
- **第三方插件**：把 `MyOptions` 和 `MySensor` 放在同一个 Python 包的兄弟子模块中：

  ```text
  my_sensor_plugin/
    __init__.py
    options.py     # class MyOptions(SimpleSensorOptions["MySensor"]): ...
    sensor.py      # class MySensor(SimpleSensor[MyOptions, MyContext, MyMetadata]): ...
  ```

  只要构造 `MyOptions()` 之前导入过 `my_sensor_plugin.options`，Genesis 在第一次 `scene.add_sensor(MyOptions(...))` 时会惰性导入兄弟模块 `my_sensor_plugin.sensor` 并解析配对。

## 选择基类

| Base | 何时使用 |
|---|---|
| `SimpleSensor[OptionsT, None, MetadataT]` | 绝大多数情况。标准逐步管线：raw -> physics imperfections -> transform -> hardware imperfections -> post-process -> delay sampling。 |
| `SimpleSensor[OptionsT, None, MetadataT, DataT]` | 与上面相同，但 `read()` 返回 `DataT` 这个 `NamedTuple`，而不是单个张量。IMU 是典型例子。 |
| `BaseCameraSensor[OptionsT]` | 相机式传感器，在 `read()` 时懒渲染 RGB 图像，例如光栅化、光线追踪、批量渲染或自定义渲染器。 |
| `Sensor[OptionsT, ContextT, MetadataT]` | 只有当标准管线都不适用时使用。你需要自己实现 `_update_shared_cache`；如果不使用 timeline rings，还要设置 `uses_ring_pipeline = False`。 |

第二个泛型参数是 shared context。没有上下文时写 `None`；多个不同传感器类型需要共享同一资源时，声明 `SharedSensorContext` 子类。

常用 mixin：

- `KinematicSensorOptionsMixin`：用于连接到 `KinematicEntity` 或只需要运动学信息的传感器。
- `RigidSensorOptionsMixin`：用于依赖刚体物理的传感器，例如接触、IMU、触觉。通常与 `SimpleSensorOptions` 多继承。
- 传感器侧的 `RigidSensorMixin` / `RigidSensorMetadataMixin` 会提供 typed `solver` 字段和常用 link bookkeeping。

## `SimpleSensor` 的 hook

所有 hook 都是 `@classmethod`，会接收 `shared_metadata` 以及需要填充的缓冲区。产生数据的 hook 还会收到 `shared_context`，没有上下文时为 `None`。hook 每步按传感器类调用一次，不会逐实例、逐环境调用。

### 必须重写

#### `_get_return_format(self) -> tuple[...]`

实例方法，返回 `read()` 的 shape。shape 按实例确定，因为传感器选项可能决定返回形状。

```python
def _get_return_format(self) -> tuple[int, ...]:
    return (3,)
```

约定：

- 单个张量返回 `(N,)`。
- 多张量返回使用 tuple of tuples，例如 IMU 的 `((3,), (3,), (3,))`，必须与 `DataT` 的字段匹配。

#### `_get_cache_dtype(cls) -> torch.dtype`

类方法，返回 `read()` 的 dtype。dtype 按类统一，不支持同一传感器类的不同实例返回不同 dtype。

```python
@classmethod
def _get_cache_dtype(cls) -> torch.dtype:
    return gs.tc_float
```

#### `_update_raw_data(cls, shared_context, shared_metadata, raw_data_T)`

传感器特定 kernel，计算该类所有传感器在当前时间步的**真实值**。输出缓冲区 `raw_data_T` 的形状为 `(cols, B)`，即列优先、batch 维在最后，以便不同传感器类共享 intermediate cache 时保持切片连续。必须原地填充这个缓冲区。

```python
@classmethod
def _update_raw_data(cls, shared_context, shared_metadata, raw_data_T):
    pos = shared_metadata.solver.get_links_pos(shared_metadata.links_idx)  # (B, N, 3)
    raw_data_T.copy_(pos.reshape(pos.shape[0], -1).T)                      # (3*N, B)
```

### 可选 hook

#### `_apply_transform(cls, shared_metadata, data, timeline, *, is_measured)`

在 `data` 上原地应用坐标变换或状态响应模型。每步调用两次：GT 分支 `is_measured=False`，measured 分支 `is_measured=True`。坐标变换通常两侧都执行；传感器元件特有的响应，例如 RC 时间常数或机械带宽，通常只在 `is_measured` 时执行。

```python
@classmethod
def _apply_transform(cls, shared_metadata, data, timeline, *, is_measured):
    data.copy_(transform_by_quat(data, shared_metadata.world_to_local_quat))

    if is_measured:
        prev = timeline.at(1)
        data.mul_(1 - shared_metadata.alpha).add_(prev, alpha=shared_metadata.alpha)
```

#### `_post_process(cls, shared_metadata, tensor, timeline, *, is_measured) -> torch.Tensor`

把 intermediate space 投影到 return space。需要阈值、clamp、mask、deadband、类型转换或形状变化时重写。返回的张量会写入 per-class return-space ring 的 slot 0。

```python
@classmethod
def _post_process(cls, shared_metadata, tensor, timeline, *, is_measured):
    return tensor > shared_metadata.thresholds
```

如果重写 `_post_process`，必须同时重写 `_get_intermediate_format` 或 `_get_intermediate_dtype`。即使 intermediate 与 return 的 shape/dtype 相同，也应写一个 no-op override 来显式声明 intermediate buffer 是独立语义空间。

#### `_get_intermediate_format(self) -> tuple[...]`

返回管线内部缓冲区的 shape。默认与 `_get_return_format()` 相同。只要 `_post_process` 改变 shape，或需要显式声明 intermediate space，都应重写。

```python
def _get_intermediate_format(self) -> tuple[int, ...]:
    return self._get_return_format()
```

#### `_get_intermediate_dtype(cls) -> torch.dtype`

返回管线内部缓冲区的 dtype。默认与 `_get_cache_dtype()` 相同。`ContactSensor` 这类“float 中间值，bool 返回值”的传感器应重写它。

```python
@classmethod
def _get_intermediate_dtype(cls) -> torch.dtype:
    return gs.tc_float
```

#### `_apply_physics_imperfections(cls, shared_metadata, measured_slot_0, timeline)`

在 measured ring 当前槽位上原地应用物理层误差，发生在 `_apply_transform` 之前。适用于仿真器未建模的底层物理现象波动。默认 no-op。需要把 raw 与物理噪声融合到单个 kernel pass 中时，重写 `_update_current_timestep_data`。

#### `_apply_hardware_imperfections(cls, shared_metadata, measured_slot_0)`

`SimpleSensor` 已经按嵌入式采样器语义实现了 `noise`、`bias`、`random_walk` 和 `resolution`。它们作用在每步 measured 工作缓冲区上，不写入 timeline ring。需要非标准误差模型时重写，通常先调用 `super()` 再添加自定义项。

```python
@classmethod
def _apply_hardware_imperfections(cls, shared_metadata, measured_slot_0):
    super()._apply_hardware_imperfections(shared_metadata, measured_slot_0)
    measured_slot_0 += torch.normal(0.0, shared_metadata.signal_noise_coeff) * measured_slot_0.abs()
```

#### `_update_current_timestep_data(...)`

默认行为是调用 `_update_raw_data` 生成 GT，镜像到 GT/measured timeline slot 0，然后对 measured slot 调用 `_apply_physics_imperfections`。如果某个传感器的物理噪声必须在同一个 kernel 内参与分支或命中计算，可以重写这个方法，同时写入 GT 和 measured 槽位。

#### `uses_ring_pipeline`

类级标志，声明该类是否参与 ring-based per-step pipeline。默认 `True`。直接继承 `Sensor` 且完全绕过 rings 的子类，例如相机，应设置：

```python
class MyCustomSensor(Sensor[MyOptions, None, MyMetadata]):
    uses_ring_pipeline: ClassVar[bool] = False
```

## Camera-style sensors via `BaseCameraSensor`

`BaseCameraSensor` 是直接继承 `Sensor` 的基类，封装了 Genesis 相机共享的“读取时懒渲染”模式。自定义图像渲染传感器应优先使用它。

优点：

- 每步懒渲染并缓存；同一步多次 `read()` 共享一次渲染。
- 支持用 `pos` / `lookat` / `up` 或显式 `offset_T` 连接到 link。
- 默认 RGB 输出形状为 `((h, w, 3),)`，dtype 为 `torch.uint8`，`read()` 返回 `CameraReturnType(rgb=...)`。
- 设置 `uses_ring_pipeline = False`，并拒绝 `delay > 0`、`jitter > 0`、`history_length > 0`，避免用户请求该类型无法支持的功能。

需要实现两个 hook：

```python
class MyCameraSensor(BaseCameraSensor[MyCameraOptions]):
    def _apply_camera_transform(self, camera_T: torch.Tensor) -> None:
        # camera_T 是 (4, 4) 世界坐标变换。把它应用到你的渲染器相机表示上。
        ...

    def _render_current_state(self) -> None:
        # 从当前姿态渲染场景，并写入该传感器在每类图像缓存中的槽位。
        # 每个仿真步、每个相机最多调用一次。
        ...
```

完整示例可参考 `RasterizerCameraSensor`。

限制：默认返回固定为 RGB `torch.uint8`。如果需要深度、分割、法线或非 RGB 输出，需要重写 `_get_return_format` / `_get_cache_dtype` 并调整缓存，或退回到直接继承 `Sensor`。
