# 🔒 约束

Genesis 支持用于操作任务（如吸盘抓取）的运行时约束。

## Weld 约束

Weld 约束将两个 link 刚性连接在一起（6 DOF 约束）。

### 添加 Weld 约束

```python
import genesis as gs
import numpy as np

scene = gs.Scene()
franka = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
cube = scene.add_entity(gs.morphs.Box(pos=(0.65, 0, 0.02), size=(0.04, 0.04, 0.04)))
scene.build()

# 获取 link 句柄
rigid = scene.sim.rigid_solver
end_effector = franka.get_link("hand")
cube_link = cube.base_link

# 创建约束数组
link_cube = np.array([cube_link.idx], dtype=gs.np_int)
link_franka = np.array([end_effector.idx], dtype=gs.np_int)

# 添加 weld 约束（吸盘接合）
rigid.add_weld_constraint(link_cube, link_franka)
```

### 移除 Weld 约束

```python
# 释放物体
rigid.delete_weld_constraint(link_cube, link_franka)
```

## 吸盘示例

```python
# 移动到物体
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.65, 0.0, 0.13]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(50):
    scene.step()

# 连接（吸盘开启）
rigid.add_weld_constraint(link_cube, link_franka)

# 抬起
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.65, 0.0, 0.28]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(100):
    scene.step()

# 放置
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.4, 0.2, 0.13]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(100):
    scene.step()

# 释放（吸盘关闭）
rigid.delete_weld_constraint(link_cube, link_franka)
```

## 多环境约束

```python
scene.build(n_envs=4)

# 向特定环境添加约束
rigid.add_weld_constraint(link_cube, link_franka, envs_idx=(0, 1, 2))

# 从子集删除
rigid.delete_weld_constraint(link_cube, link_franka, envs_idx=(0, 1))
```

## Connect 约束

Connect 约束强制执行仅位置重合（3 DOF），允许相对旋转。

```xml
<!-- 在 MJCF/URDF 中 -->
<equality>
    <connect name="ball_joint" body1="link_1" body2="link_2" anchor="0 0 1" />
</equality>
```

## 查询活动约束

```python
constraints = rigid.get_weld_constraints()
print(constraints)  # 活动约束对
```

## 约束属性

- **Weld**: 完整 6-DOF 约束（平移 + 旋转）
- **Connect**: 3-DOF 约束（仅平移）
- **即时**: 无受力限制或顺应性
- **运行时**: 可以动态添加/移

## 下一章节
- [控制您的机器人](./control_your_robot) — 关节控制，位置，速度和力控
- [逆运动学和运动规划](./inverse_kinematics_motion_planning) — IK求解和 pick-and-place 工作流
