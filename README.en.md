# Euclid-Castillon-Min · Inscribed-Triangle Constructions

[简体中文](README.md) · **English**

**Given a circle, its center, and three points A, B, C, use an unmarked straightedge and compass to construct an inscribed triangle whose side lines pass through A, B, C, respectively.**

For two-solution inputs where line AB meets the circle at two distinct points, the general-case construction draws one triangle with 12 lines, or both with 15 lines.

This project studies the Cramer–Castillon problem and provides step-by-step animations, elementary traces,
general-parameter proofs, independent exact verification, solution classification, and bounded searches.
**Global minimality and full-domain robust bounds remain open.**

[Watch the 15 E two-solution animation](animations/castillon/media/CastillonBoth_15E_4k60.mp4) ·
[12 E single-solution animation](animations/castillon/media/CastillonOne_12E_4k60.mp4) ·
[Secant construction and proof](docs/SECANT.md) · [Exact verification](experiments/results/secant-seed-verification.json)

[![15 E construction on the proper-secant subdomain](animations/castillon/preview.png)](animations/castillon/media/CastillonBoth_15E_4k60.mp4)

*Click the preview to view or download the two-solution animation, 3840 × 2160, 60 fps, approximately 64 seconds. The single-solution video is approximately 55 seconds.*

## Explore the constructions

| Animation | Target | Scope | Video |
|---|---|---|---|
| One solution in 12 E | One complete triangle, using 12 lines | AB meets the circle at two distinct points, general case | [4K60 MP4](animations/castillon/media/CastillonOne_12E_4k60.mp4) |
| Both solutions in 15 E | Two complete triangles, using 15 lines | AB meets the circle at two distinct points, general case | [4K60 MP4](animations/castillon/media/CastillonBoth_15E_4k60.mp4) |

