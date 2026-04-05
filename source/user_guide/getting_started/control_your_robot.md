# 🕹️ 控制您的机器人

现在我们已经加载了机器人，接下来通过一个完整示例来展示控制机器人的各种方式。

像往常一样，让我们导入 Genesis，创建一个场景，并加载一个 Franka 机器人：
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
        camera_pos    = (0, -3.5, 2.5),
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

# 加载实体时，您可以在 morph 中指定其姿态
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
        pos   = (1.0, 1.0, 0.0),
        euler = (0, 0, 0),
    ),
)

########################## build ##########################
scene.build()
```

如果我们不给它任何驱动力，这个机器人手臂会因重力而下落。Genesis 内置了一个 PD 控制器（[比例-积分-微分控制器](https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller)），它以目标关节位置或速度作为输入。您也可以直接设置施加到每个关节的扭矩或力。

在机器人仿真领域，`joint`（关节）和 `dof`（自由度）是两个相关但不同的概念。Franka 手臂有 7 个旋转关节位于手臂部分，2 个平移关节位于夹爪部分，每个关节均为 1 个自由度，共同构成一个 9 自由度的关节体。在更一般的情况下，会有自由关节（6 自由度）或球关节（3 自由度）等具有多个自由度的关节类型。一般来说，您可以将每个自由度视为一个电机，可以独立控制。

为了知道要控制哪个关节（自由度），我们需要将我们在 URDF/MJCF 文件中定义的关节名称映射到仿真器内部的实际自由度索引：

```
jnt_names = [
    'joint1',
    'joint2',
    'joint3',
    'joint4',
    'joint5',
    'joint6',
    'joint7',
    'finger_joint1',
    'finger_joint2',
]
dofs_idx = [franka.get_joint(name).dof_idx_local for name in jnt_names]
```
注意这里我们使用 `.dof_idx_local` 来获取相对于机器人实体本身的局部自由度索引。您也可以使用 `joint.dof_idx` 来访问每个关节在场景中的全局自由度索引。

接下来，我们可以为每个自由度设置控制增益。这些增益决定了给定目标关节位置或速度时实际控制力的大小。通常这些信息会从导入的 MJCF 或 URDF 文件中解析，但建议手动调整或参考经过良好调试的参数值。

```python
############ Optional: set control gains ############
# 设置位置增益
franka.set_dofs_kp(
    kp             = np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local = dofs_idx,
)
# 设置速度增益
franka.set_dofs_kv(
    kv             = np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local = dofs_idx,
)
# 为安全设置力的范围
franka.set_dofs_force_range(
    lower          = np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    upper          = np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
    dofs_idx_local = dofs_idx,
)
```
注意这些 API 通常接受两组输入：要设置的实际值和相应的自由度索引。大多数与控制相关的 API 都遵循此约定。

接下来，让我们先看看如何手动设置机器人的配置，而不是使用物理真实的 PD 控制器。这些 API 可以瞬间改变机器人状态，而不遵循物理规律：

```python
# 硬重置
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()
```
如果您打开了查看器，您会看到机器人每 50 步变换一次姿态。

接下来，让我们尝试使用内置的 PD 控制器来控制机器人。Genesis 中的 API 设计遵循结构化模式。我们使用 `set_dofs_position` 来硬设置自由度位置。现在我们将 `set_*` 更改为 `control_*` 以使用控制器对应的 API。这里我们演示控制机器人的不同方式：
```python
# PD 控制
for i in range(1250):
    if i == 0:
        franka.control_dofs_position(
            np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 250:
        franka.control_dofs_position(
            np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 500:
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    elif i == 750:
        # 用速度控制第一个自由度，其余的用位置控制
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])[1:],
            dofs_idx[1:],
        )
        franka.control_dofs_velocity(
            np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0])[:1],
            dofs_idx[:1],
        )
    elif i == 1000:
        franka.control_dofs_force(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    # 这是基于给定控制命令计算的控制力
    # 如果使用力控制，它与给定的控制命令相同
    print('control force:', franka.get_dofs_control_force(dofs_idx))

    # 这是自由度实际受到的力
    print('internal force:', franka.get_dofs_force(dofs_idx))

    scene.step()
```
让我们深入了解一下：
- 从第 0 步到 500，我们使用位置控制来控制所有自由度，并按顺序将机器人移动到 3 个目标位置。注意，对于 `control_*` API，一旦设置了目标值，只要目标保持不变，您就不需要向仿真器在后续步骤中发送重复命令，它会内部存储。
- 在第 750 步，我们演示了可以对不同的自由度进行混合控制：对于第一个自由度（dof 0），我们发送速度命令，而其余的仍然遵循位置控制命令
- 在第 1000 步，我们切换到扭矩（力）控制并向所有自由度发送零力命令，机器人将再次落到地板上。

在每一步结束时，我们打印两种类型的力：`get_dofs_control_force()` 和 `get_dofs_force()`。
- `get_dofs_control_force()` 返回控制器施加的力。在位置或速度控制的情况下，这是使用目标命令和控制增益计算的。在力（扭矩）控制的情况下，这与输入的控制命令相同
- `get_dofs_force()` 返回每个自由度实际受到的力，这是控制器施加的力与其他内部力（如碰撞力和科里奥利力）的组合。

如果一切正常，这就是您应该看到的：

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/control_your_robot.mp4" type="video/mp4">
</video>


以下是涵盖上述所有内容的完整代码脚本：
```python
import numpy as np

import genesis as gs

########################## init ##########################
gs.init(backend=gs.gpu)

########################## create a scene ##########################
scene = gs.Scene(
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (0, -3.5, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 30,
        res           = (960, 640),
        max_FPS       = 60,
    ),
    sim_options = gs.options.SimOptions(
        dt = 0.01,
    ),
    show_viewer = True,
)

########################## entities ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
    ),
)
########################## build ##########################
scene.build()

