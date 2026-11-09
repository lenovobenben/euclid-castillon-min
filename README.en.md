# Euclid-Castillon-Min · Inscribed-Triangle Constructions

[简体中文](README.md) · **English**

**Draw one solution triangle using 14 lines; draw both solution triangles using 17 lines. No additional circles are needed.**

Given a circle, its center, and three points, this project studies E-move optimization for
the Cramer–Castillon problem: inscribe a triangle whose side lines respectively pass
through the given points. It provides elementary traces, general-parameter proofs,
independent exact verification, solution-count classification, and bounded searches.
**14 and 17 E are verified generic upper bounds, not proved global minima.
A full-domain robust upper bound has not yet been established.**

[Construction and proof](docs/CONSTRUCTION.md) · [Input classification](docs/CLASSIFICATION.md) ·
[Certificates](experiments/results/baseline.json) · [Sage verification](experiments/results/sage-verification.json)

Manim animations will be added later. Detailed research documents are currently in Chinese.

## Current verified upper bounds

| Target | Lines | New circles | Generic score |
|---|---:|---:|---:|
| Three vertices of either solution `one_vertices` | 13 | 0 | **13 E** |
| One complete triangle `one_edges` | 14 | 0 | **14 E** |
| All vertices of both solutions `all_vertices` | 15 | 0 | **15 E** |
| Both complete triangles `all_edges` | 17 | 0 | **17 E** |

The shared prefix draws the fixed-point axis at move 11, obtaining one starting vertex
of each solution. The free input circle remains available for intersections.
Each row is a separately trimmed program. The 15 E vertex score is not the first-hit time
of the 17 E complete-triangle program. No full-domain `rob` score is claimed.

Generic coverage is relatively open, dense, and full measure within the two-solution domain.
Exceptional auxiliary coincidences and parallel defining lines still require repairs.
See [DESIGN](docs/DESIGN.md) and [CONSTRUCTION](docs/CONSTRUCTION.md).

## Inputs and solution counts

Only Γ, its center O, and three distinct, noncollinear points A, B, C off Γ are free.
Points may lie inside or outside the circle, including at its center. No circumference point,
radius endpoint, axis, or line is free. Side extensions are allowed.

For radius R, triangle area S, and point powers p_P=OP²−R², set

```math
K=4R^2S^2+p_Ap_Bp_C.
```

Let e count tangent contact points from each given point lying on the line through the other two.
The two-nondegenerate-solution domain is exactly **K>0 and e=0**.
[CLASSIFICATION](docs/CLASSIFICATION.md) gives the full zero/one/two/infinite classification,
including self-polar configurations and degenerate closed candidates.

## E moves

| Operation | Cost |
|---|---:|
| Draw a line through two existing distinct points | 1 E |
| Draw a circle centered at an existing point through another existing point | 1 E |
| Obtain or name a determined finite real intersection | 0 E |
| Given circle, center, and three input points | 0 E |
| Execute a duplicate draw | Still 1 E |

The tools are an unmarked straightedge and a **collapsing compass**. Arbitrary points,
points at infinity, and direct distance transfer are forbidden. All finite real intersections
of a new object with prior distinct objects become available automatically.
Composite operations must be expanded into elementary draws.

The elementary semantics follow Euclid-Min's fixed-version
[metrics](https://github.com/lenovobenben/euclid-min/blob/792619b38d749643bc9d80da8110dc9cff5b4877/docs/METRICS.md)
and [formal model](https://github.com/lenovobenben/euclid-min/blob/792619b38d749643bc9d80da8110dc9cff5b4877/docs/FORMAL_MODEL.md),
as used in [Euclid-CCC-Min](https://github.com/lenovobenben/euclid-ccc-min).
Inputs and targets are specific to this [profile](profiles/castillon-d2-e-generic-v1.json).
Scores for different problems are not directly comparable.

## Exact verification

The standard-library constructor uses `Fraction` and a real quadratic field.
The independent Sage verifier imports none of that geometry implementation.
Claimed certificate coordinates may only select independently computed intersections.

| Check | Evidence |
|---|---|
| Exact replay | Four fixtures, five output programs, no duplicate draws: [certificates](experiments/results/baseline.json) |
| Independent Sage replay | 20 programs, automatic intersection closure, recounted scores and first-hit times; four corrupt controls rejected: [report](experiments/results/sage-verification.json) |
| General identities | Five independent parameters for the projection pairs and fixed-point axis: [script](experiments/verify_sage.py) |
| Classification | Six-coordinate identities, 21 exact examples, and four baseline-domain checks: [report](experiments/results/classification-verification.json) |

Finite examples, symbolic identities, bounded-search misses, and global lower bounds are
recorded separately. No floating-point tolerance is used. Python assertions must remain
enabled; optimized `python -O` verifier runs are rejected.

## Reproduce

Python 3.10+ standard library:

```sh
python3 experiments/replay_baseline.py --output experiments/results/baseline.json
python3 -m unittest discover -v
python3 experiments/search_prefix_suffix.py
python3 experiments/search_one_move_finish.py
python3 experiments/search_chord_trees.py
```

Independent SageMath 10.7 verification uses a pinned Docker image with no network and a read-only mount:

```sh
docker run --rm --network none \
  -v "$PWD:/workspace:ro" -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify_sage.py > experiments/results/sage-verification.json

docker run --rm --network none \
  -v "$PWD:/workspace:ro" -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/classify_sage.py > experiments/results/classification-verification.json
```

Obtain the image first if it is not cached. Verification itself needs no network access.

## Sources, research, and repository map

The route uses the classical fixed-point axis of a circle projectivity, as described in
Maurice Starck's [*Castillon’s problem*](https://www.polyhedra-world.nc/stuff/Castillon.pdf), 2002.
This project supplies a deterministic seed, chord sharing, elementary traces, exact replays,
general-parameter checks, and bounded searches. It claims neither historical priority for
the method or counts nor global minimality. See [LITERATURE](docs/LITERATURE.md).

The next target is a complete single triangle below 14 E. Planned work includes line-intersection
seeds, mixed line/circle prefixes, direct target hits, robust repairs, and future Manim animations.

| Content | Entry |
|---|---|
| Formal inputs, targets, metrics, and claim levels | [DESIGN](docs/DESIGN.md) |
| Elementary trace and proof | [CONSTRUCTION](docs/CONSTRUCTION.md) |
| Existence and number of solutions | [CLASSIFICATION](docs/CLASSIFICATION.md) |
| Bounded searches already performed | [SEARCH](docs/SEARCH.md) |
| Research priorities and animation plans | [ROADMAP](docs/ROADMAP.md) |
| Sources and score comparability | [LITERATURE](docs/LITERATURE.md) |
| Replays, verifiers, searches, and results | [experiments](experiments/) |

## License and citation

Code, tests, and configuration use [Apache 2.0](LICENSE). Mathematical documentation,
construction records, and research data use [CC BY 4.0](LICENSE-CONTENT).
Third-party rights are unchanged; see [license scope](LICENSE-SCOPE.md).
Cite **lenovobenben, Euclid-Castillon-Min**, the [repository](https://github.com/lenovobenben/euclid-castillon-min),
and the commit or version used. Attribute and indicate modifications when reusing non-software content.
