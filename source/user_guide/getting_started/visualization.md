# 📸 可视化与渲染

Genesis 的可视化系统由您刚刚创建的场景的 `visualizer` 管理（即 `scene.visualizer`）。有两种可视化场景的方式：1）使用在单独线程中运行的交互式查看器，2）通过手动向场景添加相机并使用相机渲染图像。


## 查看器
如果您连接到显示器，可以使用交互式查看器来可视化场景。Genesis 使用不同的 `options` 组来配置场景中的不同组件。要配置查看器，您可以在创建场景时更改 `viewer_options` 中的参数。此外，我们使用 `vis_options` 来指定与可视化相关的属性，这些属性将由查看器和相机（我们很快会添加）共享。

使用更详细的查看器和可视化设置创建场景（这看起来有点复杂，但仅用于说明目的）：
```python
scene = gs.Scene(
    show_viewer    = True,
    viewer_options = gs.options.ViewerOptions(
        res           = (1280, 960),
        camera_pos    = (3.5, 0.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 60,
    ),
    vis_options = gs.options.VisOptions(
        show_world_frame = True, # 在其原点可视化 `world` 的坐标系
        world_frame_size = 1.0, # 世界坐标轴的长度，单位为米
        show_link_frame  = False, # 不可视化实体连杆的坐标系
        show_cameras     = False, # 不可视化添加的相机的网格和视锥体
        plane_reflection = True, # 开启平面反射
        ambient_light    = (0.1, 0.1, 0.1), # 环境光设置
    ),
    renderer = gs.renderers.Rasterizer(), # 使用光栅化器进行相机渲染
)
```
在这里，我们可以指定查看器相机的姿态和视场角（fov）。如果 `max_FPS` 设置为 `None`，查看器将尽可能快地运行。如果 `res` 设置为 None，Genesis 将自动创建一个 4:3 窗口，高度设置为显示器高度的一半。还要注意，在上述设置中，我们设置为使用光栅化后端进行相机渲染。Genesis 提供两种渲染后端：`gs.renderers.Rasterizer()` 和 `gs.renderers.RayTracer()`。查看器始终使用光栅化器。默认情况下，相机也使用光栅化器。


场景创建后，您可以通过 `scene.visualizer.viewer` 或简单地使用 `scene.viewer` 作为快捷方式来访问查看器对象。您可以查询或设置查看器相机姿态：
```python
cam_pose = scene.viewer.camera_pose

scene.viewer.set_camera_pose(cam_pose)
```

## 相机与无界面渲染
现在让我们手动向场景添加一个相机对象。相机不连接到查看器或显示器，仅在您需要时返回渲染的图像。因此，相机可以在无界面模式下工作。

```python
cam = scene.add_camera(
    res    = (1280, 960),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False
)
```
如果 `GUI=True`，每个相机将创建一个 opencv 窗口来动态显示渲染的图像。注意这与查看器 GUI 不同。

然后，一旦我们构建场景，就可以使用相机渲染图像。我们的相机支持渲染 RGB 图像、深度、分割掩码和表面法线。默认情况下，仅渲染 RGB，您可以在调用 `camera.render()` 时通过设置参数来开启其他模式：

```python
scene.build()

# 渲染 RGB、深度、分割掩码和法线图
rgb, depth, segmentation, normal = cam.render(depth=True, segmentation=True, normal=True)
```

如果您使用了 `GUI=True` 并且连接了显示器，您应该能看到 4 个窗口。（有时 opencv 窗口会有额外的延迟，所以如果窗口是黑色的，您可以调用额外的 `cv2.waitKey(1)`，或者简单地再次调用 `render()` 来刷新窗口。）
```{figure} ../../_static/images/multimodal.png
```

**使用相机录制视频**

现在，让我们只渲染 RGB 图像，移动相机并录制视频。Genesis 提供了一个方便的实用工具来录制视频：
```python
# 开始相机录制。一旦开始，所有渲染的 RGB 图像将在内部记录
cam.start_recording()

import numpy as np
for i in range(120):
    scene.step()

    # 更改相机位置
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    
    cam.render()

# 停止录制并保存视频。如果未指定 `filename`，将使用调用者文件名自动生成名称。
cam.stop_recording(save_to_filename='video.mp4', fps=60)
```
视频将被保存到 `video.mp4`：

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/cam_record.mp4" type="video/mp4">
</video>


