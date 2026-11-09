# 回归检查与搜索阳性校准

运行 `python3 -m unittest discover -v`，仅需 Python 3.10+ 标准库。

- [test_exact_geometry.py](test_exact_geometry.py)：精确二次域符号、倒数、圆交点个数、投影对合、切线重根与非法定义点。
- [test_search_calibration.py](test_search_calibration.py)：已知十笔前缀后的 JH 阳性命中，防止筛查器空转。

共六项检查。一般参数正确性由证明和 Sage 恒等式负责，测试不代替全域覆盖或最小性证明。
独立 Sage 重放与错误证书对照见 [REPRODUCING](../docs/REPRODUCING.md)。
