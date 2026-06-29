# IMU 传感器

`IMUSensor`（惯性测量单元）提供用于机器人状态估计的加速度计、陀螺仪和磁力计读数。

## 概述

IMU 传感器测量：

- **线加速度**：包含重力影响的 3D 加速度。
- **角速度**：3D 旋转速度。
- **磁场**：3D 磁场向量。

## 用法

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="quadruped.urdf"))
base = robot.get_link("base_link")

# 添加 IMU 到机器人基座
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=robot.idx,
        link_idx_local=base.idx_local,
        pos_offset=(0.0, 0.0, 0.15),
    )
)

scene.build()

# 仿真循环
for i in range(1000):
    scene.step()

    # 获取 IMU 读数（IMUReturnType NamedTuple）
    data = imu.read()
    accel = data.lin_acc  # ([n_envs,] 3) 加速度，单位 m/s^2
    gyro = data.ang_vel   # ([n_envs,] 3) 角速度，单位 rad/s
    mag = data.mag        # ([n_envs,] 3) 磁场，单位 Tesla
```

## 配置

```python
gs.sensors.IMU(
    # 连接参数（继承自 RigidSensorOptionsMixin）
    entity_idx=robot.idx,             # 全局 entity 索引
    link_idx_local=base.idx_local,    # 局部 link 索引
    pos_offset=(0.0, 0.0, 0.0),       # 相对于 link 坐标系的位置偏移
    euler_offset=(0.0, 0.0, 0.0),     # 相对于 link 坐标系的旋转偏移（度）

    # 加速度计参数
    acc_noise=(0.01, 0.01, 0.01),              # 每轴白噪声标准差 (m/s^2)
    acc_random_walk=(0.001, 0.001, 0.001),     # 每轴偏置漂移标准差 (m/s^3)
    acc_bias=(0.0, 0.0, 0.0),                  # 每轴常量偏置
    acc_cross_axis_coupling=0.0,               # 轴间耦合/错位
    acc_resolution=0.0,                        # 测量分辨率，0 表示不量化

    # 陀螺仪参数
    gyro_noise=(0.01, 0.01, 0.01),             # 每轴白噪声标准差 (rad/s)
    gyro_random_walk=(0.001, 0.001, 0.001),    # 每轴偏置漂移标准差 (rad/s^2)
    gyro_bias=(0.0, 0.0, 0.0),                 # 每轴常量偏置
    gyro_cross_axis_coupling=0.0,              # 轴间耦合/错位
    gyro_resolution=0.0,                       # 测量分辨率，0 表示不量化

    # 磁力计参数
    mag_noise=(0.0, 0.0, 0.0),
    mag_random_walk=(0.0, 0.0, 0.0),
    mag_bias=(0.0, 0.0, 0.0),
    mag_cross_axis_coupling=0.0,
    mag_resolution=0.0,

    # 时序
    delay=0.0,
    jitter=0.0,

    draw_debug=True,
)
```

## 输出格式

`read()` 和 `read_ground_truth()` 都返回 `IMUReturnType` NamedTuple：

| 字段 | 类型 | 形状 | 描述 |
|-------|------|-------|-------------|
| `lin_acc` | `torch.Tensor` (float32) | `([n_envs,] 3)` | 传感器局部坐标系下的线加速度 (m/s^2) |
| `ang_vel` | `torch.Tensor` (float32) | `([n_envs,] 3)` | 传感器局部坐标系下的角速度 (rad/s) |
| `mag` | `torch.Tensor` (float32) | `([n_envs,] 3)` | 传感器局部坐标系下的磁场向量 (Tesla) |

`read()` 会应用已配置的噪声、偏置、随机游走和轴间耦合。`read_ground_truth()` 返回无噪声值。

## 噪声建模

### 加速度计噪声

| 参数 | 描述 | 典型值 |
|-----------|-------------|---------------|
| `acc_noise` | 白噪声标准差 | 0.001-0.01 m/s^2 |
| `acc_random_walk` | 偏置漂移标准差 | 0.0001-0.001 m/s^3 |

### 陀螺仪噪声

| 参数 | 描述 | 典型值 |
|-----------|-------------|---------------|
| `gyro_noise` | 白噪声标准差 | 0.0001-0.001 rad/s |
| `gyro_random_walk` | 偏置漂移标准差 | 0.00001-0.0001 rad/s^2 |

## 示例：四足机器人状态估计

```python
import genesis as gs
import torch

gs.init()
scene = gs.Scene()
quadruped = scene.add_entity(gs.morphs.URDF(file="go2.urdf"))
base = quadruped.get_link("base")

imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=quadruped.idx,
        link_idx_local=base.idx_local,
    )
)

scene.build()

velocity_estimate = torch.zeros(3, device=gs.device)
dt = scene.dt

for i in range(1000):
    scene.step()
    data = imu.read()
    velocity_estimate += data.lin_acc * dt
```

## API 参考

```{eval-rst}
.. autoclass:: genesis.engine.sensors.IMUSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 传感器概述
- {doc}`contact` - 接触力传感
