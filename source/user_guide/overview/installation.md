# 🛠️ 安装

## 前置条件

* **Python**: >=3.10,<3.14
* **操作系统**: Linux (*推荐*) / MacOS / Windows

:::{note}
Genesis 设计为***跨平台***，支持的后端设备包括*CPU*、*CUDA GPU*和*非 CUDA GPU*。也就是说，建议使用**Linux**平台和**CUDA 兼容 GPU**以获得最佳性能。
:::

各系统支持的功能如下：

<div style="text-align: center;">

| 操作系统 | GPU 设备        | GPU 仿真 | CPU 仿真 | 交互式查看器 | 无界面渲染 |
| ------- | ----------------- | -------------- | -------------- | ---------------- | ------------------ |
| Linux   | Nvidia            | ✅             | ✅             | ✅               | ✅                 |
|         | AMD               | ✅             | ✅             | ✅               | ✅                 |
|         | Intel             | ✅             | ✅             | ✅               | ✅                 |
| Windows | Nvidia            | ✅             | ✅             | ✅               | ✅                 |
|         | AMD               | ✅             | ✅             | ✅               | ✅                 |
|         | Intel             | ✅             | ✅             | ✅               | ✅                 |
| MacOS   | Apple Silicon     | ✅             | ✅             | ✅               | ✅                 |

</div>

## 安装步骤

