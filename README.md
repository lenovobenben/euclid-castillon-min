# Euclid-Castillon-Min · 圆内接三角形的尺规构造

**简体中文** · [English](README.en.md)

**只画 14 条直线，完成一个目标三角形；只画 17 条直线，完成两个目标三角形。**

研究 Cramer–Castillon 问题的 E 步优化：给定一个带圆心的圆和三个点，
构造内接三角形，使三边所在直线分别经过三个给定点。

提供逐笔构造、一般参数证明、独立精确核验、解数分类与有界搜索记录。
**14、17 E 是一般位置上的已验证上界，尚未证明全局最小，完整域鲁棒上界待研究。**

[逐笔构造与证明](docs/CONSTRUCTION.md) · [输入条件与解数](docs/CLASSIFICATION.md) ·
[独立核验](experiments/results/sage-verification.json)

Manim 动画将在后续补充。

## E 步计数

基础计数沿用 [Euclid-Min](https://github.com/lenovobenben/euclid-min) 与
[Euclid-CCC-Min](https://github.com/lenovobenben/euclid-ccc-min)：

- 两个已有不同点确定一条直线，1 E。
- 一个已有点为圆心、经过另一个已有点画圆，1 E；使用塌圆规。
- 已有对象的确定有限实交点及命名，0 E。
- 禁止任取点；三点作圆、中垂线、平行线等宏必须展开。
- 实际重复绘制仍然收费。初始对象和目标不同，分数不能直接比较。

## 当前上界

免费输入：圆 Γ、其圆心 O，以及互异、不共线、不在 Γ 上的 A、B、C。
不免费提供圆周点、半径端点、坐标轴或任何直线。

首先研究恰有两个非退化解的输入域 D₂；边的延长线可以经过给定点。
设 S 为 ABC 面积，p_P=OP²−R²，令 K=4R²S²+p_Ap_Bp_C。
令 e 为三个“给定点的切点恰好落在另外两点连线上”的个数之和，
则 **D₂ 的充要条件为 K>0 且 e=0**。
无解、唯一解、两解、无穷多解的完整充要条件、退化检查和证明见
[输入条件与解数分类](docs/CLASSIFICATION.md)。
当前程序覆盖其中的一般位置子域，尚未补齐全部中间退化情形。

| 目标 | 直线 | 新增圆 | E |
|---|---:|---:|---:|
| 得到两个解各自的起始顶点 | 11 | 0 | 11 |
| 得到任意一个解的三个顶点 | 13 | 0 | 13 |
| 实际画出任意一个完整三角形 | 14 | 0 | 14 |
| 得到两个解的全部顶点 | 15 | 0 | 15 |
| 实际画出两个完整三角形 | 17 | 0 | 17 |

这些是不同目标程序的已验证上界，**不是全局最少步数**。
“圆为零”指零个新增圆；免费输入圆始终参与求交。
`gen` 覆盖二解域中相对开稠密、满测度的一般位置子域；当前没有 `rob` 完整域成绩。
输入、目标和声明等级见 [DESIGN](docs/DESIGN.md)。

## 构造与验证

构造使用圆上射影变换的不动点轴，选择确定性起始弦，并在三个投影点对之间共享已有弦。
所有笔画均展开为过两个已有点的直线。

- [逐笔构造、证明和适用条件](docs/CONSTRUCTION.md)
- [完整输入条件、存在性、解数与退化分类](docs/CLASSIFICATION.md)
- [研究配置](profiles/castillon-d2-e-generic-v1.json)
- [标准库精确重放](experiments/replay_baseline.py)
- [独立 Sage 验证器与一般参数恒等式](experiments/verify_sage.py)
- [标准库证书](experiments/results/baseline.json)
- [Sage 验证报告](experiments/results/sage-verification.json)
- [解数分类的 Sage 验证报告](experiments/results/classification-verification.json)
- [已检查搜索范围及限制](docs/SEARCH.md)

四个有理数夹具覆盖全外点、混合内外点、全内点的正常二解构型；
构造只需要有理运算和最后一个实二次扩域。标准库重放完全不用浮点判定。
独立 Sage 验证器不导入标准库几何实现，重新计算交点、自动交点闭包、
实际步数、重复绘制、目标和首次命中时刻。

Sage 另外在五个独立参数的多项式环中验证三个对应点对、两个轴上辅助点、
最终轴和复合矩阵的一致性及非恒等退化，提供一般位置正确性的代数依据。
有限夹具通过与一般参数恒等式证明是分别记录的证据。

## 复现

标准库重放和有界搜索：

```sh
python3 experiments/replay_baseline.py --output experiments/results/baseline.json
python3 -m unittest discover -v
python3 experiments/search_prefix_suffix.py
python3 experiments/search_one_move_finish.py
python3 experiments/search_chord_trees.py
```

独立验证使用 SageMath 10.7。先取得对应 Docker 镜像；验证本身断网运行，项目只读挂载：

```sh
docker run --rm --network none \
  -v "$PWD:/workspace:ro" -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify_sage.py > experiments/results/sage-verification.json
```

判定公式的一般恒等式和 21 个精确分类实例另运行
`experiments/classify_sage.py`，输出保存到 `experiments/results/classification-verification.json`，完整命令见 [分类文档](docs/CLASSIFICATION.md#8-可复核证据与复现)。

## 下一步研究范围

1. 使用已有线线交点作为新弦的定义点，扩大当前 A/B/C 弦线树前缀。
2. 比较混合直线与基础圆的短程序，目标是优先突破 14 E 单解完整三角形。
3. 比较不先画不动点轴、直接命中任意目标顶点的路线。
4. 建立中间退化分类和带最坏成本的修复分支，另列 `rob` 上界。
5. 单解、双解共享构造和下界分开研究；不将有界未命中写成最小性证明。

优先级、搜索边界和未来动画安排见 [ROADMAP](docs/ROADMAP.md)。

## 来源

圆上对应的不动点及交叉弦交点轴路线见 Maurice Starck，
[*Castillon’s problem*](https://www.polyhedra-world.nc/stuff/Castillon.pdf)，2002。
本项目的工作是冻结本题 E 配置、选择确定性起始弦、复用已有弦、展开逐笔程序，
以及建立精确重放、一般参数验证与有界搜索台账。
目前不主张经典构造路线或当前步数的文献首创性。

详细来源及计数可比性见 [LITERATURE](docs/LITERATURE.md)。

## 文档与代码入口

| 内容 | 入口 |
|---|---|
| 输入、目标、计分和声明等级 | [DESIGN](docs/DESIGN.md) |
| 十七笔构造与证明 | [CONSTRUCTION](docs/CONSTRUCTION.md) |
| 存在性与解数判定 | [CLASSIFICATION](docs/CLASSIFICATION.md) |
| 研究优先级与动画计划 | [ROADMAP](docs/ROADMAP.md) |
| 已有搜索范围 | [SEARCH](docs/SEARCH.md) |
| 出处与计数可比性 | [LITERATURE](docs/LITERATURE.md) |
| 精确重放、符号核验与搜索 | [experiments](experiments/) |
| 构造证书、报告与搜索数据 | [experiments/results](experiments/results/) |

## 许可与引用

代码、测试和配置采用 [Apache 2.0](LICENSE)；数学文档、构造记录和研究数据采用
[CC BY 4.0](LICENSE-CONTENT)。第三方材料保持其原有权利，详见 [许可范围](LICENSE-SCOPE.md)。

引用时请注明 **lenovobenben，Euclid-Castillon-Min**、[仓库地址](https://github.com/lenovobenben/euclid-castillon-min)
及所用提交或版本；转载或改编非软件内容时按 CC BY 4.0 署名并注明修改。