以下是涵盖上述所有内容的完整代码脚本：
```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene(
    show_viewer = True,
    viewer_options = gs.options.ViewerOptions(
        res           = (1280, 960),
        camera_pos    = (3.5, 0.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 60,
    ),
    vis_options = gs.options.VisOptions(
        show_world_frame = True,
        world_frame_size = 1.0,
        show_link_frame  = False,
        show_cameras     = False,
        plane_reflection = True,
        ambient_light    = (0.1, 0.1, 0.1),
    ),
    renderer=gs.renderers.Rasterizer(),
)

plane = scene.add_entity(
    gs.morphs.Plane(),
)
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

cam = scene.add_camera(
    res    = (640, 480),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False,
)

scene.build()

# 渲染 RGB、深度、分割和法线
# rgb, depth, segmentation, normal = cam.render(rgb=True, depth=True, segmentation=True, normal=True)

cam.start_recording()
import numpy as np

for i in range(120):
    scene.step()
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    cam.render()
cam.stop_recording(save_to_filename='video.mp4', fps=60)
```
## 使用 Nyx 进行照片级真实渲染

[Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx) 是专为 Genesis 构建的 GPU 加速路径追踪器。与下面的 LuisaRender 后端不同，Nyx 以**相机传感器**的形式接入，而不是作为全局 scene renderer：你向场景添加 `NyxCameraOptions` 传感器，然后从 `cam.read().rgb` 读取图像。它支持 PBR 材质、HDRI 光照、3D Gaussian splat 资产、连接/多相机设置、多环境渲染以及逐像素对象拾取。

### 安装

Nyx 以 `gs-nyx` 包发布：

```bash
pip install gs-nyx
```

```{note}
`gs-nyx` 当前在项目准备公开发布期间通过内部包索引分发。wheel 发布到 PyPI 后，公开安装说明会在 [Nyx 仓库](https://github.com/Genesis-Embodied-AI/genesis-nyx) 中提供。
```

安装后，可通过同时导入 Genesis 和 Nyx 插件来验证：

```python
import genesis as gs
import gs_nyx.nyx_py_renderer as npr
import gs_nyx.nyx_py_sdk as nps
from gs_nyx_plugin.nyx_camera_options import NyxCameraOptions
```

### 最小示例

