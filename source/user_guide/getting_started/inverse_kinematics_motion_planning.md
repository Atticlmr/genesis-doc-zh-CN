# 🦾 逆运动学与运动规划

在本教程中，我们将通过几个示例演示如何在 Genesis 中使用逆运动学（IK）和运动规划求解器，并执行一个简单的抓取任务。

首先，让我们创建一个场景，加载您最喜欢的机械臂和一个小立方体，构建场景，然后设置控制增益：
```python
import numpy as np
import genesis as gs

########################## init ##########################
gs.init(backend=gs.gpu)

########################## create a scene ##########################
scene = gs.Scene(
    sim_options = gs.options.SimOptions(
        dt = 0.01,
    ),
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (3, -1, 1.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 30,
        max_FPS       = 60,
    ),
    show_viewer = True,
)

########################## entities ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
cube = scene.add_entity(
    gs.morphs.Box(
        size = (0.04, 0.04, 0.04),
        pos  = (0.65, 0.0, 0.02),
    )
)
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)
########################## build ##########################
scene.build()

motors_dof = np.arange(7)
fingers_dof = np.arange(7, 9)

# 设置控制增益
# 注意：以下值是针对 Franka 实现最佳行为而调整的
# 通常，每个新机器人都会有一组不同的参数。
# 有时高质量的 URDF 或 XML 文件也会提供这些参数并会被解析。
franka.set_dofs_kp(
    np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
)
franka.set_dofs_kv(
    np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
)
franka.set_dofs_force_range(
    np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
)
```

```{figure} ../../_static/images/IK_mp_grasp.png
```
接下来，让我们将机器人的末端执行器移动到预抓取姿态。这通过两个步骤完成：
- 使用 IK 求解给定目标末端执行器姿态的关节位置
- 使用运动规划器到达目标位置
  
Genesis 中的运动规划使用 OMPL 库。您可以按照[安装](../overview/installation.md)页面中的说明进行安装。

Genesis 中的 IK 和运动规划尽可能简单：每个都可以通过单个函数调用来完成。
```python

# 获取末端执行器连杆
end_effector = franka.get_link('hand')

# 移动到预抓取姿态
qpos = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.25]),
    quat = np.array([0, 1, 0, 0]),
)
# 夹爪打开位置
qpos[-2:] = 0.04
path = franka.plan_path(
    qpos_goal     = qpos,
    num_waypoints = 200, # 2 秒持续时间
)
# 执行规划的路径
for waypoint in path:
    franka.control_dofs_position(waypoint)
    scene.step()

# 允许机器人到达最后一个路径点
for i in range(100):
    scene.step()

```
如您所见，IK 求解和运动规划都是机器人实体的集成方法。对于 IK 求解，您只需告诉机器人的 IK 求解器哪个连杆是末端执行器，并指定目标姿态。然后，您告诉运动规划器目标关节位置（qpos），它将返回一个规划并平滑的路径点列表。注意，在执行路径后，我们让控制器再运行 100 步。这是因为我们使用 PD 控制器，期望目标位置与当前位置之间会存在差距。因此，我们让控制器运行更长时间，以便机器人能够到达规划轨迹中的最后一个路径点。

接下来，我们向下移动机器人夹爪，抓取立方体，并将其抬起：
```python
# 到达
qpos = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.130]),
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)
for i in range(100):
    scene.step()

# 抓取
franka.control_dofs_position(qpos[:-2], motors_dof)
franka.control_dofs_force(np.array([-0.5, -0.5]), fingers_dof)

for i in range(100):
    scene.step()

# 抬起
qpos = franka.inverse_kinematics(
    link=end_effector,
    pos=np.array([0.65, 0.0, 0.28]),
    quat=np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)
for i in range(200):
    scene.step()
```
抓取物体时，我们对 2 个夹爪自由度使用了力控制，并施加了 0.5N 的抓取力。如果一切正常，您会看到物体被抓取并抬起。


## 下一章节

- [高级 IK](./advanced_ik) — 多目标 IK、零空间控制和求解器调优
- [约束](./constraints) — 运行时焊接和连接约束以锁定连杆
- [路径规划](./path_planning) — 使用 RRT 的无碰撞运动规划