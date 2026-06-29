# 🎱 刚体碰撞

Genesis 中的刚体碰撞分为两个阶段：先找出哪些物体发生接触，再计算用于解析这些接触的冲量。下面两页分别介绍这两个阶段的算法内容。

- [**刚体碰撞检测**](collision_contacts_forces) - 粗阶段裁剪与精阶段接触流形生成，包括 Sweep & Prune、GJK、MPR 和特殊情形处理。
- [**刚体碰撞解析**](rigid_constraint_model) - 约束公式、接触与摩擦模型、关节限制、等式约束以及数值求解器（PCG、Newton-Cholesky）。

```{toctree}
:hidden:
:maxdepth: 1

collision_contacts_forces
rigid_constraint_model
```
