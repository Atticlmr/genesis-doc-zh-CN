# 🎲 域随机化

随机化物理和视觉属性以实现鲁棒的强化学习训练。

## 物理随机化

在 `scene.build()` 之后应用：

```python
import genesis as gs
import torch

scene.build(n_envs=64)

# 摩擦随机化
robot.set_friction_ratio(
    friction_ratio=0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=range(robot.n_links),
)

# 质量随机化
robot.set_mass_shift(
    mass_shift=-0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=range(robot.n_links),
)

# 质心随机化
robot.set_COM_shift(
    com_shift=-0.05 + 0.1 * torch.rand(scene.n_envs, robot.n_links, 3),
    links_idx_local=range(robot.n_links),
)
```

## 控制参数随机化

```python
import numpy as np

# 每环境的刚度 (Kp)
kp_values = 4000 + 1000 * np.random.rand(scene.n_envs, robot.n_dofs)
robot.set_dofs_kp(kp_values, motors_dof)

# 每环境的阻尼 (Kv)
kv_values = 400 + 100 * np.random.rand(scene.n_envs, robot.n_dofs)
robot.set_dofs_kv(kv_values, motors_dof)
```

## 物体位置随机化（每回合）

```python
def reset_idx(self, envs_idx):
    num_reset = len(envs_idx)

    # 随机物体位置
    random_x = torch.rand(num_reset, device=gs.device) * 0.4 + 0.2
    random_y = (torch.rand(num_reset, device=gs.device) - 0.5) * 0.5
    random_z = torch.ones(num_reset, device=gs.device) * 0.025
    random_pos = torch.stack([random_x, random_y, random_z], dim=-1)

    self.object.set_pos(random_pos, envs_idx=envs_idx)
```

## 指令随机化

```python
def gs_rand(lower, upper, shape):
    """在 [lower, upper] 范围内的均匀随机"""
    return (upper - lower) * torch.rand(shape, device=gs.device) + lower

# 随机化速度指令
commands = gs_rand(
    lower=torch.tensor([-1.0, -0.5, -0.5]),
    upper=torch.tensor([1.0, 0.5, 0.5]),
    shape=(self.num_envs, 3),
)
```

## 可用方法

| 方法 | 形状 | 描述 |
|--------|-------|-------------|
| `set_friction_ratio` | (n_envs, n_links) | 摩擦缩放 |
| `set_mass_shift` | (n_envs, n_links) | 质量偏移 |
| `set_COM_shift` | (n_envs, n_links, 3) | 质心偏移 |
| `set_dofs_kp` | (n_envs, n_dofs) | 位置增益 |
| `set_dofs_kv` | (n_envs, n_dofs) | 速度增益 |
| `set_dofs_armature` | (n_envs, n_dofs) | 电机惯量 |

## 所需选项

为物理随机化启用批处理：

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        batch_dofs_info=True,
        batch_links_info=True,
    ),
)
```

## 最佳实践

1. 在 `scene.build()` 后应用一次物理 DR
2. 在每个回合重置时应用位置/指令 DR
3. 使用 `envs_idx` 参数进行选择性随机化
4. 确保张量形状匹配 `(n_envs, ...)`


## 下一章节

- [并行仿真](../../parallel_simulation) — 运行并行仿真用于强化学习训练
- [运动控制](../examples/locomotion) — 在运动控制端到端策略中使用域随机化