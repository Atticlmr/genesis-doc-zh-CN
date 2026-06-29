# 🧭 最佳实践

用于编写可在 Genesis 上扩展的 RL 训练流水线的模式和工具。

- [**编写高效的 RL 环境**](efficient_environment) - 预分配缓冲区、布尔掩码 `envs_idx`、零拷贝状态访问器、高效机器人重置和命令下发，以及基于 errno 的终止。
- [**域随机化**](domain_randomization) - 在多环境中随机化物理参数，以训练泛化能力更强的策略。

```{toctree}
:hidden:
:maxdepth: 1

efficient_environment
domain_randomization
```
