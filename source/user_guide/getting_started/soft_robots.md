# 🐛 软体机器人

## 体积肌肉仿真

Genesis 支持使用 MPM 和 FEM 进行软体机器人的体积肌肉仿真。在以下示例中，我们演示了一个非常简单的软体机器人，具有球形体，由正弦波控制信号驱动。

```python
import numpy as np
import genesis as gs


########################## init ##########################
gs.init(seed=0, precision='32', logging_level='info')

########################## create a scene ##########################
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt = 5e-4,
        substeps=10,
        gravity=(0, 0, 0),
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 0, 0.8),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(-1.0, -1.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
    ),
    fem_options=gs.options.FEMOptions(
        damping=45.0,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=False,
    ),
)

########################## entities ##########################
scene.add_entity(morph=gs.morphs.Plane())

E, nu = 3.e4, 0.45
rho = 1000.

robot_mpm = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.5, 0.2, 0.3),
        radius=0.1,
    ),
    material=gs.materials.MPM.Muscle(
        E=E,
        nu=nu,
        rho=rho,
        model='neohooken',
    ),
)

robot_fem = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.5, -0.2, 0.3),
        radius=0.1,
    ),
    material=gs.materials.FEM.Muscle(
        E=E,
        nu=nu,
        rho=rho,
        model='stable_neohooken',
    ),
)

########################## build ##########################
scene.build()

########################## run ##########################
scene.reset()
for i in range(1000):
    actu = np.array([0.2 * (0.5 + np.sin(0.01 * np.pi * i))])

    robot_mpm.set_actuation(actu)
    robot_fem.set_actuation(actu)
    scene.step()
```

您会看到：

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/muscle.mp4" type="video/mp4">
</video>

与实例化常规可变形实体相比，大部分代码都非常标准。只有两个小区别实现了这个效果：

* 实例化软体机器人 `robot_mpm` 和 `robot_fem` 时，我们分别使用材质 `gs.materials.MPM.Muscle` 和 `gs.materials.FEM.Muscle`。
* 在步进仿真时，我们使用 `robot_mpm.set_actuation` 或 `robot_fem.set_actuation` 来设置肌肉的驱动。

默认情况下，只有一个肌肉横跨整个机器人身体，肌肉方向垂直于地面 `[0, 0, 1]`。

在下一个示例中，我们展示如何通过设置肌肉组和方向来仿真蠕虫向前爬行，如下所示。（完整脚本可在 [tutorials/advanced_worm.py](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/examples/tutorials/advanced_worm.py) 找到。）

```python
########################## entities ##########################
worm = scene.add_entity(
    morph=gs.morphs.Mesh(
        file='meshes/worm/worm.obj',
        pos=(0.3, 0.3, 0.001),
        scale=0.1,
        euler=(90, 0, 0),
    ),
    material=gs.materials.MPM.Muscle(
        E=5e5,
        nu=0.45,
        rho=10000.,
        model='neohooken',
        n_groups=4,
    ),
)

########################## set muscle ##########################
def set_muscle_by_pos(robot):
    if isinstance(robot.material, gs.materials.MPM.Muscle):
        pos = robot.get_state().pos
        n_units = robot.n_particles
    elif isinstance(robot.material, gs.materials.FEM.Muscle):
        pos = robot.get_state().pos[robot.get_el2v()].mean(1)
        n_units = robot.n_elements
    else:
        raise NotImplementedError

    pos = pos.cpu().numpy()
    pos_max, pos_min = pos.max(0), pos.min(0)
    pos_range = pos_max - pos_min

    lu_thresh, fh_thresh = 0.3, 0.6
    muscle_group = np.zeros((n_units,), dtype=int)
    mask_upper = pos[:, 2] > (pos_min[2] + pos_range[2] * lu_thresh)
    mask_fore = pos[:, 1] < (pos_min[1] + pos_range[1] * fh_thresh)
    muscle_group[ mask_upper &  mask_fore] = 0 # upper fore body
    muscle_group[ mask_upper & ~mask_fore] = 1 # upper hind body
    muscle_group[~mask_upper &  mask_fore] = 2 # lower fore body
    muscle_group[~mask_upper & ~mask_fore] = 3 # lower hind body

    muscle_direction = np.array([[0, 1, 0]] * n_units, dtype=float)

    robot.set_muscle(
        muscle_group=muscle_group,
        muscle_direction=muscle_direction,
    )

set_muscle_by_pos(worm)

########################## run ##########################
scene.reset()
for i in range(1000):
    actu = np.array([0, 0, 0, 1. * (0.5 + np.sin(0.005 * np.pi * i))])

    worm.set_actuation(actu)
    scene.step()
```

您会看到：

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/worm.mp4" type="video/mp4">
</video>

这段代码片段中有几点值得注意：

