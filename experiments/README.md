# 研究脚本

数学语义见 [DESIGN](../docs/DESIGN.md)，完整运行命令见 [REPRODUCING](../docs/REPRODUCING.md)。

| 文件 | 用途与证据范围 |
|---|---|
| [castillon.py](castillon.py) | Fraction 与二次扩域几何、固定夹具的逐笔构造；不是通用任意输入执行器 |
| [replay_baseline.py](replay_baseline.py) | 生成五种裁剪程序与真实 E 台账 |
| [replay_secant_seed.py](replay_secant_seed.py) | AB 严格割圆子域的 9/11/12/13/15 E 程序 |
| [verify_secant_seed_sage.py](verify_secant_seed_sage.py) | 割线构造六参数恒等式、20 份独立重放和覆盖缺口 |
| [verify_sage.py](verify_sage.py) | 独立求交闭包、计分、目标及五参数恒等式 |
| [classify_sage.py](classify_sage.py) | 完整解数分类、六参数恒等式与独立固定点计数 |
| [search_prefix_suffix.py](search_prefix_suffix.py) | 固定前缀后的有界连接线筛查 |
| [search_one_move_finish.py](search_one_move_finish.py) | 选定前缀后一笔线/圆直接命中的筛查 |
| [search_chord_trees.py](search_chord_trees.py) | 受限弦线树与交叉弦轴构造的枚举 |
| [search_secant_chords.py](search_secant_chords.py) | AB 起步的 625 个弦线树前缀与一步直接命中筛查，需要 NumPy |
| [search_secant_mixed.py](search_secant_mixed.py) | 固定五笔割线前缀后的两笔混合操作与直接命中筛查，需要 NumPy |
| [verify_secant_search_sage.py](verify_secant_search_sage.py) | 数值初筛候选的独立精确重建、目标检查与 9 E 阳性校准 |

生成数据保存到 [results](results/README.md)。搜索范围与未覆盖候选见 [SEARCH](../docs/SEARCH.md)。
有界未命中不成为全局最小性证据；[Manim 动画](../animations/castillon/README.md)读取验证后的精确轨迹。
