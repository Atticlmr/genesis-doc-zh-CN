# Sensors

Genesis 提供多种传感器用于感知仿真状态。传感器会连接到实体或场景上，并返回视觉观测、接触、惯性、光线投射、接近距离和温度等数据。

## 概览

可用的传感器类型：

| Sensor | 返回类型 | 字段 | 形状 |
|--------|-------------|--------|-------|
| **Camera** | `CameraReturnType` | `rgb` (uint8) | `([n_envs,] h, w, 3)` |
| **ContactSensor** | `torch.Tensor` (bool) | - | `([n_envs,] 1)` |
| **ContactForceSensor** | `torch.Tensor` (float32) | - | `([n_envs,] 3)` |
| **IMUSensor** | `IMUReturnType` | `lin_acc`, `ang_vel`, `mag` (float32) | 每个字段 `([n_envs,] 3)` |
| **RaycasterSensor** | `RaycasterReturnType` | `points`, `distances` (float32) | `([n_envs,] *shape, 3)`, `([n_envs,] *shape)` |
| **DepthCameraSensor** | `RaycasterReturnType` | `points`, `distances` (float32) | `([n_envs,] h, w, 3)`, `([n_envs,] h, w)` |
| **ProximitySensor** | `torch.Tensor` (float32) | - | `([n_envs,] n_probes)` |
| **KinematicContactProbe** | `KinematicContactProbeData` | `penetration`, `force` (float32) | `([n_envs,] n_probes)`, `([n_envs,] n_probes, 3)` |
| **ElastomerDisplacementSensor** | `torch.Tensor` (float32) | - | `([n_envs,] n_probes, 3)` |
| **TemperatureGridSensor** | `torch.Tensor` (float32) | - | `([n_envs,] nx, ny, nz)` |

## 快速开始

### 添加 Sensors

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
end_effector = robot.get_link("end_effector")
base = robot.get_link("base_link")

# Camera sensor（通过 add_camera）
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

# 末端执行器上的接触力 sensor
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        entity_idx=robot.idx,
        link_idx_local=end_effector.idx_local,
    )
)

# IMU sensor
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=robot.idx,
        link_idx_local=base.idx_local,
    )
)

scene.build()
```

### 读取 Sensor 数据

```python
scene.step()

# Camera
rgb, _, _, _ = cam.render(rgb=True)
_, depth, _, _ = cam.render(depth=True)

# 接触力
force = contact_sensor.read()

# IMU
imu_data = imu.read()
acceleration = imu_data.lin_acc
angular_velocity = imu_data.ang_vel
```

## Sensor 类型

```{toctree}
:titlesonly:

camera
contact
imu
raycaster
```

## 另请参阅

- {doc}`/api_reference/visualization/index` - 可视化系统
- {doc}`/api_reference/entity/index` - 向 entities 添加 sensors