下面的片段会在 HDRI 环境贴图照明下渲染平面上的 PBR 球体，是 Nyx 的典型 “hello world”。它对应 Nyx 仓库中的 [`examples/01_hello_nyx.py`](https://github.com/Genesis-Embodied-AI/genesis-nyx/blob/main/examples/01_hello_nyx.py)。

```{image} ../../_static/images/nyx_hello.png
:alt: PBR ball rendered with Nyx under an HDRI environment map
:align: center
:width: 80%
```

```python
import os
from PIL import Image

import genesis as gs
import gs_nyx.nyx_py_renderer as npr
import gs_nyx.nyx_py_sdk as nps
from gs_nyx_plugin.nyx_camera_options import NyxCameraOptions


HERE        = os.path.dirname(__file__)
PBR_BALL    = os.path.join(HERE, "assets", "PBR_Ball.glb")
ENV_MAP     = os.path.join(HERE, "assets", "kloppenheim_07_puresky_4k.hdr")
OUTPUT_PATH = os.path.join(HERE, "out", "01_hello_nyx.png")


def main():
    gs.init()

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01),
        show_viewer=False,
    )

    scene.add_entity(morph=gs.morphs.Plane(plane_size=(10.0, 10.0)))
    scene.add_entity(
        morph=gs.morphs.Mesh(file=PBR_BALL, pos=(0.0, 0.0, 0.0)),
        surface=gs.surfaces.Gold(),
    )

    env_map            = nps.EnvironmentMapAsset()
    env_map.texture    = ENV_MAP
    env_map.layout     = nps.EEnvMapLayout.LongLat
    env_map.multiplier = 8

    cam = scene.add_sensor(NyxCameraOptions(
        res         = (1920, 1080),
        pos         = (-1.0, 1.0, 1.2),
        lookat      = (0.0, 0.0, 0.1),
        fov         = 20.0,
        spp         = 64,
        render_mode = npr.ERenderMode.FastPathTracer,
        env_maps    = (env_map,),
    ))

    scene.build(n_envs=1)
    scene.step()  # 渲染在仿真 step 中发生

    rgb = cam.read().rgb[0].cpu().numpy()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    Image.fromarray(rgb).save(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
```

需要注意：

- **Nyx 是传感器。** 它通过 `scene.add_sensor(NyxCameraOptions(...))` 注册，而不是全局 renderer 后端。
- **渲染发生在 `scene.step()` 中。** 通过 `cam.read().rgb` 读取帧；这是一个 torch 张量，每个环境一张图。
- **`spp`**（每像素采样数）和 **`render_mode`** 会在质量与速度之间取舍；`FastPathTracer` 是迭代时的良好默认值。

更多高级功能（Gaussian splats、多相机、对象拾取等）见专门的 [Nyx 渲染器](nyx_renderer.md) 页面和 [Nyx 文档站点](https://genesis-embodied-ai.github.io/genesis-nyx/)。

```{note}
**路线图。** Genesis 正在把光栅化和路径追踪统一到 Nyx 这个基于传感器的渲染接口下。Nyx 会逐步替代下面记录的 LuisaRender 后端以及默认的 Pyrender 光栅化器；未来 Genesis 中所有基于相机的渲染都会通过 Nyx。
```

## 使用 Luisa 的照片级真实渲染（逐步弃用）

Genesis 提供光线追踪渲染后端以实现照片级真实感渲染。您可以在创建场景时通过设置 `renderer=gs.renderers.RayTracer()` 轻松切换到使用此后端。此相机允许更多参数调整，如 `spp`、`aperture`、`model` 等。

### 设置

测试环境
- Ubuntu 22.04, CUDA 12.4, python 3.9

获取子模块，特别是 `genesis/ext/LuisaRender`。
```bash
# 在 Genesis/ 目录内
git submodule update --init --recursive
pip install -e ".[render]"
```
安装/升级 g++ 和 gcc 到版本 >= 11。
```bash
sudo apt install build-essential manpages-dev software-properties-common
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt update && sudo apt install gcc-11 g++-11
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 110
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110

# 验证版本
g++ --version
gcc --version
```
如果您的本地版本不符合要求版本，请安装 CMake。我们使用 `snap` 而不是 `apt`，因为我们需要 CMake 版本 >= 3.26。但是，请记住使用正确的 cmake。您可能有 `/usr/local/bin/cmake`，但 `snap` 安装的包位于 `/snap/bin/cmake`（或 `/usr/bin/snap`）。请通过 `echo $PATH` 仔细检查二进制路径的顺序。
```bash
sudo snap install cmake --classic
cmake --version
```
安装依赖项，
```bash
sudo apt install libvulkan-dev xorg-dev # Vulkan, X11 & RandR
sudo apt-get install uuid-dev # UUID 
sudo apt-get install zlib1g-dev # zlib
```

如果您没有 sudo，以下命令也可以在您的 conda 环境中安装所需的依赖项：
```bash
conda install -c conda-forge gcc=11.4 gxx=11.4 
conda install -c conda-forge cmake=3.26.1
conda install -c conda-forge vulkan-tools vulkan-headers xorg-xproto # Vulkan, X11 & RandR
conda install -c conda-forge libuuid # UUID
conda install -c conda-forge zlib # zlib
```

构建 `LuisaRender`。请记住使用正确的 cmake。默认情况下，我们使用 OptiX 降噪器（仅适用于 CUDA 后端）。如果您需要 OIDN 降噪器，请附加 `-D LUISA_COMPUTE_DOWNLOAD_OIDN=ON`。
```bash
cd genesis/ext/LuisaRender
cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF -D LUISA_RENDER_BUILD_TESTS=OFF # 记得检查 python 版本
cmake --build build -j $(nproc)
```

如果您真的难以完成构建，我们在[这里](https://drive.google.com/drive/folders/1Ah580EIylJJ0v2vGOeSBU_b8zPDWESxS?usp=sharing)有一些构建版本，您可以检查您的机器是否恰好有相同的设置。命名遵循 `build_<commit-tag>_cuda<version>_python<version>`。下载与您系统匹配的版本，重命名为 `build/` 并放在 `genesis/ext/LuisaRender` 中。

最后，您可以运行示例，
```bash
cd examples/rendering
python demo.py
```
您应该能够得到
```{figure} ../../_static/images/raytracing_demo.png
```

## 使用 gs-madrona 批量渲染

Genesis 通过 gs-madrona 提供高吞吐量批量渲染后端。您可以通过设置 `renderer=gs.renderers.BatchRenderer(use_rasterizer=True/False)` 轻松切换到 gs-madrona 后端

### 前提条件
请首先按照[官方 README 说明](https://github.com/Genesis-Embodied-AI/Genesis#quick-installation)安装最新版本的 Genesis。

### 简易安装（仅 x86）
Python>=3.10 的预编译二进制 wheel 可在 PyPI 上获取。可以使用任何 Python 包管理器（例如 `uv` 或 `pip`）安装：
```sh
pip install gs-madrona
```

### 从源码构建
```sh
pip install .
```

### 测试（可选）
1. 如果尚未克隆 Genesis Simulator 仓库
```sh
git clone https://github.com/Genesis-Embodied-AI/Genesis.git
```

2. 运行 Genesis 提供的以下示例脚本
```sh
python Genesis/examples/rigid/single_franka_batch_render.py
```

所有生成的图像将存储在当前目录下的 `./image_output` 中。

2. 要使用光线追踪器，在 `single_franka_batch_render.py` 中更改 `use_rasterizer=False`
```
renderer = gs.options.renderers.BatchRenderer(
    use_rasterizer=False,
)
```

### 常见问题
- 运行 `cmake -S . -B build` 时仍检测不到已安装的库，
    您可以通过显式设置 `XXX_INCLUDE_DIR` 等选项手动指示 CMake 检测依赖项，例如 `ZLIB_INCLUDE_DIR=/path/to/include`。对于 conda 环境，`XXX_INCLUDE_DIR` 通常遵循 `/home/user/anaconda3/envs/genesis/include` 格式。
- 执行 `cmake -S . -B build` 时出现 Pybind 错误，
    ```bash
    CMake Error at src/apps/CMakeLists.txt:12 (find_package):
    By not providing "Findpybind11.cmake" in CMAKE_MODULE_PATH this project has
    asked CMake to find a package configuration file provided by "pybind11",
    but CMake did not find one.

    Could not find a package configuration file provided by "pybind11" with any
    of the following names:

        pybind11Config.cmake
        pybind11-config.cmake
    ```
    您可能忘记执行 `pip install -e ".[render]"`。或者，您可以简单地执行 `pip install "pybind11[global]"`。
- 运行 `cmake -S . -B build` 时出现 CUDA 运行时编译错误，
    ```bash
    /usr/bin/ld: CMakeFiles/luisa-cuda-nvrtc-standalone-compiler.dir/cuda_nvrtc_compiler.cpp.o: in function `main':
    cuda_nvrtc_compiler.cpp:(.text.startup+0x173): undefined reference to `nvrtcGetOptiXIRSize'
    /usr/bin/ld: cuda_nvrtc_compiler.cpp:(.text.startup+0x197): undefined reference to `nvrtcGetOptiXIR'
    ```
    您需要安装"系统级"的 cuda-toolkit（[官方安装指南](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)）。首先检查 cuda-toolkit，
    ```bash
    nvcc --version # 这应该与您的 nvidia-smi 中的 cuda 版本一致
    which nvcc # 只是检查您正在使用预期的 cuda-toolkit
    ```
    如果您无法从 `nvcc` 获得正确的输出，请按照官方 cuda-toolkit 安装指南进行操作。作为示例，以下是安装 cuda-12.4 的 cuda-toolkit 的方法。按照[此处](https://developer.nvidia.com/cuda-12-4-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_local)的说明下载安装程序。
    ```bash
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
    sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
    sudo dpkg -i cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
    sudo cp /var/cuda-repo-ubuntu2204-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
    sudo apt-get update
    sudo apt-get -y install cuda-toolkit-12-4
    ```
    记得设置二进制和运行时库路径。在 `~/.bashrc` 中，添加以下内容（注意我们将 CUDA 路径附加到末尾，因为 `/usr/local/cuda-12.4/bin` 中还有另一个 `gcc` 和 `g++`，可能不是版本 11，而这是构建所需的），
    ```bash
    PATH=${PATH:+${PATH}:}/usr/local/cuda-12.4/bin
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}/usr/local/cuda-12.4/lib64
    ```
    记得重新启动终端或执行 `source ~/.bashrc`。另一种错误类型是，
    ```bash
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_fatal_printf@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_audit_symbind_alt@GLIBC_PRIVATE'
    <your-env-path>/genesis-test1/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_exception_create@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `__nptl_change_stack_perm@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `__tunable_get_val@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_audit_preinit@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_find_dso_for_object@GLIBC_PRIVATE'
    ```
    这可能是由于您的 conda 环境中的 cuda-toolkit 导致的。请执行以下操作并安装系统级 CUDA，
    ```bash
    which nvcc
    conda uninstall cuda-toolkit
    ```
    或者，您可以将您的 conda 库路径添加到运行时库路径，
    ```bash
    ls $CONDA_PREFIX/lib/libcudart.so # 您应该有这个

    # 在您的 ~/.bashrc 中，添加
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}/usr/local/cuda-12.4/lib64
    ```
    最后，记得在完成上述修复后清除构建，
    ```bash
    rm -r build
    ```
- 在 `cmake -S . -B build` 时出现 C/CXX 编译器错误，
    ```bash
    CMake Error at /snap/cmake/1435/share/cmake-3.31/Modules/CMakeDetermineCCompiler.cmake:49 (message):
    Could not find compiler set in environment variable CC:

    /home/tsunw/miniconda3/envs/genesis-test1/bin/x86_64-conda-linux-gnu-cc.
    Call Stack (most recent call first):
    CMakeLists.txt:21 (project)


    CMake Error: CMAKE_C_COMPILER not set, after EnableLanguage
    CMake Error: CMAKE_CXX_COMPILER not set, after EnableLanguage
    ```
    您可能没有使用版本 11 的 `gcc` 和 `g++`。请仔细检查（i）版本（ii）二进制文件是否指向预期的路径（iii）二进制路径的顺序，
    ```bash
    gcc --version
    g++ --version
    which gcc
    which g++
    echo $PATH # 例如，/usr/local/cuda-12.4/bin/gcc（版本 = 10.5）不应该在 /usr/bin/gcc（如果通过 apt 正确安装，版本 = 11）之前
    ```
- 运行 `examples/rendering/demo.py` 时出现导入错误，
    ```bash
    [Genesis] [11:29:47] [ERROR] Failed to import LuisaRenderer. ImportError: /home/tsunw/miniconda3/envs/genesis-test1/bin/../lib/libstdc++.so.6: version `GLIBCXX_3.4.30' not found (required by /home/tsunw/workspace/Genesis/genesis/ext/LuisaRender/build/bin/liblc-core.so)
    ```
    Conda 的 `libstdc++.so.6` 不支持 3.4.30。您需要将系统的移到 conda 中（[参考](https://stackoverflow.com/a/73708979)）。
    ```bash
    cd $CONDA_PREFIX/lib
    mv libstdc++.so.6 libstdc++.so.6.old
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
    ```
- 断言 'lerror' 失败：无法写入进程：管道损坏：您可能需要使用与编译时相同版本的 CUDA。
