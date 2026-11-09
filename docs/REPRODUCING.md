# 复现与报告再生成

## 1. 环境与快速检查

从项目根目录运行。六项标准库检查仅需 Python 3.10+：

```sh
python3 -m unittest discover -v
```

精确独立核验使用 SageMath 10.7，固定镜像为 `sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528`。
先取得该镜像；已有镜像后，以下命令断网运行、只读挂载项目并自动删除临时容器。

## 2. 独立重放与一般恒等式

```sh
docker run --rm --network none \
  -v "$PWD:/workspace:ro" -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify_sage.py
```

打印 JSON，核验五参数恒等式、20 个程序的交点闭包与计费、4 个错误对照。
它不导入标准库几何内核，不自动更新已提交的报告。

## 3. 解数分类

```sh
docker run --rm --network none \
  -v "$PWD:/workspace:ro" -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/classify_sage.py
```

打印六参数恒等式、21 个分类例子及 4 个基线输入域检查；所有检查精确执行。
记录的全部一般判定见 [CLASSIFICATION](CLASSIFICATION.md)。

## 4. 再生成构造与报告

以下命令会覆盖项目生成数据；输入文件和来源文档不会改变：

```sh
python3 experiments/replay_baseline.py --output experiments/results/baseline.json
```

要更新两份独立核验报告，在第 2、3 节的命令末尾分别追加
`> experiments/results/sage-verification.json` 和 `> experiments/results/classification-verification.json`。
重放分别报告 axis / one_vertices / one_edges / all_vertices / all_edges 为 11 / 13 / 14 / 15 / 17 E，
新增圆与重复绘制均为零。不同目标使用不同裁剪程序。

## 5. 有界搜索

```sh
python3 experiments/search_prefix_suffix.py
python3 experiments/search_one_move_finish.py
python3 experiments/search_chord_trees.py
```

这些命令更新 experiments/results 中相应报告，不属于重复证明最小性。
范围、已知阳性对照与未覆盖集合见 [SEARCH](SEARCH.md)。

## 6. Windows 与本地 Sage

Windows PowerShell 7 可以将 Docker 多行命令写成单行，使用 `${PWD}:/workspace:ro` 挂载；
Docker 参数、固定镜像和容器内脚本保持不变。安装本地 Sage 10.7 时也可直接运行
`sage -python experiments/verify_sage.py` 与 `sage -python experiments/classify_sage.py`。

验证器使用断言进行精确检查，不支持 python -O。数值可视化或浮点筛查不能替代核验。
