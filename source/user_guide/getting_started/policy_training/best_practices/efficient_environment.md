# 🏎️ 编写高效的 RL 环境

当数千个环境在单张 GPU 上并行运行时，吞吐量最关键的不是 `step` 做了什么，而是它没有做什么。下面这些模式能让 `env.step()` 避免 GPU 同步：不要在每步使用 Python 侧 `.item()` / `.nonzero()`，不要触发隐式主机-设备传输，也不要反复重新分配缓冲区。

## 预分配所有缓冲区

把 `step` 和 `reset` 会写入的所有张量一次性分配好，形状和 dtype 都使用最终形式。对于每步都会完全覆盖的缓冲区，使用 `torch.empty(...)`；只有初始值有意义时才使用 `torch.zeros(...)`，例如累加器。

```python
# 好：只分配一次
self.obs_buf = torch.empty((num_envs, num_obs), dtype=gs.tc_float, device=gs.device)
self.reset_buf = torch.ones((num_envs,), dtype=gs.tc_bool, device=gs.device)
self.episode_length_buf = torch.empty((num_envs,), dtype=gs.tc_int, device=gs.device)
```

在 `step` 内重新分配（例如每步 `torch.zeros(...)`）会在环境数量增加后显著降低吞吐量：每次分配都会触碰 CUDA 缓存分配器，并与未完成工作同步。

同样，优先写入已有存储，而不是替换张量对象：

```python
# 差：每步分配新张量
self.commands = torch.where(reset_mask[:, None], new_commands, self.commands)

# 好：写入已有缓冲区
torch.where(reset_mask[:, None], new_commands, self.commands, out=self.commands)
```

`out=` 形式会保持 `self.commands` 指向同一块存储。如果 recorder、logger 或观测构造器持有它的 view，这一点尤其重要。`.copy_(...)` 相比 `=`、`.masked_fill_(...)` 相比不带 `out=` 的 `torch.where(...)` 也是同样道理。

## 对 envs_idx 使用布尔掩码

`(condition).nonzero()[:, 0]` 会强制 GPU 同步，因为主机需要知道产生了多少索引才能构造一维张量。请让 `envs_idx` 一直保持为布尔掩码，并直接传给 Genesis API、`torch.where` 或 `masked_fill_`。

```python
# 差：.nonzero() 触发 GPU 同步
reset_idx = self.reset_buf.nonzero()[:, 0]
self.last_actions[reset_idx] = 0.0

# 好：布尔掩码，无同步
self.last_actions.masked_fill_(self.reset_buf[:, None], 0.0)
```

Genesis 的求解器和实体 setter（`set_qpos`、`set_dofs_position`、`set_pos` 等）都接受布尔掩码形式的 `envs_idx`。统一的 `reset(envs_idx=mask)` 入口也一样。

## 通过零拷贝访问器读取状态

在热路径中读取实体状态是可以的，前提是访问器返回 Genesis 底层存储的零拷贝 view。目前刚体实体支持零拷贝的读取包括：

| 读取 | 返回 |
|---|---|
| `entity.get_pos()` / `entity.get_quat()` | base link 世界位姿 |
| `entity.get_vel()` / `entity.get_ang()` | base link 线速度 / 角速度 |
| `entity.get_dofs_position()` / `entity.get_dofs_velocity()` | 每个 DOF 的位置 / 速度 |
| `entity.get_links_pos()` / `entity.get_links_quat()` / `entity.get_links_vel()` | 每个 link 的世界位姿和速度 |
| `entity.get_contacts()` | 该实体的活跃接触集合 |

其他读取如果放在热路径中，很可能会分配新张量。请把它移出 `step()`，或者在确实应该支持零拷贝时提交 issue。

对于传感器输出，如果一次观测很多传感器，优先使用批量 `scene.read_sensors()` / `entity.read_sensors()`，而不是逐个调用 `sensor.read()`。批量读取按传感器类别返回一个张量，虽然仍会分配新存储，但成本会摊销到该类别的所有传感器上。参见 {doc}`传感器 <../../sensors/index>` 中的批量读取 API。

