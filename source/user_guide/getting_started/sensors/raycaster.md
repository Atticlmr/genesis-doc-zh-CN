# 📡 光线投射传感器

`Raycaster` 家族通过向场景投射光线并检测与几何体的交点来测量距离。具体传感器包括 `Lidar`（返回完整的光线命中集合）和 `DepthCamera`（把命中结果格式化为深度图像）。光线数量和方向由 `RaycastPattern` 控制。

## Lidar 和 DepthCamera

```python
lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=gs.sensors.SphericalPattern(),
        entity_idx=robot.idx,        # 连接到刚体实体
        pos_offset=(0.3, 0.0, 0.1),  # 相对于连接实体的偏移
        return_world_frame=True,     # 返回世界坐标系下的点，否则返回局部坐标系
    )
)

depth_camera = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=gs.sensors.DepthCameraPattern(
            res=(480, 360),          # 图像分辨率（宽，高）
            fov_horizontal=90,       # 视场角，单位为度
            fov_vertical=40,
        ),
    )
)

scene.build()
scene.step()

lidar.read()                # NamedTuple(points=..., distances=...)
depth_camera.read_image()   # 距离张量，形状为 (height, width)
```

示例脚本 `examples/sensors/lidar_teleop.py` 展示了安装在机器人上的光线投射传感器。将 `--pattern` 设为 `spherical` 可得到类似 LiDAR 的模式，设为 `grid` 可得到平面网格模式，设为 `depth` 可得到深度相机。

运行 `python examples/sensors/lidar_teleop.py --pattern depth` 的效果如下：

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/depth_camera.mp4" type="video/mp4">
</video>

## 通用选项

```python
gs.sensors.Lidar(
    pattern=pattern,
    entity_idx=robot.idx,
    pos_offset=(0.0, 0.0, 0.15),
    euler_offset=(0.0, 0.0, 0.0),
    max_range=100.0,
    min_range=0.1,
    return_world_frame=True,
    draw_debug=True,
)
```

## 模式

| Pattern | 使用场景 |
|---|---|
| `SphericalPattern` | 3D LiDAR（Velodyne、Ouster） |
| `DepthCameraPattern` | 深度相机（RealSense、Kinect） |
| `GridPattern` | 平面感知、高度图 |

### SphericalPattern（LiDAR）

```python
# 360° 水平视场角，60° 垂直视场角
pattern = gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),
    n_points=(128, 32),
)

lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=pattern,
        entity_idx=robot.idx,
        pos_offset=(0.0, 0.0, 0.15),
        max_range=100.0,
        min_range=0.1,
        draw_debug=True,
    )
)
```

参数：

```python
gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),               # (水平, 垂直) 角度
    n_points=(128, 64),              # (水平, 垂直) 光线数量
    angular_resolution=(0.25, 0.5),  # 另一种写法：每条光线对应的角度
    angles=(h_angles, v_angles),     # 自定义角度数组
)
```

真实 LiDAR 配置示例：

```python
# Velodyne VLP-16
velodyne = gs.sensors.SphericalPattern(fov=(360.0, 30.0), n_points=(1800, 16))

# 前向 120° 视场角
front_lidar = gs.sensors.SphericalPattern(fov=((-60, 60), 30.0), n_points=(128, 32))
```

### DepthCameraPattern

```python
pattern = gs.sensors.DepthCameraPattern(
    res=(640, 480),
    fov_horizontal=87.0,
)

depth_cam = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=pattern,
        entity_idx=robot.idx,
        pos_offset=(0.0, 0.0, 0.05),
        max_range=5.0,
    )
)
```

参数：

```python
gs.sensors.DepthCameraPattern(
    res=(640, 480),         # 分辨率（宽，高）
    fov_horizontal=90.0,    # 水平视场角
    fov_vertical=None,      # 根据宽高比自动计算
    fx=None, fy=None,       # 焦距，可覆盖 FOV
    cx=None, cy=None,       # 主点
)
```

### GridPattern

平行光线组成的平面网格：

```python
pattern = gs.sensors.GridPattern(
    resolution=0.1,             # 10 cm 间距
    size=(2.0, 2.0),            # 2 m x 2 m 网格
    direction=(0.0, 0.0, -1.0), # 指向下方
)
```

## 读取数据

```python
data = lidar.read()
points = data.points         # shape: (n_h, n_v, 3)
distances = data.distances   # shape: (n_h, n_v)

depth_image = depth_cam.read_image()  # shape: (H, W)
```

## 多环境

```python
scene.build(n_envs=4)
data = lidar.read()
print(data.points.shape)  # (4, n_h, n_v, 3)
```
