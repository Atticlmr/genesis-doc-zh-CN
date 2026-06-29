# 🧭 IMU

`IMU` 传感器建模连接在刚体连杆上的惯性测量单元。它返回线性加速度、角速度和磁场，数据类型为 `NamedTuple`（`lin_acc`、`ang_vel`、`mag`），并支持可选的轴间耦合、噪声、漂移、延迟和抖动来模拟真实硬件。

完整示例脚本位于 `examples/sensors/imu_franka.py`。

## 场景设置

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu)

scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    sim_options=gs.options.SimOptions(dt=0.01),
    show_viewer=True,
)

scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))
end_effector = franka.get_link("hand")
motors_dof = (0, 1, 2, 3, 4, 5, 6)
```

## 添加 IMU 传感器

通过指定 `entity_idx` 和 `link_idx_local`，可以把 IMU 安装到末端执行器所在实体和连杆上：

```python
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=franka.idx,
        link_idx_local=end_effector.idx_local,
        pos_offset=(0.0, 0.0, 0.15),
        # 传感器特性
        acc_cross_axis_coupling=(0.0, 0.01, 0.02),
        gyro_cross_axis_coupling=(0.03, 0.04, 0.05),
        acc_noise=(0.01, 0.01, 0.01),
        gyro_noise=(0.01, 0.01, 0.01),
        acc_random_walk=(0.001, 0.001, 0.001),
        gyro_random_walk=(0.001, 0.001, 0.001),
        delay=0.01,
        jitter=0.01,
        draw_debug=True,
    )
)
```

IMU 构造函数提供以下选项：

- `pos_offset` - 传感器相对于连杆坐标系的位置。
- `acc_cross_axis_coupling` / `gyro_cross_axis_coupling` - 传感器错位或轴间耦合。
- `acc_noise` / `gyro_noise` - 每个轴上的高斯噪声。
- `acc_random_walk` / `gyro_random_walk` - 随时间累积的漂移。
- `delay` / `jitter` - 时序真实感。
- `draw_debug` - 在查看器中可视化传感器坐标系。

## 运动控制与仿真

```python
scene.build()

franka.set_dofs_kp(np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]))
franka.set_dofs_kv(np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]))

circle_center = np.array([0.4, 0.0, 0.5])
circle_radius = 0.15
rate = np.deg2rad(2.0)

def control_franka_circle_path(i):
    pos = circle_center + np.array([np.cos(i * rate), np.sin(i * rate), 0]) * circle_radius
    qpos = franka.inverse_kinematics(
        link=end_effector,
        pos=pos,
        quat=np.array([0, 1, 0, 0]),
    )
    franka.control_dofs_position(qpos[:-2], motors_dof)
    scene.draw_debug_sphere(pos, radius=0.01, color=(1.0, 0.0, 0.0, 0.5))

for i in range(1000):
    scene.step()
    control_franka_circle_path(i)
```

机器人在保持固定方向的同时绘制水平圆形轨迹。圆周运动会产生 IMU 可检测到的向心加速度，同时读数也会受到传感器朝向下重力投影的影响。

构建场景后，可以读取带误差的测量值和真实值：

```python
print("Ground truth data:")
print(imu.read_ground_truth())
print("Measured data:")
print(imu.read())
```

IMU 返回的 `NamedTuple` 字段包括：

- `lin_acc` - 线性加速度，单位 m/s^2（三维向量）。
- `ang_vel` - 角速度，单位 rad/s（三维向量）。
- `mag` - 磁场，单位 Tesla（三维向量）。

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/imu.mp4" type="video/mp4">
</video>
