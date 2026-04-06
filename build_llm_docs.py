#!/usr/bin/env python3
"""
将 Genesis 文档转换为 LLM 友好的 txt 格式，按功能模块组织
"""

import os
import re
from pathlib import Path

# 定义功能模块结构
MODULES = {
    "01_intro": {
        "name": "介绍与概述",
        "description": "Genesis 项目介绍、使命和安装指南",
        "files": [
            "source/index.md",
            "source/user_guide/overview/what_is_genesis.md",
            "source/user_guide/overview/why_a_new_simulator.md",
            "source/user_guide/overview/installation.md",
            "source/user_guide/overview/mission.md",
        ]
    },
    "02_getting_started": {
        "name": "入门指南-基础",
        "description": "Genesis 基础概念、可视化、调试和并行仿真",
        "files": [
            "source/user_guide/getting_started/hello_genesis.md",
            "source/user_guide/getting_started/visualization.md",
            "source/user_guide/getting_started/interactive_debugging.md",
            "source/user_guide/getting_started/parallel_simulation.md",
            "source/user_guide/getting_started/control_your_robot.md",
            "source/user_guide/getting_started/miscellaneous.md",
            "source/user_guide/getting_started/misc_guidelines.md",
        ]
    },
    "03_robot_control": {
        "name": "机器人控制",
        "description": "机器人运动控制、逆运动学、约束和路径规划",
        "files": [
            "source/user_guide/getting_started/inverse_kinematics_motion_planning.md",
            "source/user_guide/getting_started/advanced_ik.md",
            "source/user_guide/getting_started/constraints.md",
            "source/user_guide/getting_started/path_planning.md",
        ]
    },
    "04_physics_simulation": {
        "name": "物理仿真",
        "description": "刚体之外的物理仿真、软体机器人、混合实体、地形和发射器",
        "files": [
            "source/user_guide/getting_started/beyond_rigid_bodies.md",
            "source/user_guide/getting_started/soft_robots.md",
            "source/user_guide/getting_started/hybrid_entity.md",
            "source/user_guide/getting_started/terrain.md",
            "source/user_guide/getting_started/emitters.md",
        ]
    },
    "05_sensing_perception": {
        "name": "传感与感知",
        "description": "传感器、相机、射线投射、批量渲染器和记录器",
        "files": [
            "source/user_guide/getting_started/sensors.md",
            "source/user_guide/getting_started/camera_sensors.md",
            "source/user_guide/getting_started/raycaster_patterns.md",
            "source/user_guide/getting_started/batch_renderer.md",
            "source/user_guide/getting_started/recorders.md",
        ]
    },
    "06_rl_training": {
        "name": "强化学习训练",
        "description": "运动任务、无人机、操作任务和域随机化",
        "files": [
            "source/user_guide/getting_started/locomotion.md",
            "source/user_guide/getting_started/hover_env.md",
            "source/user_guide/getting_started/drone_entity.md",
            "source/user_guide/getting_started/manipulation.md",
            "source/user_guide/getting_started/domain_randomization.md",
        ]
    },
    "07_assets_rendering": {
        "name": "资产与渲染",
        "description": "表面纹理、USD 导入和查看器插件",
        "files": [
            "source/user_guide/getting_started/surfaces_textures.md",
            "source/user_guide/getting_started/usd_import.md",
            "source/user_guide/getting_started/viewer_plugin.md",
        ]
    },
    "08_configuration": {
        "name": "配置与约定",
        "description": "配置系统、命名约定",
        "files": [
            "source/user_guide/getting_started/config_system.md",
            "source/user_guide/getting_started/conventions.md",
        ]
    },
    "09_advanced_topics": {
        "name": "高级主题",
        "description": "深入的概念、求解器耦合、碰撞处理、性能分析等",
        "files": [
            "source/user_guide/advanced_topics/concepts.md",
            "source/user_guide/advanced_topics/naming_and_variables.md",
            "source/user_guide/advanced_topics/collision_contacts_forces.md",
            "source/user_guide/advanced_topics/solvers_and_coupling.md",
            "source/user_guide/advanced_topics/ipc_coupler.md",
            "source/user_guide/advanced_topics/sap_coupler.md",
            "source/user_guide/advanced_topics/rigid_constraint_model.md",
            "source/user_guide/advanced_topics/nonrigid_models.md",
            "source/user_guide/advanced_topics/support_field.md",
            "source/user_guide/advanced_topics/checkpoints.md",
            "source/user_guide/advanced_topics/mesh_processing.md",
            "source/user_guide/advanced_topics/multi_gpu.md",
            "source/user_guide/advanced_topics/profiling.md",
            "source/user_guide/advanced_topics/parallel_RL_training.md",
        ]
    },
    "10_api_core": {
        "name": "API参考-核心组件",
        "description": "场景、实体、仿真器的 API 参考",
        "files": [
            "source/api_reference/index.md",
            "source/api_reference/scene/index.md",
            "source/api_reference/scene/scene.md",
            "source/api_reference/scene/simulator.md",
            "source/api_reference/scene/mesh.md",
            "source/api_reference/scene/force_field.md",
            "source/api_reference/entity/index.md",
            "source/api_reference/entity/rigid_entity/index.md",
            "source/api_reference/entity/rigid_entity/rigid_entity.md",
            "source/api_reference/entity/rigid_entity/rigid_geom.md",
            "source/api_reference/entity/rigid_entity/rigid_joint.md",
            "source/api_reference/entity/rigid_entity/rigid_link.md",
            "source/api_reference/entity/rigid_entity/rigid_visgeom.md",
            "source/api_reference/entity/fem_entity.md",
            "source/api_reference/entity/mpm_entity.md",
            "source/api_reference/entity/pbd_entity/index.md",
            "source/api_reference/entity/pbd_entity/pbd_2d.md",
            "source/api_reference/entity/pbd_entity/pbd_3d.md",
            "source/api_reference/entity/pbd_entity/pbd_free_particle.md",
            "source/api_reference/entity/pbd_entity/pbd_particle.md",
            "source/api_reference/entity/pbd_entity/pbd_tet.md",
            "source/api_reference/entity/sph_entity.md",
            "source/api_reference/entity/hybrid_entity.md",
            "source/api_reference/entity/drone_entity.md",
            "source/api_reference/entity/emitter.md",
        ]
    },
    "11_api_visualization": {
        "name": "API参考-可视化与渲染",
        "description": "可视化、渲染器、相机、灯光的 API 参考",
        "files": [
            "source/api_reference/visualization/index.md",
            "source/api_reference/visualization/visualizer.md",
            "source/api_reference/visualization/viewer.md",
            "source/api_reference/visualization/lights.md",
            "source/api_reference/visualization/cameras/index.md",
            "source/api_reference/visualization/cameras/camera.md",
            "source/api_reference/visualization/renderers/index.md",
            "source/api_reference/visualization/renderers/rasterizer.md",
            "source/api_reference/visualization/renderers/raytracer.md",
            "source/api_reference/visualization/renderers/batch_renderer.md",
        ]
    },
    "12_api_sensors": {
        "name": "API参考-传感器",
        "description": "各类传感器的 API 参考",
        "files": [
            "source/api_reference/sensor/index.md",
            "source/api_reference/sensor/camera.md",
            "source/api_reference/sensor/contact.md",
            "source/api_reference/sensor/imu.md",
            "source/api_reference/sensor/raycaster.md",
        ]
    },
    "13_api_recording": {
        "name": "API参考-数据记录",
        "description": "记录器和绘图工具的 API 参考",
        "files": [
            "source/api_reference/recording/index.md",
            "source/api_reference/recording/recorder.md",
            "source/api_reference/recording/recorder_manager.md",
            "source/api_reference/recording/file_writers.md",
            "source/api_reference/recording/plotters.md",
        ]
    },
    "14_api_engine": {
        "name": "API参考-物理引擎",
        "description": "求解器和耦合器的 API 参考",
        "files": [
            "source/api_reference/engine/index.md",
            "source/api_reference/engine/solvers/index.md",
            "source/api_reference/engine/solvers/rigid_solver.md",
            "source/api_reference/engine/solvers/mpm_solver.md",
            "source/api_reference/engine/solvers/fem_solver.md",
            "source/api_reference/engine/solvers/pbd_solver.md",
            "source/api_reference/engine/solvers/sph_solver.md",
            "source/api_reference/engine/solvers/sf_solver.md",
            "source/api_reference/engine/solvers/tool_solver.md",
            "source/api_reference/engine/couplers/index.md",
            "source/api_reference/engine/couplers/ipc_coupler.md",
            "source/api_reference/engine/couplers/sap_coupler.md",
            "source/api_reference/engine/couplers/legacy_coupler.md",
            "source/api_reference/engine/states/index.md",
        ]
    },
    "15_api_materials": {
        "name": "API参考-材质",
        "description": "各类材质的 API 参考",
        "files": [
            "source/api_reference/material/index.md",
            "source/api_reference/material/rigid.md",
            "source/api_reference/material/hybrid.md",
            "source/api_reference/material/fem/index.md",
            "source/api_reference/material/fem/elastic.md",
            "source/api_reference/material/fem/muscle.md",
            "source/api_reference/material/mpm/index.md",
            "source/api_reference/material/mpm/elastic.md",
            "source/api_reference/material/mpm/liquid.md",
            "source/api_reference/material/mpm/sand.md",
            "source/api_reference/material/mpm/snow.md",
            "source/api_reference/material/mpm/elasto_plastic.md",
            "source/api_reference/material/mpm/muscle.md",
            "source/api_reference/material/pbd/index.md",
            "source/api_reference/material/pbd/cloth.md",
            "source/api_reference/material/pbd/elastic.md",
            "source/api_reference/material/pbd/liquid.md",
            "source/api_reference/material/pbd/particle.md",
            "source/api_reference/material/sph/index.md",
            "source/api_reference/material/sph/liquid.md",
        ]
    },
    "16_api_options": {
        "name": "API参考-选项与配置",
        "description": "各种选项和配置的 API 参考",
        "files": [
            "source/api_reference/options/index.md",
            "source/api_reference/options/options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/index.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/sim_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/rigid_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/mpm_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/fem_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/pbd_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/sph_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/sf_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/tool_options.md",
            "source/api_reference/options/simulator_coupler_and_solver_options/coupler_options.md",
            "source/api_reference/options/morph/index.md",
            "source/api_reference/options/morph/morph.md",
            "source/api_reference/options/morph/primitive/index.md",
            "source/api_reference/options/morph/primitive/primitive.md",
            "source/api_reference/options/morph/primitive/plane.md",
            "source/api_reference/options/morph/primitive/box.md",
            "source/api_reference/options/morph/primitive/sphere.md",
            "source/api_reference/options/morph/primitive/cylinder.md",
            "source/api_reference/options/morph/file_morph/index.md",
            "source/api_reference/options/morph/file_morph/file_morph.md",
            "source/api_reference/options/morph/file_morph/mesh.md",
            "source/api_reference/options/morph/file_morph/urdf.md",
            "source/api_reference/options/morph/file_morph/mjcf.md",
            "source/api_reference/options/morph/file_morph/terrain.md",
            "source/api_reference/options/morph/file_morph/drone.md",
            "source/api_reference/options/surface/index.md",
            "source/api_reference/options/surface/surface.md",
            "source/api_reference/options/surface/plastic/index.md",
            "source/api_reference/options/surface/plastic/plastic.md",
            "source/api_reference/options/surface/plastic/default.md",
            "source/api_reference/options/surface/plastic/smooth.md",
            "source/api_reference/options/surface/plastic/rough.md",
            "source/api_reference/options/surface/plastic/reflective.md",
            "source/api_reference/options/surface/plastic/collision.md",
            "source/api_reference/options/surface/metal/index.md",
            "source/api_reference/options/surface/metal/metal.md",
            "source/api_reference/options/surface/metal/gold.md",
            "source/api_reference/options/surface/metal/aluminium.md",
            "source/api_reference/options/surface/metal/copper.md",
            "source/api_reference/options/surface/metal/iron.md",
            "source/api_reference/options/surface/glass/index.md",
            "source/api_reference/options/surface/glass/glass.md",
            "source/api_reference/options/surface/glass/water.md",
            "source/api_reference/options/surface/emission/index.md",
            "source/api_reference/options/surface/emission/emission.md",
            "source/api_reference/options/texture/index.md",
            "source/api_reference/options/texture/texture.md",
            "source/api_reference/options/texture/color_texture.md",
            "source/api_reference/options/texture/image_texture.md",
            "source/api_reference/options/vis/index.md",
            "source/api_reference/options/vis/vis.md",
            "source/api_reference/options/vis/viewer.md",
            "source/api_reference/options/renderer/index.md",
            "source/api_reference/options/renderer/renderer.md",
            "source/api_reference/options/renderer/rasterizer.md",
            "source/api_reference/options/renderer/raytracer.md",
            "source/api_reference/options/renderer/batchrenderer.md",
        ]
    },
    "17_api_utilities": {
        "name": "API参考-工具函数",
        "description": "工具函数和辅助功能的 API 参考",
        "files": [
            "source/api_reference/utilities/index.md",
            "source/api_reference/utilities/constants.md",
            "source/api_reference/utilities/device.md",
            "source/api_reference/utilities/geometry.md",
            "source/api_reference/utilities/file_io.md",
            "source/api_reference/utilities/tensor_utils.md",
        ]
    },
    "18_api_differentiation": {
        "name": "API参考-可微分仿真",
        "description": "可微分仿真相关的 API 参考",
        "files": [
            "source/api_reference/differentiation/index.md",
            "source/api_reference/differentiation/tensor.md",
            "source/api_reference/differentiation/creation_ops.md",
        ]
    },
    "19_roadmap": {
        "name": "路线图",
        "description": "Genesis 项目的发展路线图",
        "files": [
            "source/roadmap/index.md",
        ]
    },
}


