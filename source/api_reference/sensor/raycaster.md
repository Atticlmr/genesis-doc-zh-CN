# 射线投射传感器

`RaycasterSensor` 提供基于射线的距离测量，可用于 LiDAR 仿真、深度相机、接近感知和障碍物检测。

## 概述

射线投射传感器：

- 从传感器坐标系向场景中投射射线。
- 返回与几何体相交的命中点和距离。
- 支持可配置的射线模式，例如球面、深度相机和平面网格。
- 使用 GPU 加速的 BVH 遍历高效计算。

## 用法

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.add_entity(gs.morphs.Box(pos=(2, 0, 0.5), size=(1.0, 1.0, 1.0)))
sensor_link = robot.get_link("sensor_link")

lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=gs.sensors.SphericalPattern(
            fov=(360.0, 30.0),
            n_points=(1800, 16),
        ),
        entity_idx=robot.idx,
        link_idx_local=sensor_link.idx_local,
        max_range=10.0,
        min_range=0.1,
        return_world_frame=True,
    )
)

scene.build()

for i in range(100):
    scene.step()
    data = lidar.read()
    print(data.distances.min())
```

## 配置

```python
gs.sensors.Lidar(
    pattern=pattern,
    entity_idx=robot.idx,
    link_idx_local=sensor_link.idx_local,
    pos_offset=(0.0, 0.0, 0.0),
    euler_offset=(0.0, 0.0, 0.0),
    min_range=0.1,
    max_range=100.0,
    return_world_frame=True,
    draw_debug=True,
)
```

## 射线模式

### SphericalPattern（LiDAR）

```python
pattern = gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),
    n_points=(128, 32),
)
```

### DepthCameraPattern

```python
pattern = gs.sensors.DepthCameraPattern(
    res=(640, 480),
    fov_horizontal=87.0,
)
```

### GridPattern

```python
pattern = gs.sensors.GridPattern(
    resolution=0.1,
    size=(2.0, 2.0),
    direction=(0.0, 0.0, -1.0),
)
```

## 输出格式

`Lidar.read()` 和 `DepthCamera.read()` 返回 `RaycasterReturnType`：

| 字段 | 形状 | 描述 |
|--------|-------|-------------|
| `points` | `([n_envs,] *shape, 3)` | 命中点坐标 |
| `distances` | `([n_envs,] *shape)` | 到交点的距离；无命中时为 `max_range` |

`DepthCamera` 还提供 `read_image()`，直接返回形状为 `([n_envs,] H, W)` 的深度图。

## 性能

Raycaster 使用 GPU 加速的 BVH 遍历进行射线-场景相交计算：

- 随场景复杂度扩展良好。
- 可高效处理数百到数千条射线。
- 支持并行环境中的批处理。

## API 参考

```{eval-rst}
.. autoclass:: genesis.engine.sensors.RaycasterSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 传感器概述
- {doc}`camera` - 视觉传感
