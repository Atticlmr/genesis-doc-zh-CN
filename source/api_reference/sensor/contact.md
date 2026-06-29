# 接触传感器

Genesis 提供用于检测接触和测量接触力的传感器。这些传感器适用于操作、抓取以及理解物理交互。

## ContactForceSensor

`ContactForceSensor` 测量施加在关联刚体连杆上的总接触力，并以该连杆的局部坐标系返回。

### 用法

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="gripper.urdf"))
finger = robot.get_link("finger_link")

# 添加接触力传感器到夹爪手指
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        entity_idx=robot.idx,
        link_idx_local=finger.idx_local,
    )
)

scene.build()

for i in range(1000):
    scene.step()

    # 获取接触力；返回普通 tensor，不是 NamedTuple
    force = contact_sensor.read()  # ([n_envs,] 3)，单位 Newton
    print(f"Contact force: {force}")
```

### 配置

```python
gs.sensors.ContactForce(
    entity_idx=robot.idx,            # 全局 entity 索引
    link_idx_local=finger.idx_local, # 局部 link 索引
    pos_offset=(0.0, 0.0, 0.0),      # 相对于 link 坐标系的位置偏移
    euler_offset=(0.0, 0.0, 0.0),    # 旋转偏移（度）
    min_force=0.0,                   # 每轴最小可检测绝对力，低于该值返回 0
    max_force=float("inf"),          # 每轴最大输出绝对力，超过该值会裁剪
    noise=0.0,                       # 白噪声标准差
    bias=0.0,                        # 常量加性偏置
    draw_debug=True,
)
```

### 输出格式

`read()` 返回普通 `torch.Tensor` (float32)：

| 形状 | 描述 |
|-------|-------------|
| `([n_envs,] 3)` | 局部 link 坐标系中的总接触力，单位 Newton |

## ContactSensor

`ContactSensor` 检测关联刚体连杆是否处于接触状态，返回布尔值。

### 用法

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

contact = scene.add_sensor(
    gs.sensors.Contact(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("base").idx_local,
    )
)

scene.build()
scene.step()
in_contact = contact.read()  # ([n_envs,] 1) bool tensor
```

### 输出格式

`read()` 返回普通 `torch.Tensor` (bool)：

| 形状 | 描述 |
|-------|-------------|
| `([n_envs,] 1)` | link 处于接触时为 True |

## API 参考

### ContactForceSensor

```{eval-rst}
.. autoclass:: genesis.engine.sensors.ContactForceSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

### ContactSensor

```{eval-rst}
.. autoclass:: genesis.engine.sensors.ContactSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 传感器概述
- {doc}`/api_reference/entity/rigid_entity/index` - RigidEntity 和连杆