def clean_markdown(content):
    """清理 Markdown 格式，转换为纯文本"""
    # 移除 toctree 指令
    content = re.sub(r'```\{toctree\}.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r':::\{toctree\}.*?:::', '', content, flags=re.DOTALL)
    
    # 移除 figure 指令
    content = re.sub(r'```\{figure\}.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r':::\{figure\}.*?:::', '', content, flags=re.DOTALL)
    
    # 移除 note/warning 等 admonition 的格式标记，保留内容
    content = re.sub(r'```\{(note|warning|tip|important|caution)\}', r'\1:', content)
    content = re.sub(r':::\{(note|warning|tip|important|caution)\}', r'\1:', content)
    content = re.sub(r'```', '', content)
    content = re.sub(r':::', '', content)
    
    # 转换 Markdown 图片为文本描述
    content = re.sub(r'!\[(.*?)\]\(.*?\)', r'[图片: \1]', content)
    
    # 保留链接但简化格式
    content = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', content)
    
    # 处理标题 - 保留格式
    content = re.sub(r'^#{1,6}\s+', lambda m: m.group(0), content, flags=re.MULTILINE)
    
    # 处理代码块标记
    content = re.sub(r'```python', '\n[Python 代码]:', content)
    content = re.sub(r'```bash', '\n[Bash 代码]:', content)
    content = re.sub(r'```', '\n[/代码]', content)
    
    # 清理多余的空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content


def read_file(filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"\n[错误: 无法读取文件 {filepath}: {e}]\n"


def process_module(module_id, module_info, output_dir):
    """处理一个模块，生成对应的 txt 文件"""
    output_file = output_dir / f"{module_id}_{module_info['name'].replace(' ', '_').replace('-', '_')}.txt"
    
    lines = []
    lines.append("=" * 80)
    lines.append(f"模块: {module_info['name']}")
    lines.append(f"描述: {module_info['description']}")
    lines.append("=" * 80)
    lines.append("")
    
    for filepath in module_info['files']:
        if os.path.exists(filepath):
            content = read_file(filepath)
            cleaned = clean_markdown(content)
            lines.append("-" * 80)
            lines.append(f"文件: {filepath}")
            lines.append("-" * 80)
            lines.append(cleaned)
            lines.append("")
            lines.append("")
        else:
            lines.append(f"[警告: 文件不存在: {filepath}]")
            lines.append("")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return output_file.name, len(lines)


def generate_index(modules, output_dir):
    """生成主索引文件"""
    index_file = output_dir / "00_INDEX.txt"
    
    lines = []
    lines.append("=" * 80)
    lines.append("Genesis 物理仿真引擎 - LLM 友好文档索引")
    lines.append("=" * 80)
    lines.append("")
    lines.append("本文档是 Genesis 物理仿真引擎的中文文档，专为 LLM 处理优化。")
    lines.append("文档按功能模块组织，共包含 19 个模块。")
    lines.append("")
    lines.append("-" * 80)
    lines.append("模块列表")
    lines.append("-" * 80)
    lines.append("")
    
    for module_id in sorted(modules.keys()):
        module = modules[module_id]
        filename = f"{module_id}_{module['name'].replace(' ', '_').replace('-', '_')}.txt"
        lines.append(f"{module_id}: {module['name']}")
        lines.append(f"  文件: {filename}")
        lines.append(f"  描述: {module['description']}")
        lines.append(f"  包含 {len(module['files'])} 个文档文件")
        lines.append("")
    
    lines.append("-" * 80)
    lines.append("使用建议")
    lines.append("-" * 80)
    lines.append("")
    lines.append("1. 新手入门: 请按顺序阅读 01_intro -> 02_getting_started")
    lines.append("2. 机器人控制: 阅读 03_robot_control")
    lines.append("3. 物理仿真: 阅读 04_physics_simulation")
    lines.append("4. API 参考: 根据需要查阅 10_api_core 及之后的模块")
    lines.append("")
    lines.append("=" * 80)
    lines.append("文档说明")
    lines.append("=" * 80)
    lines.append("")
    lines.append("本文档基于 Sphinx MyST 格式的 Markdown 源文件生成，")
    lines.append("已转换为纯文本格式以便于 LLM 处理。")
    lines.append("代码示例使用 Python 语言。")
    lines.append("")
    lines.append("项目官网: https://genesis-embodied-ai.github.io/")
    lines.append("GitHub: https://github.com/Genesis-Embodied-AI/Genesis")
    lines.append("中文文档源: https://github.com/Atticlmr/genesis-doc-zh-CN")
    lines.append("")
    lines.append("=" * 80)
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return index_file.name


def main():
    # 创建输出目录
    output_dir = Path("llm_docs")
    output_dir.mkdir(exist_ok=True)
    
    print("开始生成 LLM 友好文档...")
    print(f"输出目录: {output_dir.absolute()}")
    print()
    
    # 处理每个模块
    generated_files = []
    for module_id in sorted(MODULES.keys()):
        module_info = MODULES[module_id]
        print(f"处理模块: {module_id} - {module_info['name']}")
        filename, line_count = process_module(module_id, module_info, output_dir)
        generated_files.append((filename, module_info['name'], len(module_info['files'])))
    
    # 生成索引
    index_name = generate_index(MODULES, output_dir)
    
    print()
    print("=" * 60)
    print("文档生成完成!")
    print("=" * 60)
    print()
    print(f"索引文件: {index_name}")
    print()
    print("生成的模块文件:")
    for filename, name, file_count in generated_files:
        print(f"  - {filename}")
        print(f"    ({name}, {file_count} 个源文件)")
    print()
    print(f"总计: {len(generated_files)} 个模块文件 + 1 个索引文件")
    print(f"输出位置: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
