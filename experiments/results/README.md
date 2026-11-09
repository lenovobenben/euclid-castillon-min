# 构造证书与验证报告

| 文件 | 内容 |
|---|---|
| [baseline.json](baseline.json) | 四个输入夹具、五种输出程序、规则 ID/哈希及精确交点依赖 |
| [secant-seed.json](secant-seed.json) | AB 严格割圆子域的四个夹具、五种更短程序 |
| [secant-seed-verification.json](secant-seed-verification.json) | 六参数恒等式、20 份独立重放、错误对照和非割线二解输入 |
| [sage-verification.json](sage-verification.json) | 一般恒等式、20 次独立重放和 4 个错误对照 |
| [classification-verification.json](classification-verification.json) | 完整解数分类的六参数关系、21 个例子和基线域检查 |
| [prefix-suffix.json](prefix-suffix.json) | 固定前缀筛查范围和候选 |
| [one-move-finish.json](one-move-finish.json) | 已选前缀后一笔线/圆的检查 |
| [chord-trees.json](chord-trees.json) | 9,878 个受限前缀的记录 |
| [secant-chords.json](secant-chords.json) | AB 起步的 625 个前缀与直接命中数值筛查 |
| [secant-mixed.json](secant-mixed.json) | 五笔割线前缀后的 98,653 个混合状态筛查 |
| [secant-search-verification.json](secant-search-verification.json) | 五个数值初筛结果的独立精确拒绝及四个 9 E 阳性校准 |

再生成命令见 [REPRODUCING](../../docs/REPRODUCING.md)。验证报告、固定夹具与一般参数证明
分别作为不同证据，搜索零结果不声明全局下界。输入和覆盖约定见 [DESIGN](../../docs/DESIGN.md)。