jnt_names = [
    'joint1',
    'joint2',
    'joint3',
    'joint4',
    'joint5',
    'joint6',
    'joint7',
    'finger_joint1',
    'finger_joint2',
]
dofs_idx = [franka.get_joint(name).dof_idx_local for name in jnt_names]

############ Optional: set control gains ############
# 设置位置增益
franka.set_dofs_kp(
    np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
)
# 设置速度增益
franka.set_dofs_kv(
    np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
)
# 为安全设置力的范围
franka.set_dofs_force_range(
    np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
)
# 硬重置
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()

# PD 控制
for i in range(1250):
    if i == 0:
        franka.control_dofs_position(
            np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 250:
        franka.control_dofs_position(
            np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 500:
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    elif i == 750:
        # 用速度控制第一个自由度，其余的用位置控制
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])[1:],
            dofs_idx[1:],
        )
        franka.control_dofs_velocity(
            np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0])[:1],
            dofs_idx[:1],
        )
    elif i == 1000:
        franka.control_dofs_force(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    # 这是基于给定控制命令计算的控制力
    # 如果使用力控制，它与给定的控制命令相同
    print('control force:', franka.get_dofs_control_force(dofs_idx))

    # 这是自由度实际受到的力
    print('internal force:', franka.get_dofs_force(dofs_idx))

    scene.step()
```

## 使用吸盘进行拾取和放置

在许多工业环境中，机器人使用吸盘抓取物体，其行为类似于"即时"刚性抓取。在 Genesis 中，您可以通过暂时将两个刚体焊接在一起来重现相同的行为。

场景中的*rigid solver*（刚体求解器）通过 `add_weld_constraint()` 和 `delete_weld_constraint()` 让您直接访问此功能。该 API 接受两个 numpy 数组，列出要连接/分离的连杆索引。

下面是一个最小示例，将 Franka 末端执行器移动到一个小立方体上方，将两个主体焊接在一起（模仿吸附），将立方体运送到另一个姿态，最后再次释放它。

```python
import numpy as np
import genesis as gs

# --- （场景和机器人创建省略，与上面的部分相同） ---

# 向场景添加一个立方体实体
cube = scene.add_entity(
    gs.morphs.Box(
        size = (0.08, 0.08, 0.08),
        pos  = (0.65, 0.0, 0.13),
    )
)

# 获取一些常用的句柄
rigid        = scene.sim.rigid_solver   # 底层刚体求解器
end_effector = franka.get_link("hand")  # Franka 夹爪坐标系
cube_link    = cube.base_link           # 我们想要拾取的连杆

################ 到达预抓取姿态 ################
q_pregrasp = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.13]),  # 刚好在立方体上方
    quat = np.array([0, 1, 0, 0]),       # 朝下的方向
)
franka.control_dofs_position(q_pregrasp[:-2], np.arange(7))  # 仅手臂关节
for _ in range(50):
    scene.step()

################ 连接（激活吸附） ################
link_cube   = np.array([cube_link.idx],    dtype=gs.np_int)
link_franka = np.array([end_effector.idx], dtype=gs.np_int)
rigid.add_weld_constraint(link_cube, link_franka)

################ 抬起和运输 ################
q_lift = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.28]),  # 抬起
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(q_lift[:-2], np.arange(7))
for _ in range(50):
    scene.step()

q_place = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.4, 0.2, 0.18]),  # 目标放置姿态
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(q_place[:-2], np.arange(7))
for _ in range(100):
    scene.step()

################ 分离（释放吸附） ################
rigid.delete_weld_constraint(link_cube, link_franka)
for _ in range(400):
    scene.step()
```

几点说明：
1. 吸盘被建模为*理想的*焊接——不强制执行顺应性或力限制。如果您需要更物理真实的行为，您可以改为创建 `gs.constraints.DampedSpring` 或控制夹爪手指。
2. 连杆索引是**场景全局的**，因此我们将它们包装在单元素 numpy 数组中以满足 API 约定。
3. 您可以通过传递包含多个索引的数组来一次附加或分离多个对象。

只需两行代码，您现在就可以使用吸盘拾取和放置任意对象！请随意将此代码片段集成到您自己的控制流程中。
