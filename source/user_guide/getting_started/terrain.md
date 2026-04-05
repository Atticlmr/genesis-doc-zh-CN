# 🏔️ 地形仿真与生成

Genesis 通过 `gs.morphs.Terrain` morph 为 **高度场地形** 提供一流的支持。地形是一个静态刚体对象，内部由高度图（用于快速碰撞查询）和水密三角网格（用于可视化和 SDF 生成）表示。

本页介绍了创建地形的三种最常见方式：

1. 传入您自己的 NumPy 高度图。
2. 程序化生成 *子地形* 网格（Isaac Gym 风格）。
3. 自动将任意三角网格转换为高度图。

---

## 1  使用自定义高度图
如果您已有地形数据（例如来自 DEM 文件），可以直接将其输入 Genesis。您只需要两个数值：水平比例和垂直比例。

```python
import numpy as np
import genesis as gs

# 1. 初始化 Genesis
gs.init(seed=0, backend=gs.gpu)  # 使用 gs.cpu 表示 CPU 后端

# 2. 创建场景
scene = gs.Scene(show_viewer=True)

# 3. 准备高度图（这里是一个简单的凸起用于演示）
hf = np.zeros((40, 40), dtype=np.int16)
hf[10:30, 10:30] = 200 * np.hanning(20)[:, None] * np.hanning(20)[None, :]

horizontal_scale = 0.25  # 网格点之间的米数
vertical_scale   = 0.005  # 每个高度场单位的米数

# 4. 添加地形实体
scene.add_entity(
    morph=gs.morphs.Terrain(
        height_field=hf,
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
    ),
)

scene.build()

# 运行仿真以便您可以检查表面
for _ in range(1_000):
    scene.step()
```

### 可视化调试技巧
构建场景后，高度图存储在 `terrain.geoms[0].metadata["height_field"]` 中。您可以在每个采样点上绘制小球来查看实际几何形状：

```python
import torch

hf = terrain.geoms[0].metadata["height_field"]
rows = horizontal_scale * torch.arange(hf.shape[0]).unsqueeze(1).repeat(1, hf.shape[1])
cols = horizontal_scale * torch.arange(hf.shape[1]).unsqueeze(0).repeat(hf.shape[0], 1)
heights = vertical_scale * torch.tensor(hf)
poss = torch.stack((rows, cols, heights), dim=-1).reshape(-1, 3)
scene.draw_debug_spheres(poss, radius=0.05, color=(0, 0, 1, 0.7))
```

---

## 2  程序化子地形
`gs.morphs.Terrain` 还可以通过拼接 *子地形* 网格来**合成**复杂地面——与 Isaac Gym 使用的技术相同。您只需指定：

* `n_subterrains=(nx, ny)` – 每个方向的瓦片数量。
* `subterrain_size=(sx, sy)` – 每个瓦片的尺寸（米）。
* `subterrain_types` – 一个二维列表，为每个瓦片选择生成器。

内置生成器的完整列表包括：
`flat_terrain`, `random_uniform_terrain`, `pyramid_sloped_terrain`, `discrete_obstacles_terrain`, `wave_terrain`, `pyramid_stairs_terrain`, `stairs_terrain`, `stepping_stones_terrain`, `fractal_terrain`。

```python
scene = gs.Scene(show_viewer=True)

terrain = scene.add_entity(
    morph=gs.morphs.Terrain(
        n_subterrains=(2, 2),
        subterrain_size=(6.0, 6.0),
        horizontal_scale=0.25,
        vertical_scale=0.005,
        subterrain_types=[
            ["flat_terrain", "random_uniform_terrain"],
            ["pyramid_sloped_terrain", "discrete_obstacles_terrain"],
        ],
    ),
)

scene.build(n_envs=100)  # 您仍然可以运行多个并行环境
```

上面的代码本质上与 Genesis 附带的 `examples/rigid/terrain_subterrain.py` 相同。欢迎打开该示例查看完整的可运行脚本。

---

## 3  从三角网格生成高度图
有时您已经有一个详细的 CAD 或摄影测量网格，只是希望碰撞检测运行得更快。辅助函数 `genesis.utils.terrain.mesh_to_heightfield` 使用垂直光线采样网格，并返回一个 NumPy 高度数组以及网格坐标。

```python
import os
from genesis.utils.terrain import mesh_to_heightfield

# 您的 .obj / .glb / .stl 地形文件路径
mesh_path = os.path.join(gs.__path__[0], "assets", "meshes", "terrain_45.obj")

horizontal_scale = 2.0  # 期望的网格间距（米）
height, xs, ys = mesh_to_heightfield(mesh_path, spacing=horizontal_scale, oversample=3)

# 移动地形，使网格中心变为 (0,0)
translation = np.array([xs.min(), ys.min(), 0.0])

scene = gs.Scene(show_viewer=True)
scene.add_entity(
    morph=gs.morphs.Terrain(
        height_field=height,
        horizontal_scale=horizontal_scale,
        vertical_scale=1.0,
        pos=translation,  # 可选的世界变换
    ),
)
scene.add_entity(gs.morphs.Sphere(pos=(10, 15, 10), radius=1))
scene.build()
```

这个过程被封装在 `examples/rigid/terrain_from_mesh.py` 中。

---

## API 参考
有关完整的关键字参数列表，请参阅自动生成的 API 页面：

```{eval-rst}
.. autoclass:: genesis.options.morphs.Terrain
   :members:
   :show-inheritance:
```

---

### 保存与重复使用地形
创建地形时，Genesis 会生成高度图、用于碰撞检测的水密网格以及用于可视化的简化网格。您可以通过在首次创建地形时传入 `name="my_terrain"` 来启用高度图的缓存，之后将从缓存加载而无需重新生成。这对于精确重建随机化地形非常有用。

---

祝您使用愉快！🧗‍♂️🏔️
