# 🎥 使用 Recorders 保存和可视化数据

Genesis 还提供了数据记录工具，用于自动处理数据而不会降低仿真速度。这可用于将格式化数据流式传输到文件，或实时可视化数据。

```python
# 1. 在构建场景之前开始记录
sensor.start_recording(
    rec_options=gs.recorders.NPZFile(
        filename="sensor_data.npz"
    ),
)
```
... 就这样！当场景不再处于活动状态时，录制将自动停止并清理，也可以使用 `scene.stop_recording()` 停止。

您可以使用 `sensor.start_recording(recorder_options)` 记录传感器数据，或使用带有自定义数据函数的 `scene.start_recording(data_func, recorder_options)` 记录任何其他类型的数据。例如：

```
def imu_data_func():
    data = imu.read()
    true_data = imu.read_ground_truth()
    return {
        "lin_acc": data.lin_acc,
        "true_lin_acc": true_data.lin_acc,
        "ang_vel": data.ang_vel,
        "true_ang_vel": true_data.ang_vel,
    }

scene.start_recording(
    imu_data_func,
    gs.recorders.MPLLinePlot(
        title="IMU Data",
        labels={
            "lin_acc": ("x", "y", "z"),
            "true_lin_acc": ("x", "y", "z"),
            "ang_vel": ("x", "y", "z"),
            "true_ang_vel": ("x", "y", "z"),
        },
    ),
)
```

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/imu.mp4" type="video/mp4">
</video>

有关当前可用的 recorders，请参阅 API 参考中的 RecorderOptions。更多 recorders 的使用示例可以在 `examples/sensors/` 中查看。