1. 按照[官方指南](https://pytorch.org/get-started/locally/)安装 **PyTorch**。

2. 通过 PyPI 安装 Genesis：
    ```bash
    pip install genesis-world
    ```

:::{note}
如果您在 CUDA 环境下使用 Genesis，请确保您的机器上安装了适当的 nvidia 驱动程序。
:::

## （可选）表面重建

如果您需要为基于粒子的实体（流体、可变形体等）可视化提供精美的视觉效果，通常需要使用基于粒子的内部表示来重建网格表面。为此，我们开箱即用地支持 [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf)，这是一种最先进的表面重建工具。或者，我们也提供了 `ParticleMesher`，这是我们自己的基于 openVDB 的表面重建工具，速度更快但质量较低：

```bash
echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
source ~/.bashrc
```

## （可选）光线追踪渲染器

如果您需要照片级真实感的视觉效果，Genesis 内置了一个基于光线追踪（路径追踪）的渲染器，使用 [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute) 开发，这是一种为渲染设计的高性能领域特定语言。有关设置，请参见[可视化与渲染](../getting_started/visualization.md)。

## （可选）USD 资产

如果您需要将 USD 资产加载到 Genesis 场景中，请参见 [USD 导入设置](../getting_started/usd_import.md#installation)获取安装说明。

## 故障排除

### 导入错误

#### 'Genesis hasn't been initialized'（Genesis 尚未初始化）

Genesis 未初始化时，尝试导入任何引擎相关子模块将引发异常，例如：

```python
Traceback (most recent call last):
  File "/home/jeremy/Downloads/Genesis_Jeremy/examples/./init_error.py", line 3, in <module>
    from genesis.engine.entities import RigidEntity
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/engine/entities/rigid_entity/rigid_entity.py", line 14, in <module>
    from genesis.utils import array_class
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/utils/array_class.py", line 13, in <module>
    gs.raise_exception("Genesis hasn't been initialized. Did you call `gs.init()`?")
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/utils/misc.py", line 42, in raise_exception
    raise gs.GenesisException(msg)
genesis.GenesisException: Genesis hasn't been initialized. Did you call `gs.init()`?
```

这个错误虽然是 bug 但是预期的行为。任何引擎相关的子模块必须在初始化 Genesis 之后导入，以便有机会配置低级的 Quadrants 功能，如快速缓存机制或 Quadrants 动态数组模式。在实践中，这个限制不应该成为任何人的障碍，因为引擎相关的类不意味着手动实例化。不过，为了类型检查而导入它们可能是方便的。如果是这样，只需使用类型检查保护，例如：

```python
from typing import TYPE_CHECKING

import genesis as gs
if TYPE_CHECKING:
    from genesis.engine.entities.drone_entity import DroneEntity
```

#### 循环导入错误

如果当前目录是 Genesis 的源目录，Python 将无法（循环）导入 Genesis。这可能是由于 Genesis 在未启用可编辑模式的情况下安装的，无论是从 PyPI 包索引还是从源代码安装。明显的解决方法是在运行 Python 之前移出 Genesis 的源目录。长期的解决方案是简单地切换到可编辑安装模式：首先卸载 Python 包 `genesis-world`，然后在 Genesis 的源目录中运行 `pip install -e '.[render]'`。

### [原生 Ubuntu] 渲染缓慢（CPU 即软件回退）

有时，在 Genesis 中使用 `cam.render()` 或查看器相关功能时，渲染会变得非常缓慢。这**不是 Genesis 的问题**。Genesis 依赖 PyRender 和 EGL 进行基于 GPU 的离屏渲染。如果您的系统未正确配置以使用 `libnvidia-egl`，它可能会**静默回退到 MESA（CPU）渲染**，严重影响性能。

即使 GPU 看起来可以访问，您的系统仍可能默认使用 CPU 渲染，除非明确配置。

---

#### ✅ 确保 GPU 渲染处于活动状态

1. **安装 NVIDIA GL 库**
   ```bash
   sudo apt update && sudo apt install -y libnvidia-gl-525
   ```

2. **检查 EGL 是否指向 NVIDIA 驱动**
   ```bash
   ldconfig -p | grep EGL
   ```
   您应该看到：
   ```
   libEGL_nvidia.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libEGL_nvidia.so.0
   ```

   ⚠️ 您*可能也会看到*：
   ```
   libEGL_mesa.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libEGL_mesa.so.0
   ```

   这并不总是问题——**某些系统可以同时处理两者**。
   但如果您遇到**渲染缓慢**，通常最好移除 Mesa。

3. **（可选但推荐）** 移除 MESA 以防止回退：
   ```bash
   sudo apt remove -y libegl-mesa0 libegl1-mesa libglx-mesa0
   ```
   然后重新检查：
   ```bash
   ldconfig -p | grep EGL
   ```
   ✅ 您现在应该只能看到 `libEGL_nvidia.so.0`。

4. **（可选 – 针对少数情况）** 检查 NVIDIA EGL ICD 配置文件是否存在

    在大多数情况下，如果正确安装了 NVIDIA 驱动程序，此文件应该已经存在。但是，在某些最小化或容器化环境（例如无头 Docker 镜像）中，如果 EGL 初始化失败，您可能需要手动创建它：
    ```bash
    cat /usr/share/glvnd/egl_vendor.d/10_nvidia.json
    ```
    应包含：
    ```json
    {
        "file_format_version" : "1.0.0",
        "ICD" : {
            "library_path" : "libEGL_nvidia.so.0"
        }
    }
    ```

    如果没有，请创建它：
    ```bash
    bash -c 'cat > /usr/share/glvnd/egl_vendor.d/10_nvidia.json <<EOF
    {
        "file_format_version": "1.0.0",
        "ICD": {
            "library_path": "libEGL_nvidia.so.0"
        }
    }
    EOF'
    ```

    类似地，CUDA 运行时的某些符号链接可能缺失：
    ```bash
    ln -s /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so
    ```

5. **设置全局 NVIDIA 渲染环境变量**

Genesis 默认尝试 EGL 渲染，因此在大多数环境中您无需手动设置 `PYOPENGL_PLATFORM`。但是，设置这些变量可以帮助确保在自定义设置（例如 Docker、无头服务器）中的稳定性：

   添加到 `~/.bashrc` 或 `~/.zshrc`：
   ```bash
   export NVIDIA_DRIVER_CAPABILITIES=all
   export PYOPENGL_PLATFORM=egl
   ```

   重新加载：
   ```bash
   source ~/.bashrc  # 或 source ~/.zshrc
   ```

   确认：
   ```python
   import os
   print("[DEBUG] Using OpenGL platform:", os.environ.get("PYOPENGL_PLATFORM"))
   print("[DEBUG] NVIDIA capabilities:", os.environ.get("NVIDIA_DRIVER_CAPABILITIES"))
   ```

### [Windows 11 通过 WSL2 上的 Docker 容器（Genesis 镜像）] 渲染窗口黑屏

    对于配备 Nvidia GPU 的机器，请确保已安装 NVIDIA Container Toolkit。官方指南可在[此处](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)获取。

    某些用户在 Windows 上基于 Genesis 镜像在 Docker 容器中运行 Genesis 时仍可能遇到渲染问题。通常可以通过将 WSL 库添加到 Linux 的动态库搜索路径来解决此问题，该路径由环境变量 `LD_LIBRARY_PATH` 指定，即：
    ```bash
    docker run --gpus all --rm -it \
    -e DISPLAY=$DISPLAY \
    -e LD_LIBRARY_PATH=/usr/lib/wsl/lib \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v $PWD:/workspace \
    genesis
    ```

### [Windows 11 通过 WSL2 上的 Ubuntu VM] OpenGL 错误

    对于配备 Nvidia GPU 的机器，尝试通过在 Ubuntu VM 中导出以下环境变量来强制 GPU 加速渲染：
    ```bash
    export LIBGL_ALWAYS_INDIRECT=0
    export GALLIUM_DRIVER=d3d12
    export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
    ```

    如果不起作用，请尝试安装最新版本的 OSMesa：
    ```bash
    sudo add-apt-repository ppa:kisak/kisak-mesa
    sudo apt update
    sudo apt upgrade
    ```
    然后，仅强制执行直接渲染：
    ```bash
    export LIBGL_ALWAYS_INDIRECT=0
    ```

    此时，可以使用 `glxinfo` mesa 工具来确定默认使用的 OpenGL 供应商，即：
    ```bash
    glxinfo -B
    ```

    作为最后的手段，如有必要，可以使用 OSMesa 强制 CPU（即软件）渲染，如下所示：
    ```bash
    export LIBGL_ALWAYS_SOFTWARE=1
    ```

### [Windows 11 通过 WSL2 上的 Ubuntu VM] Quadrants 和 Genesis 找不到 cudalib.so 并回退到 CPU

安装 Pytorch 和 Genesis 后，Quadrants 回退到 CPU，而 torch 在 CUDA 上初始化正常。

症状：

- 运行 `python -c "import torch; print(torch.zeros((3,), device='cuda'))"` 输出 `tensor([0., 0., 0.], device='cuda:0')`
- 但运行 `python -c "import quadrants as qd; qd.init(arch=qd.gpu)"` 输出类似
    ```
    [W 06/18/25 12:47:56.784 14507] [cuda_driver.cpp:load_lib@36] libcuda.so lib not found.
    [Quadrants] Starting on arch=vulkan
    ```

修复方法：

- 使用 `ls /usr/lib/wsl/lib/` 检查 libcuda.so 和其他 cuda 库是否在 lib 文件夹中
- 如果是，使用 `export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH` 更新库路径
