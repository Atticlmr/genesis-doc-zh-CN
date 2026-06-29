# 🤝 耦合器

耦合器是 Genesis 各个求解器之间的桥梁，用于处理由不同物理模型仿真的实体之间的力和交互。Genesis 提供两个接触处理后端，它们适用于不同场景：

- [**IPC Coupler**](ipc_coupler) - 面向布料以及高变形弹性/塑性体的平滑屏障接触。它适合烹饪、骑行等复杂软体交互，不需要降阶抽象，只需要初始顶点位置；同时也可以与刚体动力学配合使用。
- [**SAP Coupler**](sap_coupler) - 用于中等变形体积软体的半解析原始求解器，介于刚体和 IPC 之间，适合 FEM 风格的连续体动力学。

```{toctree}
:hidden:
:maxdepth: 1

ipc_coupler
sap_coupler
```
