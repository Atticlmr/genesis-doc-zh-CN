# 📏 接近传感器

`Proximity` 传感器会报告一个或多个局部探针位置到一组选定刚体连杆的最近距离。每个探针会返回 `max_range` 内任意被跟踪网格表面上的最近点。

```python
sensor = scene.add_sensor(
    gs.sensors.Proximity(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("palm").idx_local,
        probe_local_pos=((0.0, 0.0, 0.0),),
        track_link_idx=(duck.base_link_idx, box.base_link_idx),  # 全局刚体连杆 idx
        max_range=0.5,
        draw_debug=True,
    )
)

scene.build()

distances = sensor.read()        # shape ([n_envs,] n_probes)
points = sensor.nearest_points   # shape ([n_envs,] n_probes, 3)
```

如果在 `max_range` 内没有找到被跟踪网格，返回距离会被截断为 `max_range`，返回点则为探针自身位置。

交互示例 `examples/sensors/proximity_shadowhand.py` 会把接近探针安装到灵巧手的手掌和指尖上。

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/proximity.mp4" type="video/mp4">
</video>
