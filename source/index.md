# Genesis World

![Genesis World teaser](https://raw.githubusercontent.com/YilingQiao/Genesis/readme-assets/videos/HeroShot_Final.png)

[![GitHub Repo stars](https://img.shields.io/github/stars/Genesis-Embodied-AI/Genesis?style=plastic&logo=GitHub&logoSize=auto)](https://github.com/Genesis-Embodied-AI/Genesis)
[![PyPI version](https://badge.fury.io/py/genesis-world.svg?icon=si%3Apython)](https://pypi.org/project/genesis-world/)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fgenesis-embodied-ai.github.io%2F)](https://genesis-embodied-ai.github.io/)
[![Discord](https://img.shields.io/discord/1322086972302430269?logo=discord)](https://discord.gg/nukCuhB47p)
<a href="https://drive.google.com/uc?export=view&id=1ZS9nnbQ-t1IwkzJlENBYqYIIOOZhXuBZ"><img src="https://img.shields.io/badge/WeChat-07C160?style=for-the-badge&logo=wechat&logoColor=white" height="20" style="display:inline"></a>


## Genesis World 是什么？

**Genesis World** 是面向物理 AI 开发的仿真平台。它把统一的多物理引擎、照片级真实渲染器 [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)，以及跨平台编译器 [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) 放在同一个 Pythonic 仿真接口之后。Genesis World 既能从单台笔记本上的 kernel 扩展到数据中心级 GPU，也保持了适合研究代码阅读、扩展和嵌入的接口。

它以前名为 **Genesis**，最早是 2024 年 12 月启动的学术项目；现在其开发由 [Genesis AI](https://www.genesis.ai/) 正式支持。更多技术背景见我们的 [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward)。

Genesis World 包含四层。上层是你构建的机器人环境、机器学习流水线或智能体仿真；下层是你拥有的计算后端。

- **Simulation Interface**：面向用户的 API，包括资产解析（URDF、MJCF、OBJ、GLB、USD 等）、实体访问器、控制器、传感器、并行/异构环境和内置 GUI。
- **Physics**：统一的多物理引擎，集成 Rigid、FEM、MPM、Particle（PBD / SPH）、[uipc](https://github.com/spiriMirror/libuipc)、显式耦合器和 SAP，并共享同一个场景与状态。
- **Render**：三条渲染路径都作为相机传感器接入：**[Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)**（Genesis 自研、面向机器人任务的渲染器）、**Luisa**（DSL 光线追踪器）和 **Pyrender**（光栅化器）。
- **Compiler**：**[Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)** 会把 Python kernel code 降低到 CUDA、AMD ROCm、Apple Metal、Vulkan、x86 和 ARM64，并承载 Genesis World 的自动微分、GPU graphs 和 fastcache 机制。

## 核心特性

与以往的仿真平台相比，以下是 Genesis World 的几个核心特性：

- 🐍 **Pythonic** 且完全透明。Genesis World 使用 Python 开发并完全开源，使代码理解和贡献更容易。
- 👶 **轻松安装**，API 设计**极其简单**且**用户友好**。
- 🚀 **并行仿真**带来***前所未有的速度***：Genesis World 是**世界上最快的物理引擎**，仿真速度比现有的*GPU 加速*机器人仿真器（Isaac Gym/Sim/Lab、Mujoco MJX 等）快***10~80 倍***，同时***不妥协***仿真精度和保真度。
- 💥 **统一**框架支持各种最先进的物理求解器，建模**广泛的材料**和物理现象。
- 📸 通过 [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx) 提供照片级真实光线追踪渲染，并针对机器人应用优化性能。
- 📐 **可微分性**：Genesis World 设计为与可微分仿真兼容，自动微分和反向传播基础设施由 [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) 提供。
- ☝🏻 内置**完整传感器系统**：除了物理精确且可微的**触觉**传感器，还包括 **IMU**、**lidar**、**深度相机**、**接触力**、**表面距离**和**温度网格**传感器，均可直接用于并行和异构环境。

## 快速开始

### 快速安装

Genesis 可通过 PyPI 获取：

```bash
pip install genesis-world
```

您还需要按照[官方说明](https://pytorch.org/get-started/locally/)安装 **PyTorch**。

### 文档

:::{note}
本文档站点非官方站点，由 [GitHub@Atticlmr](https://github.com/Atticlmr) 翻译润色。
:::

请参阅我们的[文档站点](https://genesis.osaerialrobot.top/user_guide/index.html)了解详细的安装步骤、教程和 API 参考。

### LLM友好文档获取(Beta)

:::{note}
本文档站点非官方站点，由 [GitHub@Atticlmr](https://github.com/Atticlmr) 制作
问题反馈：https://github.com/Atticlmr/genesis-doc-zh-CN/issues
:::
请将以下提示词输入大模型即可使用

```bash

LLm友好文档地址:https://genesis.osaerialrobot.top/llm_docs/
### 使用方法
1. **先读取索引**了解文档结构：
   ```
   https://genesis.osaerialrobot.top/llm_docs/00_INDEX.txt
   ```
2. **按需加载模块**（不要一次性加载全部，避免上下文过长）：
   - 新手入门 → 01_intro + 02_getting_started
   - 机器人控制 → 03_robot_control
   - 物理仿真 → 04_physics_simulation + 09_advanced_topics
   - API 查询 → 10_api_core 及之后的模块
3. **获取具体模块**（示例）：
   ```
   https://genesis.osaerialrobot.top/llm_docs/02_getting_started_入门指南_基础.txt
   ```
### 编码说明
文档使用 UTF-8 编码，获取时请确保使用正确的编码方式解析。
```

## 为 Genesis 贡献

Genesis 项目的目标是构建一个完全透明、用户友好的生态系统，让来自机器人和计算机图形学领域的贡献者能够**齐聚一堂，协作创建一个高效率、真实（包括物理和视觉）的虚拟世界，用于机器人研究及其他领域**。

我们诚挚欢迎社区以*任何形式*做出贡献，让机器人的世界变得更美好。从**新功能的 pull request**、**bug 报告**，到哪怕是让 Genesis API 更直观的微小**建议**，都衷心感谢！

## 支持

- 请使用 Github [Issues](https://github.com/Genesis-Embodied-AI/Genesis/issues)提交 bug 报告和功能请求。

- 请使用 GitHub [Discussions](https://github.com/Genesis-Embodied-AI/Genesis/discussions)讨论想法和提问。

## 引用

如果您在您的研究中使用了 Genesis，我们将非常感谢您能引用它。我们仍在撰写技术报告，在它公开之前，您可以考虑引用：

```
@misc{Genesis,
  author = {Genesis Authors},
  title = {Genesis: A Generative and Universal Physics Engine for Robotics and Beyond},
  month = {December},
  year = {2024},
  url = {https://github.com/Genesis-Embodied-AI/Genesis}
}
```

```{toctree}
:maxdepth: 1

user_guide/index
api_reference/index

```
