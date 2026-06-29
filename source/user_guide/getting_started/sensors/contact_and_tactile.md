# 🫳 接触与触觉

接触和触觉传感器都测量刚体连杆与场景中其他实体之间的交互，只是输出信息逐步丰富：从单个布尔值，到完整的弹性体位移场。

## Contact 和 ContactForce

`Contact` 与 `ContactForce` 传感器从刚体求解器中检索每个刚体连杆的接触信息。`Contact` 返回布尔值，`ContactForce` 返回关联刚体连杆局部坐标系中的合力向量。

完整示例脚本位于 `examples/sensors/contact_force_go2.py`，添加 `--force` 参数可使用力传感器。

```{figure} ../../../_static/images/contact_force_sensor.png
```

## KinematicContactProbe

`KinematicContactProbe` 是一种触觉传感器，会在连接到刚体连杆的用户自定义探针位置采样接触深度。它不会直接返回求解器接触力，而是基于穿透深度估算每个探针的力：这是一个三维向量，大小为 `stiffness * penetration`，方向由探针法线决定：

```text
force = stiffness * penetration * normal
```

```python
probe = scene.add_sensor(
    gs.sensors.KinematicContactProbe(
        entity_idx=platform.idx,
        link_idx_local=0,
        probe_local_pos=probe_positions,
        probe_local_normal=probe_normals,
        probe_radius=probe_radii,
        stiffness=5000.0,
        draw_debug=True,
    )
)

scene.build()

data = probe.read()
print(data.penetration)  # shape ([n_envs,] n_probes)
print(data.force)        # shape ([n_envs,] n_probes, 3)
```

完整交互示例位于 `examples/sensors/kinematic_contact_probe.py`。

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/kin_probe_data.mp4" type="video/mp4">
</video>

由于探针在连杆局部坐标系中定义，可以用规则网格来模拟触觉表面上的触觉像素。

## ElastomerDisplacement

`ElastomerDisplacement` 可以在不实际仿真形变的情况下建模柔性触觉皮肤。每个探针都会报告由局部压入、剪切和扭转引起的三维位移向量。

可以通过以下系数调节传感器响应。空间影响按 `exp(-coeff * dist^2)` 计算，系数越大影响越局部，系数越小传播越远：

- `dilate_coefficient` - 法向压入的扩散范围。
- `shear_coefficient` - 切向滑移的扩散范围。
- `twist_coefficient` - 扭转位移的扩散范围。

```python
tactile = scene.add_sensor(
    gs.sensors.ElastomerDisplacement(
        entity_idx=pusher.idx,
        link_idx_local=0,
        probe_local_pos=gu.generate_grid_points_on_plane(
            lo=[-0.05, -0.05, -0.025],
            hi=[0.05, 0.05, -0.025],
            normal=(0.0, 0.0, -1.0),
            nx=6,
            ny=8,
        ),
        probe_local_normal=(0.0, 0.0, -1.0),
        probe_radius=0.01,
        dilate_coefficient=1e1,
        shear_coefficient=1e-2,
        twist_coefficient=1e-2,
        draw_debug=True,
    )
)

scene.build()

displacement = tactile.read()
print(displacement)  # shape ([n_envs,] n_probes, 3)
```

当 `probe_local_pos` 以二维网格形式提供时，Genesis 会使用基于 FFT 的算法来加速较大触觉阵列的计算。

示例脚本 `examples/sensors/tactile_elastomer_sandbox.py` 展示了球形或盒形推动器与其他物体的交互。

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/elastomer_sandbox.mp4" type="video/mp4">
</video>

另一个示例脚本 `examples/sensors/tactile_elastomer_franka.py` 会在机械臂夹爪手指上布置网格触觉像素。

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/elastomer_franka.mp4" type="video/mp4">
</video>
