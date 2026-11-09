# 构造证书与验证报告

| 文件 | 内容 |
|---|---|
| [baseline.json](baseline.json) | 四个输入夹具、五种输出程序、规则 ID/哈希及精确交点依赖 |
| [sage-verification.json](sage-verification.json) | 一般恒等式、20 次独立重放和 4 个错误对照 |
| [classification-verification.json](classification-verification.json) | 完整解数分类的六参数关系、21 个例子和基线域检查 |
| [prefix-suffix.json](prefix-suffix.json) | 固定前缀筛查范围和候选 |
| [one-move-finish.json](one-move-finish.json) | 已选前缀后一笔线/圆的检查 |
| [chord-trees.json](chord-trees.json) | 9,878 个受限前缀的记录 |

再生成命令见 [REPRODUCING](../../docs/REPRODUCING.md)。验证报告、固定夹具与一般参数证明
分别作为不同证据，搜索零结果不声明全局下界。输入和覆盖约定见 [DESIGN](../../docs/DESIGN.md)。
