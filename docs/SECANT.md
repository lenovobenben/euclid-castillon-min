# 割线起步的 12 E 单解与 15 E 双解

在二解域 D₂ 中，若直线 AB 与 Γ 有两个不同实交点，可以在一般位置下将
不动点轴入口缩至 9 E，得到以下受限域上界。所有动作均为直线。

| 目标 | 圆心弦程序 | AB 割线程序 |
|---|---:|---:|
| 一个解的三个顶点 | 13 E | **11 E** |
| 一个完整三角形 | 14 E | **12 E** |
| 两个解的全部顶点 | 15 E | **13 E** |
| 两个完整三角形 | 17 E | **15 E** |

三个输入点均在圆内的 D₂ 输入自动满足割线条件。
四行分别裁剪程序；13 E 全顶点程序省去两次第三条边的绘制。

## 适用域

沿用免费输入 Γ、O、A、B、C 和原有 E 计数规则，增加严格割线条件。
单位圆坐标下，若 AB 的方程为 `lx x + ly y + lz = 0`，条件为

```math
l_x^2+l_y^2-l_z^2>0.
```

此外要求辅助圆周点 U、V、W、T、R、P 互异，定位点不同，
J、H 有限且不同。这些条件给出严格割线子域内相对开稠密、满测度的一般位置范围。
程序使用已选择的 AB；若通过实际绘线试选其他输入点对，所画的尝试线也计费。

## 十五笔构造

| E | 实际画出的直线 | 自动出现或命名的点 |
|---:|---|---|
| 1 | AB | U、V 为与 Γ 的两个不同交点 |
| 2 | CU | W 为另一圆交点 |
| 3 | CV | T 为另一圆交点 |
| 4 | BW | R 为另一圆交点 |
| 5 | AR | P 为另一圆交点 |
| 6 | UT | — |
| 7 | VW | J=UT∩VW |
| 8 | TP | H=TP∩AB |
| 9 | JH | X₀、X₁ 为与 Γ 的两个交点 |
| 10 | AX₀ | Y₀ 为另一圆交点 |
| 11 | BY₀ | Z₀ 为另一圆交点，单解顶点齐备 |
| 12 | Z₀X₀ | 第一完整三角形齐备 |
| 13 | AX₁ | Y₁ 为另一圆交点 |
| 14 | BY₁ | Z₁ 为另一圆交点 |
| 15 | Z₁X₁ | 两个完整三角形齐备 |

## 省去两笔的原因

记另一圆交点映射为 I_P，复合映射为 f=I_C I_B I_A。
由于 A、B 同时位于 UV 上，两个投影对合都交换 U、V，因此

```math
I_A(U)=I_B(U)=V,\qquad I_A(V)=I_B(V)=U.
```

于是 `f(U)=I_C(U)=W`，`f(V)=I_C(V)=T`，前三笔就取得两组对应点。
再从 U 逆向执行复合映射，利用已有 W=I_C(U)，第 4–5 笔得到
`R=I_B(W)`、`P=I_A(R)`。因此 f(P)=U，已有三组对应点

```math
f(U)=W,\qquad f(V)=T,\qquad f(P)=U.
```

五笔取得三组对应点，比圆心弦前缀少两笔。
由圆上射影对应的交叉弦性质，两个点

```math
J=UT\cap VW,\qquad H=VU\cap TP
```

同在不动点轴上。VU 是首笔 AB，后三条辅助直线与 JH 共需四笔。
因此第 9 E 得到轴，第 10–12 E 恢复一个完整解，额外三笔恢复另一个完整解。

## 一般参数与独立精确核验

令单位圆上的有理参数点为

```math
Q(t)=\left(\frac{1-t^2}{1+t^2},\frac{2t}{1+t^2}\right).
```

采用 U=Q(u)、V=Q(v)，以及
`A=(1−a)U+aV`、`B=(1−b)U+bV`、`C=(cx,cy)`。
六个独立参数覆盖严格割线输入的一般位置；圆周参数缺失的单点可通过旋转坐标避开。
坐标选择仅用于证明，程序的首笔仍为 AB。

独立 Sage 脚本在六参数多项式环中验证两个对合均交换 U、V，三组对应点成立，
J、H 落在复合矩阵给出的轴上，且 JH 非恒零并与该轴成比例。
非恒零条件及正常夹具给出上述一般位置适用范围。

另使用现有独立验证器重放四个夹具的五种程序，共 20 份证书，
核对交点闭包、逐笔计分、重复绘制和目标首次出现时刻，四个错误对照全部被拒绝。

- [构造脚本](../experiments/replay_secant_seed.py)
- [构造证书](../experiments/results/secant-seed.json)
- [独立核验与一般参数脚本](../experiments/verify_secant_seed_sage.py)
- [独立验证报告](../experiments/results/secant-seed-verification.json)

## 二解域中的覆盖缺口

单位圆、O=(0,0)，取 `A=(10,2)`、`B=(11,3)`、`C=(12,2)`。
精确分类得到 `K=1953193`、`e=0`，因此恰有两个非退化解。
但 AB、BC、CA 到 O 的距离都大于 1，三条输入点连线均不与圆相交。
严格不交条件在该输入的一个开邻域内成立。

这给出 D₂ 中具有内部的未覆盖区域。12/15 E 的结论限定在上述割线子域，
整个 D₂ 的一般位置上界为原圆心弦程序的 14/17 E。两条路线的全局最小性均待研究。

## 复现

标准库重放与数据生成在仓库根目录运行。

```sh
python3 experiments/replay_secant_seed.py
python3 experiments/replay_secant_seed.py --output experiments/results/secant-seed.json
python3 -m unittest discover -v
```

第二条命令更新受限构造证书。独立核验使用同一固定 SageMath 10.7 镜像。

```sh
docker run --rm --network none \
  -v "$PWD:/workspace:ro" -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify_secant_seed_sage.py
```

命令打印验证报告。需更新已提交报告时，重定向至
`experiments/results/secant-seed-verification.json`。
