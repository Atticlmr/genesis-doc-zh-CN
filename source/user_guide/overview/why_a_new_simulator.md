# 🧬 为什么需要一个新的物理仿真器

与以往的仿真平台相比，这里我们重点介绍 Genesis 的几个关键特性：

- 🐍 **Pythonic**且完全透明。Genesis 使用 Python 开发并完全开源，使代码理解和贡献变得更加容易。
- 👶 **effortless 安装**和**极其简单**、**用户友好**的 API 设计。
- 🚀 **并行仿真**具有***前所未有的速度***：Genesis 是**世界上最快的物理引擎**，仿真速度比现有的*GPU 加速*机器人仿真器（Isaac Gym/Sim/Lab、Mujoco MJX 等）快***10~80 倍***（是的，这有点科幻），且在仿真精度和保真度上***没有任何妥协***。
- 💥 一个**统一**的框架，支持各种最先进的物理求解器，建模**广泛的材料**和物理现象。Genesis 还开发了与 [IPC](https://github.com/spiriMirror/libuipc) 的强耦合，以支持更精确的 FEM 仿真。
- 📸 具有优化性能的照片级真实感渲染。我们构建了面向机器人应用的高性能照片级真实渲染器 [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)。
- 📐 **可微性**：Genesis 设计为与可微仿真兼容。我们大幅改进了 [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) 编译器中的自动微分基础设施，并为一些复杂 kernel 手动推导反向传播以提升可微能力。
- ☝🏻 内置**完整传感器系统**：除了物理精确且可微的**触觉**传感器，还包括 **IMU**、**lidar**、**深度相机**、**接触力**、**表面距离**和**温度网格**传感器，均可直接用于并行和异构环境。基于相机的渲染（Nyx / Luisa / Pyrender）也通过同一传感器接口暴露。
