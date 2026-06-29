# 🖲️ 传感器

在 Genesis 中，传感器从场景中提取信息，但不会影响场景本身。传感器建模的是机器人控制视角下的板载传感器：每个传感器可以按自己的频率采样，带有可选的噪声、漂移、延迟和抖动，并以张量形式读出。在同一个控制步内多次调用 `read()` 是幂等的，会返回同一个值。

在选项中设置 `history_length=N` 会返回最近 `N` 个快照，并在新轴上堆叠，形状变为 `(B, N, *return_shape)`，索引 0 表示当前快照。每个快照保留采样时的误差状态，因此延迟读数在物理上保持一致。

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="urdf/go2/urdf/go2.urdf"))

contact = scene.add_sensor(
    gs.sensors.Contact(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("FL_foot").idx_local,
        history_length=4,   # 省略或设为 0 时只返回当前快照
        draw_debug=True,
    )
)

scene.build(n_envs=16)
for _ in range(1000):
    scene.step()

    # 带误差的测量值，形状为 (16, 4, 1)。
    is_touching = contact.read()

    # 无噪声的真实值，形状相同。
    is_touching_gt = contact.read_ground_truth()
```

对于高吞吐 RL 或日志记录，`scene.read_sensors()` 和 `entity.read_sensors()` 会按传感器类别批量返回张量；每个类别只需要一次批量调用。最后一个轴会把该类别所有传感器展平拼接起来。对于返回 `NamedTuple` 的传感器，字段按顺序打包，例如一个 IMU 会贡献 `lin_acc + ang_vel + mag = 9` 个标量。只要该类别中任一传感器设置了 `history_length > 0`，返回张量就会包含 history 轴。

```python
# dict[sensor_class, tensor]
data = scene.read_sensors()

# IMU 类没有 history：形状为 (B, N_imus * 9)。
imu_batch = data[gs.sensors.types.IMU]

# 上面的 Contact 传感器设置了 history_length=4：形状为 (B, 4, N_contacts)。
contact_batch = data[gs.sensors.types.Contact]
```

如需了解传感器管线设计或如何添加自定义传感器，请参见 {doc}`扩展 Genesis → 传感器 <../../advanced_topics/sensors/index>`。

示例脚本位于 `examples/sensors/`。

## 传感器族

- [**🧭 IMU**](imu) - 带噪声、漂移、延迟和抖动的加速度计、陀螺仪和磁力计。
- [**🫳 接触与触觉**](contact_and_tactile) - 布尔接触、接触力、基于穿透的探针和弹性体位移。
- [**📡 光线投射传感器**](raycaster) - 使用 `SphericalPattern`、`DepthCameraPattern`、`GridPattern` 的 LiDAR 和深度相机。
- [**🎥 相机传感器**](camera_sensors) - 用于 RGB、深度、分割和法线的光栅化器、光线追踪器和 Madrona 批量渲染器。
- [**📏 接近传感器**](proximity) - 查询到被跟踪网格表面的最近距离。
- [**🌡️ 温度网格**](temperature_grid) - 刚体连杆上的体素化温度场，支持传导、辐射和对流。

如需将传感器数据与仿真一起保存，请参见 [记录器](../recorders)。

```{toctree}
:hidden:
:maxdepth: 1

imu
contact_and_tactile
raycaster
camera_sensors
proximity
temperature_grid
```