* 在指定材质 `gs.materials.MPM.Muscle` 时，我们设置了一个额外的参数 `n_groups = 4`，这意味着这个机器人最多可以有 4 个不同的肌肉。
* 我们可以通过调用 `robot.set_muscle` 来设置肌肉，它接受 `muscle_group` 和 `muscle_direction` 作为输入。两者的长度都与 `n_units` 相同，在 MPM 中 `n_units` 是粒子数，而在 FEM 中 `n_units` 是单元数。`muscle_group` 是一个整数数组，范围从 `0` 到 `n_groups - 1`，表示机器人身体的某个单元属于哪个肌肉组。`muscle_direction` 是一个浮点数数组，指定肌肉方向的向量。注意我们不进行归一化，因此您可能需要确保输入的 `muscle_direction` 已经归一化。
* 在这个蠕虫示例中，我们设置肌肉的方式是简单地将身体分成四部分：上前部、上后部、下前部和下后部，使用 `lu_thresh` 作为下/上的阈值，`fh_thresh` 作为前/后的阈值。
* 现在给定四个肌肉组，当通过 `set_actuation` 设置控制时，驱动输入的形状为 `(4,)`。


## 混合（刚-软）机器人

另一种软体机器人是使用刚体内骨骼来驱动软体外皮肤，或者更准确地说，混合机器人。由于 Genesis 已经实现了刚体和软体动力学，因此也支持混合机器人。以下示例是一个具有两连杆骨骼的混合机器人，包裹软皮肤推动一个刚体球。

```python
import numpy as np
import genesis as gs


########################## init ##########################
gs.init(seed=0, precision='32', logging_level='info')

######################## create a scene ##########################
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=3e-3,
        substeps=10,
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 1.3, 0.5),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    rigid_options=gs.options.RigidOptions(
        gravity=(0, 0, -9.8),
        enable_collision=True,
        enable_self_collision=False,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound=( 0.0,  0.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
        gravity=(0, 0, 0), # mimic gravity compensation
        enable_CPIC=True,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,
        visualize_mpm_boundary=False,
    ),
)

########################## entities ##########################
scene.add_entity(morph=gs.morphs.Plane())

robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="urdf/simple/two_link_arm.urdf",
        pos=(0.5, 0.5, 0.3),
        euler=(0.0, 0.0, 0.0),
        scale=0.2,
        fixed=True,
    ),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(
            gravity_compensation=1.,
        ),
        material_soft=gs.materials.MPM.Muscle( # to allow setting group
            E=1e4,
            nu=0.45,
            rho=1000.,
            model='neohooken',
        ),
        thickness=0.05,
        damping=1000.,
        func_instantiate_rigid_from_soft=None,
        func_instantiate_soft_from_rigid=None,
        func_instantiate_rigid_soft_association=None,
    ),
)

ball = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.8, 0.6, 0.1),
        radius=0.1,
    ),
    material=gs.materials.Rigid(rho=1000, friction=0.5),
)

########################## build ##########################
scene.build()

########################## run ##########################
scene.reset()
for i in range(1000):
    dofs_ctrl = np.array([
        1. * np.sin(2 * np.pi * i * 0.001),
    ] * robot.n_dofs)

    robot.control_dofs_velocity(dofs_ctrl)

    scene.step()
```

您会看到：

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/hybrid_robot.mp4" type="video/mp4">
</video>

* 您可以使用材质 `gs.materials.Hybrid` 指定混合机器人，它由 `gs.materials.Rigid` 和 `gs.materials.MPM.Muscle` 组成。注意这里只支持 MPM，而且必须是 Muscle 类，因为混合材质在内部复用了为 `Muscle` 实现的 `muscle_group`。
* 控制机器人时，由于驱动来自内部刚体骨骼，因此有类似于刚体机器人的接口，例如 `control_dofs_velocity`、`control_dofs_force`、`control_dofs_position`。此外，控制维度与内部骨骼的 DoF 相同（在上面的示例中为 2）。
* 皮肤由内部骨骼的形状决定，其中 `thickness` 决定包裹骨骼时的皮肤厚度。
* 默认情况下，我们根据骨骼的形状生长皮肤，由 `morph` 指定（在此示例中为 `urdf/simple/two_link_arm.urdf`）。`gs.materials.Hybrid` 的参数 `func_instantiate_soft_from_rigid` 具体定义了皮肤应如何基于刚体 `morph` 生长。在 [genesis/engine/entities/hybrid_entity.py](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/genesis/engine/entities/hybrid_entity.py) 中有一个默认实现 `default_func_instantiate_soft_from_rigid`。您也可以实现自己的函数。
* 当 `morph` 是 `Mesh` 而不是 `URDF` 时，网格指定软体外层，内部骨骼基于皮肤形状生长。这由 `func_instantiate_rigid_from_soft` 定义。也有一个默认实现 `default_func_instantiate_rigid_from_soft`，它基本上实现了 3D 网格的骨架化。
* `gs.materials.Hybrid` 的参数 `func_instantiate_rigid_soft_association` 决定每个骨骼部分如何与皮肤关联。默认实现是找到软皮肤中距离刚体骨骼部分最近的粒子。


## 下一章节

- [混合实体](./hybrid_entity) — 从 URDF 或网格创建刚-软混合实体
- [超越刚体](./beyond_rigid_bodies) — 流体、布料和可变形体仿真