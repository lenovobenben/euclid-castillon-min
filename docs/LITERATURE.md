# 来源、构造路线与计数可比性

## Cramer–Castillon 问题

- Maurice Starck，[*Castillon’s problem*](https://www.polyhedra-world.nc/stuff/Castillon.pdf)，2002。
  给出圆上对应、不动点轴、自极特殊构型和只用直线的构造讨论。
  本项目的几何主体沿用此类经典路线，不将其表述为新发现。
- Zian Shang、David Treeby，[*Solving the Cramer-Castillon problem using Pascal’s theorem*](https://doi.org/10.1017/mag.2025.3)，
  *The Mathematical Gazette* 109(574)，2025，10–16。
  提供利用帕斯卡定理的解法，是比较其他构造路线的参考。

这里只链接原始材料，不在仓库中重新发布第三方论文全文或图片。

## E 步规则

- [Euclid-Min 固定版 METRICS](https://github.com/lenovobenben/euclid-min/blob/792619b38d749643bc9d80da8110dc9cff5b4877/docs/METRICS.md)
- [Euclid-Min 固定版 FORMAL_MODEL](https://github.com/lenovobenben/euclid-min/blob/792619b38d749643bc9d80da8110dc9cff5b4877/docs/FORMAL_MODEL.md)
- [Euclid-CCC-Min DESIGN](https://github.com/lenovobenben/euclid-ccc-min/blob/main/docs/DESIGN.md)

本项目沿用每条合法直线/基础圆 1 E、交点 0 E、塌圆规、禁止任取点与实际重复绘制计费的规则。
正十七边形、三圆相切和本题具有不同免费输入与目标，不直接比较分数大小。
历史说明中的“作任意弦”“过三点作圆”等须先变成合法基础动作，才能计入本项目成绩。

## 本项目记录的贡献范围

- 固定 D₂、免费输入、四个独立目标及 `gen`/`rob` 边界。
- 使用确定性圆心弦，记录三条投影链的弦复用和 11 E 公共前缀。
- 展开 13/14/15/17 E 程序，提供固定夹具证书和独立精确重放。
- 显式推导 K、自极条件与退化数 e，给出完整解数表及可执行分类器。
- 保存有限搜索范围、成功对照和未覆盖范围。

尚未完成相关文献的步数优先权调查，也未证明全局最小。因此目前只称“已验证上界”，
不称“世界纪录”“首次”或“理论最少”。
