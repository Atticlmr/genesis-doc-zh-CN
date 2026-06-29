# 🔬 传感器

本节介绍生成传感器测量值的内部管线，以及扩展 Genesis 添加自定义传感器类型时需要遵守的契约。如果你正在实现新传感器，或想理解 `sensor.read()` 背后的抽象，可以阅读这些页面。

- [**传感器管线**](sensor_pipeline) - 运行时数据流：嵌入式采样器抽象、中间空间与返回空间、逐步编排、立即执行的 `_post_process` 和存储作用域。
- [**实现自定义传感器**](custom_sensors) - 作者指南：需要重写哪些 hook、形状和 dtype 契约、自动插件注册，以及包括 `BaseCameraSensor` 在内的示例。

```{toctree}
:hidden:
:maxdepth: 1

sensor_pipeline
custom_sensors
```