The videos use a dark blue background, Chinese captions, and thin lines. Magenta denotes free inputs,
gold the current move, pale blue auxiliary objects, and green the targets. Each draw highlights
its two existing reference points and shows the cumulative E count. The visual style follows
[Euclid-CCC-Min](https://github.com/lenovobenben/euclid-ccc-min).

Geometry is exported from exact replay and checked against the committed certificate. The videos use
the `inside` fixture, with all three given points inside the circle. The first move draws AB.
Forward and inverse projections produce the fixed-point axis at move 9. Each video starts from
the free inputs, sharing the first 12 moves. The videos complete one triangle at move 12 and
both triangles at move 15, respectively.

See the [animation guide](animations/castillon/README.md) for geometry export, viewport tests,
and rendering commands. Detailed mathematical documents are currently in Chinese.

## Current verified upper bounds

For inputs with two nondegenerate solutions, the table gives the moves needed to draw
complete triangles in the general case. AB means the full line through the given points A and B.

| Target | AB meets the circle at two distinct points (animated method) | No restriction on how AB meets the circle |
|---|---:|---:|
| One complete triangle | **12 E** | 14 E |
| Both complete triangles | **15 E** | 17 E |

The animated method starts from the two intersections of AB with the circle.
If AB is tangent to or misses the circle, use the other method.
Having all three given points inside the circle guarantees this intersection condition.
Starting with AB makes two projection involutions exchange the same pair of circle points.
Using forward and inverse projections, five moves yield three image pairs, and move 9 draws
the fixed-point axis. See the [secant construction](docs/SECANT.md) for elementary steps,
proofs, exact certificates, and the coverage gap.

The other method starts with line OA through the circle's center O and the given point A,
and draws the fixed-point axis at move 11. It works in the general case whether AB crosses,
is tangent to, or misses the circle. See its [construction and proof](docs/CONSTRUCTION.md).

Both methods draw only lines and use the given circle for intersections. These move counts
apply to the general case. Special cases such as parallel auxiliary lines or coincident
auxiliary points still need further work to cover every input with two nondegenerate solutions.

### Free inputs and the two-solution domain

Only Γ, its center O, and distinct noncollinear points A, B, C off Γ are free.
No circumference point, radius endpoint, coordinate axis, or line is free. Side extensions are allowed.
For radius R, area S of ABC, and point powers p_P=OP²−R², define

$$
K=4R^2S^2+p_Ap_Bp_C.
$$

Let e count tangent contact points from each given point lying on the line through the other two.
The two-nondegenerate-solution domain D₂ is exactly **K>0 and e=0**.
[CLASSIFICATION](docs/CLASSIFICATION.md) also covers zero, one, and infinitely many solutions.
Input solvability and applicability of a particular auxiliary construction are separate questions.

## What counts as an E move

| Operation | Cost |
|---|---:|
| Draw a complete line through two existing distinct points | 1 E |
| Draw a circle centered at an existing point through another existing point | 1 E |
| Obtain or name a determined finite real intersection | 0 E |
| Given circle, center, and three input points | 0 E |
| Execute the same draw again | Still 1 E |

Use an unmarked straightedge and a **collapsing compass**. Arbitrary auxiliary points,
points at infinity, and free distance transfer are forbidden. All finite real intersections
of each new object with existing distinct objects enter the point set automatically.
Composite operations must be expanded. Draws used for branch tests, failed attempts,
and duplicate draws count; referencing an existing object does not add E.

The elementary semantics follow Euclid-Min's fixed-version [metrics](https://github.com/lenovobenben/euclid-min/blob/792619b38d749643bc9d80da8110dc9cff5b4877/docs/METRICS.md) and
[formal model](https://github.com/lenovobenben/euclid-min/blob/792619b38d749643bc9d80da8110dc9cff5b4877/docs/FORMAL_MODEL.md). This project's inputs, targets, and coverage are defined in
[DESIGN](docs/DESIGN.md). Scores for different problems are not directly comparable.

## Sources and project contribution

The geometric route uses the classical fixed-point axis of a circle projectivity, described
in Maurice Starck's [*Castillon’s problem*](https://www.polyhedra-world.nc/stuff/Castillon.pdf), 2002.
This project supplies elementary programs starting from a proper secant or a center chord,
shared projection chains and chords, exact replays, general identities, input classification,
and bounded-search records.
It claims no historical priority for the method or counts. See [LITERATURE](docs/LITERATURE.md).

## Exact verification

| Check | Result or purpose | Record |
|---|---|---|
| Exact secant replay | Four fixtures, five programs, no duplicate draws | [Secant certificates](experiments/results/secant-seed.json) |
| Independent Sage verification of the secant route | Six-parameter identities, 20 programs with closure, recounts and first-hit checks, four invalid controls rejected | [Secant report](experiments/results/secant-seed-verification.json) |
| Independent Sage verification of the center-chord route | Five-parameter identities and 20 exact program replays | [Center-chord report](experiments/results/sage-verification.json) |
| Classification | Six-parameter identities, 21 exact examples, four baseline-domain checks | [Report](experiments/results/classification-verification.json) |

The constructor uses Fraction and a real quadratic field. The independent Sage verifier
imports none of that geometry code and recounts the score. Claimed coordinates may only
select independently computed intersections. Finite examples, general proofs, coverage,
and minimality are separate evidence. Exact decisions use no tolerance; python -O is unsupported.

## Reproduction

Python 3.10+ standard library runs the geometry, search, and animation-data regression checks:

```sh
python3 experiments/replay_secant_seed.py
python3 -m unittest discover -v
```

The secant replay reports a 9 E axis, with one complete triangle at 12 E and both at 15 E.
The standard-library environment runs twelve checks. The Manim environment runs three additional
checks for viewports, line clipping, and numerical-search calibration. Regenerate the animation
geometry with the following command.
The [animation guide](animations/castillon/README.md) includes 4K60 rendering instructions.

```sh
python3 animations/castillon/export_geometry.py
```

Independent SageMath 10.7 verification of the secant construction uses a pinned image,
no network, and a read-only mount.

```sh
docker run --rm --network none \
  -v "$PWD:/workspace:ro" -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify_secant_seed_sage.py
```

With the image cached, neither network access nor a persistent container is needed.
See [complete reproduction instructions](docs/REPRODUCING.md) for classification, center-chord
verification, certificate regeneration, bounded searches, and expected outputs.

## Current research directions

Investigate whether the secant route's 9 E axis can be shortened, extend its 12/15 E input
coverage, and explore mixed circles, direct target edges, shared two-solution programs,
and intermediate-degeneracy repairs. Screening 625 AB-seed chord prefixes and 98,653 mixed
states produced five numerical hits, all rejected by independent exact verification.
See [SEARCH](docs/SEARCH.md) for the finite search scope and uncovered candidates.
Research priorities and presentation conventions are in [ROADMAP](docs/ROADMAP.md).

## Documentation and code

| Content | Entry |
|---|---|
| Inputs, targets, and claim levels | [DESIGN](docs/DESIGN.md) |
| Animated secant construction, elementary steps, and proof | [SECANT](docs/SECANT.md) |
| Center-chord construction for generic inputs throughout D₂ | [CONSTRUCTION](docs/CONSTRUCTION.md) |
| Existence, counts, and degeneracy | [CLASSIFICATION](docs/CLASSIFICATION.md) |
| Full reproduction commands | [REPRODUCING](docs/REPRODUCING.md) |
| Bounded searches already performed | [SEARCH](docs/SEARCH.md) |
| Animations, geometry export, and rendering | [animations/castillon](animations/castillon/README.md) |
| Research roadmap and presentation conventions | [ROADMAP](docs/ROADMAP.md) |
| Sources and comparability | [LITERATURE](docs/LITERATURE.md) |
| Research scripts | [experiments](experiments/README.md) |
| Certificates and reports | [experiments/results](experiments/results/README.md) |
| Regression checks | [tests](tests/README.md) |
| Series conventions and four-project comparison | [SERIES](docs/SERIES.md) |

**Construction optimization series**:
[Euclid-Min](https://github.com/lenovobenben/euclid-min) ·
[Euclid-CCC-Min](https://github.com/lenovobenben/euclid-ccc-min) ·
[Euclid-Equal-Angle-Min](https://github.com/lenovobenben/euclid-equal-angle-min) ·
[Euclid-Castillon-Min](https://github.com/lenovobenben/euclid-castillon-min).


## License and citation

Code, tests, and configuration use [Apache 2.0](LICENSE). Mathematical documentation,
construction records, research data, and citation metadata use [CC BY 4.0](LICENSE-CONTENT).
Third-party rights are unchanged; see the [license scope](LICENSE-SCOPE.md).
Use [CITATION.cff](CITATION.cff), citing **lenovobenben, Euclid-Castillon-Min**, the
[repository](https://github.com/lenovobenben/euclid-castillon-min), and the commit or version used.
Indicate modifications when adapting non-software content.
