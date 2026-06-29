# 🌱 Genesis World 是什么

![Genesis World teaser](https://raw.githubusercontent.com/YilingQiao/Genesis/readme-assets/videos/HeroShot_Final.png)

**Genesis World** 是面向物理 AI 开发的仿真平台。它把统一的多物理引擎、照片级真实渲染器 [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)，以及跨平台编译器 [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) 放在同一个 Pythonic 仿真接口之后。Genesis World 既能从单台笔记本上的 kernel 扩展到数据中心级 GPU，也保持了适合研究代码阅读、扩展和嵌入的接口。

它以前名为 **Genesis**，最早是 2024 年 12 月启动的学术项目；现在其开发由 [Genesis AI](https://www.genesis.ai/) 正式支持。更多技术背景见我们的 [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward)。

## 技术栈

Genesis World 包含四层。上层是你构建的机器人环境、机器学习流水线或智能体仿真；下层是你拥有的计算后端。

- **Simulation Interface**：面向用户的 API，包括资产解析（URDF、MJCF、OBJ、GLB、USD 等）、实体访问器、控制器、传感器、并行/异构环境和内置 GUI。
- **Physics**：统一的多物理引擎，集成 Rigid、FEM、MPM、Particle（PBD / SPH）、[uipc](https://github.com/spiriMirror/libuipc)、显式耦合器和 SAP，并共享同一个场景与状态。
- **Render**：三条渲染路径都作为相机传感器接入：**[Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)**（Genesis 自研、面向机器人任务的渲染器）、**Luisa**（DSL 光线追踪器）和 **Pyrender**（光栅化器）。
- **Compiler**：**[Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)** 会把 Python kernel code 降低到 CUDA、AMD ROCm、Apple Metal、Vulkan、x86 和 ARM64，并承载 Genesis World 的自动微分、GPU graphs 和 fastcache 机制。
