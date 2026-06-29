# 🧑‍💻 交互式 GUI 与调试

:::{note}
使用下面的 GUI 功能前，请先安装可选的 `imgui-bundle` 依赖。ImGui 覆盖面板随 Genesis 的 `render` extras 提供：

```bash
pip install "genesis-world[render]"
```

如果忘记安装却设置了 `enable_gui=True`，或手动调用 `ImGuiOverlayPlugin()`，Genesis 会给出可操作的错误信息并提示上述安装命令。`imgui-bundle` 并不为所有 Python/操作系统组合发布预编译 wheel，例如 Python 3.10 + Linux aarch64；这些平台可通过 `pip install imgui-bundle` 手动安装，它会从源码构建并需要 CMake。
:::

## ImGui 覆盖面板插件

**`ImGuiOverlayPlugin`** 会在原生 pyrender viewer 上添加 Dear ImGui 覆盖层。它提供以下交互式面板：

- 仿真控制：播放、暂停、单步、重置。
- 实体浏览器：每个 DOF 的关节滑块、自由关节四元数组，以及可视化模式切换（visual / collision / wireframe）。
- 相机位置和 lookat 滑块、阴影/坐标系/视锥体显示开关，以及光栅化渲染标志覆盖（法线覆盖、线框覆盖）。
- 场景重建按钮：使用当前实体清单重新运行 `scene.build()`，便于在不重启脚本的情况下迭代 URDF/MJCF。

```python
from genesis.ext.pyrender.overlay import ImGuiOverlayPlugin

plugin = ImGuiOverlayPlugin()
scene.viewer.add_plugin(plugin)
```

你可以用 `plugin.register_panel(callback)` 注册自己的面板。回调会收到实时 ImGui 模块，并可调用其中任意 widget：

```python
def custom_panel(imgui):
    imgui.text("Custom Demo Panel")
    if imgui.button("Trigger something"):
        ...

plugin.register_panel(custom_panel)
```

完整示例脚本位于 `examples/gui/imgui_joint_control.py`。它加载 Franka 机械臂和一个盒子，演示实体浏览器、仿真控制，以及通过 `register_panel` 注册的自定义面板。

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/viewer_plugin_imgui_overlay.mp4" type="video/mp4">
</video>

## 在任意示例中启用 GUI 面板

如果只是想在现有示例上显示面板，而不写插件样板代码，可以在 `ViewerOptions` 上设置 `enable_gui=True`。viewer 会自动为你挂载 `ImGuiOverlayPlugin`：

```python
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(0, -3.5, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
        max_FPS=60,
        enable_gui=True,
    ),
    show_viewer=True,
)
```

## 交互式信息访问

我们设计了一个信息丰富（希望也很美观）的界面，用于访问内部信息和 Genesis 中创建的所有对象的可用属性，通过所有 Genesis 类的 `__repr__()` 方法实现。如果您习惯使用 `IPython`、`pdb` 或 `ipdb` 进行调试，这个功能将非常有用。

在本例中使用 `IPython`。如果没有安装，请通过 `pip install ipython` 安装。这里让我们通过一个简单的例子来说明：
```python
import genesis as gs

gs.init()

scene = gs.Scene(show_viewer=False)

plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

cam_0 = scene.add_camera()
scene.build()

# 进入 IPython 交互模式
import IPython; IPython.embed()
```

您可以直接运行此脚本（如果已安装 `IPython`），或者在终端中进入 `IPython` 交互窗口并粘贴这里的代码（不包括最后一行）。

在这个小块代码中，我们添加了一个平面实体和一个 Franka 机械臂。现在，如果您是新手，可能会想知道场景实际包含什么。如果您在 `IPython` 中（或 `ipdb` 或 `pdb` 甚至原生 python shell）简单地输入 `scene`，您将看到场景中的所有内容，格式化并着色得很好：

```{figure} ../../_static/images/interactive_scene.png
```

在顶行，您将看到对象的类型（此处为 `<gs.Scene>`）。然后您将看到其中所有可用的属性。例如，它告诉您场景已构建（`is_built` 为 `True`），其时间步长（`dt`）为值 `0.01` 秒的浮点数，其唯一 id（`uid`）为 `'69be70e-dc9574f508c7a4c4de957ceb5'`。场景还有一个名为 `solvers` 的属性，本质上是它所拥有的不同物理求解器的列表。您可以在 shell 中进一步输入 `scene.solvers` 并检查此列表，它使用 `gs.List` 类实现以获得更好的可视化效果：

```{figure} ../../_static/images/interactive_solvers.png
```

您还可以检查 Franka 实体：

```{figure} ../../_static/images/interactive_franka.png
```
在这里您将看到所有的 `geoms`、`links` 以及相关信息。我们可以再深入一层，输入 `franka.links[0]`：


```{figure} ../../_static/images/interactive_link.png
```
在这里，您将看到 link 中包含的所有碰撞几何体（`geoms`）和视觉几何体（`vgeoms`），以及其他重要信息，例如其 `inertial_mass`、link 在场景中的全局索引（`idx`）、所属实体（`entity`，即 franka 机械臂实体）、其关节（`joint`）等。

我们希望这个信息丰富的界面能让您的调试过程更轻松！