## 重置机器人状态

无 GPU 同步地重置一批环境需要组合使用：布尔掩码 `envs_idx`、显式预分配源张量的零拷贝 setter，以及 `skip_forward=True`。这样正向运动学会在下一次 `scene.step()` 中统一计算，而不是在每个 setter 内重复计算。

```python
# `mask` 是 (num_envs,) bool 张量；`init_qpos` 在 __init__ 中预分配
self.robot.set_qpos(self.init_qpos, envs_idx=mask, zero_velocity=True, skip_forward=True)
self.robot.set_dofs_velocity(self.init_dof_vel, envs_idx=mask, skip_forward=True)
```

重置所有环境时，传入 `envs_idx=None`（或省略它）。实现会走更快的“完整覆盖”路径，跳过逐环境掩码处理。推荐写成一个 `reset(envs_idx=None | bool_mask)` 入口，并只分支一次：

```python
def reset(self, envs_idx=None):
    self.robot.set_qpos(self.init_qpos, envs_idx=envs_idx, zero_velocity=True, skip_forward=True)

    if envs_idx is None:
        self.last_actions.zero_()
        self.episode_length_buf.zero_()
        self.reset_buf.fill_(True)
    else:
        self.last_actions.masked_fill_(envs_idx[:, None], 0.0)
        self.episode_length_buf.masked_fill_(envs_idx, 0)
        self.reset_buf.masked_fill_(envs_idx, True)
```

对于一次性触碰所有求解器状态的粗粒度重置，`scene.rigid_solver.set_state(state_idx, state, envs_idx=mask, partial=True)` 是对应的批量接口。`partial=True` 是快速路径；`partial=False` 会重置整个场景，因为要重建辅助状态，速度明显更慢。

数值爆炸（NaN 位置、速度发散、约束求解失败）应该只终止对应环境，而不是让整批环境崩溃。刚体求解器暴露了逐环境 errno 掩码，可以把它并入常规终止条件，然后在下一次 `reset(self.reset_buf)` 中用同一套机制重置发散环境：

```python
self.reset_buf = self.episode_length_buf > self.max_episode_length
self.reset_buf |= torch.abs(self.base_euler[:, 1]) > self.cfg["termination_if_pitch_greater_than"]
self.reset_buf |= self.scene.rigid_solver.get_error_envs_mask()
```

## 下发命令

命令下发是另一个写入侧热路径。刚体实体上的零拷贝命令写入包括：

| 写入 | 效果 |
|---|---|
| `entity.control_dofs_position(targets)` | 选中 DOF 的 PD 目标位置 |
| `entity.control_dofs_velocity(targets)` | PD 目标速度 |
| `entity.control_dofs_force(forces)` | 直接广义力 |
| `entity.set_dofs_stiffness(...)` / `entity.set_dofs_damping(...)` | PD 增益 |
| `entity.set_dofs_velocity(vel, envs_idx=mask, skip_forward=True)` | 直接写入速度 |
| `entity.set_qpos(qpos, envs_idx=mask, zero_velocity=..., skip_forward=...)` | 直接写入配置 |

调用时有几个重要模式：

- **让动作向量中的 DOF 顺序匹配实体内部 DOF 顺序**，这样可以传入 `slice(start, stop)`，而不是索引张量。slice 是免费的，索引张量会强制 gather。Go2 示例会预计算 `actions_dof_idx = torch.argsort(self.motors_dof_idx)`，把按关节名排列的策略输出重排成适合 slice 的顺序后再调用。
- **跨 step 复用同一个目标缓冲区。** 把 `target_dof_pos` 写入预分配张量（例如初始化时 `torch.empty_like(self.actions)`，之后使用 `out=` 写入），避免每次调用都让 `actions * scale + default` 产生新张量。
- **不要为了跳过非驱动 DOF 而用索引切片动作张量。** 要么让策略输出包含这些 DOF 并写入一个 slice，要么通过 `motors_dof_idx` 传入 `slice(...)`。
