# 🌡️ 温度网格

`TemperatureGrid` 传感器会把刚体连杆的包围盒离散成三维体素网格，并返回每个单元格的摄氏温度。热传递由接触、传导、辐射、对流以及可选的逐单元发热驱动。

需要提供 `properties_dict` 来描述可能参与热交换的连杆材料属性。键 `-1` 可作为未显式列出连杆的默认属性。

```python
temperature_sensor = scene.add_sensor(
    gs.sensors.TemperatureGrid(
        entity_idx=entity.idx,
        link_idx_local=0,
        grid_size=(10, 10, 1),
        properties_dict={
            -1: gs.sensors.TemperatureProperties(
                base_temperature=22.0,
                conductivity=100.0,
                density=1000.0,
                specific_heat=1.0,
                emissivity=0.8,
            ),
            entity.base_link_idx: gs.sensors.TemperatureProperties(
                base_temperature=200.0,
                conductivity=1000.0,
                density=2000.0,
                specific_heat=1.0,
                emissivity=0.8,
            ),
        },
        ambient_temperature=22.0,
        convection_coefficient=0.0,
        draw_debug=True,
    )
)

scene.build()

grid = temperature_sensor.read()
print(grid)  # shape ([n_envs,] nx, ny, nz)
```

如果希望 Genesis 为所有带热属性的连杆演化温度，而不只是传感器连接的连杆，请设置 `simulate_all_link_temperatures=True`。

示例 `examples/sensors/temperature_grid.py` 会展示热推动器加热平台，同时物体落到带传感器表面上的过程。

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/temperaturegrid.mp4" type="video/mp4">
</video>
