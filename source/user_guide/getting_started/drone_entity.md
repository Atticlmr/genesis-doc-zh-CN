# 🚁 无人机实体

Genesis 提供专门的无人机仿真，包括螺旋桨物理和电机控制。

## 创建无人机

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01, gravity=(0, 0, -9.81)),
)

scene.add_entity(gs.morphs.Plane())

drone = scene.add_entity(
    morph=gs.morphs.Drone(
        file="urdf/drones/cf2x.urdf",
        model="CF2X",
        pos=(0.0, 0.0, 0.5),
    ),
)

scene.build()
```

## 无人机 Morph 选项

```python
gs.morphs.Drone(
    file="urdf/drones/cf2x.urdf",  # URDF 文件路径
    model="CF2X",                   # 模型: "CF2X", "CF2P", 或 "RACE"
    pos=(0.0, 0.0, 0.5),           # 初始位置
    euler=(0.0, 0.0, 0.0),         # 初始方向 (度)
    propellers_link_name=('prop0_link', 'prop1_link', 'prop2_link', 'prop3_link'),
    propellers_spin=(-1, 1, -1, 1), # 旋转方向: 1=逆时针, -1=顺时针
)
```

## 电机控制

通过 RPM（每分钟转数）控制螺旋桨：

```python
hover_rpm = 14475.8  # CF2X 的近似悬停 RPM
max_rpm = 25000.0

for step in range(1000):
    # 为每个螺旋桨设置 RPM [前左, 前右, 后左, 后右]
    rpms = np.array([hover_rpm, hover_rpm, hover_rpm, hover_rpm])

    # 添加差动推力以实现运动
    rpms[0] += 100  # 增加前左
    rpms[3] += 100  # 增加后右
    rpms = np.clip(rpms, 0, max_rpm)

    drone.set_propellels_rpm(rpms)  # 每步调用一次
    scene.step()
```

**重要：** `set_propellels_rpm()` 必须在每个仿真步骤中恰好调用一次。

## 物理模型

- **推力:** `F = KF × RPM²` (每个螺旋桨的垂直力)
- **扭矩:** `τ = KM × RPM² × spin_direction` (偏航力矩)
- **控制:**
  - 螺旋桨之间的差动推力 → 平移
  - 螺旋桨对之间的差动力矩 → 旋转

## 多环境

```python
scene.build(n_envs=32)

# 控制形状: (n_envs, n_propellers)
rpms = np.tile([hover_rpm] * 4, (32, 1))
drone.set_propellels_rpm(rpms)
```

## 可用模型

| 模型 | 文件 | 描述 |
|-------|------|-------------|
| CF2X | `urdf/drones/cf2x.urdf` | Crazyflie 2.0 X 配置 |
| CF2P | `urdf/drones/cf2p.urdf` | Crazyflie 2.0 Plus |
| RACE | `urdf/drones/racer.urdf` | 竞速无人机 |

## 示例：悬停控制

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
drone = scene.add_entity(gs.morphs.Drone(file="urdf/drones/cf2x.urdf", pos=(0, 0, 1)))
scene.build()

target_height = 1.0
kp = 5000.0

for _ in range(500):
    pos = drone.get_pos()[0]
    error = target_height - pos[2].item()

    base_rpm = 14475.8
    correction = kp * error
    rpms = np.clip([base_rpm + correction] * 4, 0, 25000)

    drone.set_propellels_rpm(rpms)
    scene.step()
```
## 下一章节

- [悬停环境](./hover_env) — 创建无人机悬停强化学习环境
- [运动控制](./locomotion) — 使用Genesis和强化学习训练locomotion策略