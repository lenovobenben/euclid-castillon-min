"""Replay the baseline exactly; all reported scores are upper bounds."""

import argparse
import hashlib
import json
from pathlib import Path

from castillon import FIXTURES, baseline, finish, encode

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles/castillon-d2-e-generic-v1.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    reports = []
    for name, points in FIXTURES.items():
        scores = {}
        programs = {}
        for target, all_solutions, edges in [
            ("axis", False, False),
            ("one_vertices", False, False),
            ("one_edges", False, True),
            ("all_vertices", True, False),
            ("all_edges", True, True),
        ]:
            r = baseline(*points)
            if target != "axis":
                finish(r, all_solutions, edges)
            scores[target] = r.score
            programs[target] = r.program
        reports.append(
            {
                "fixture": name,
                "input": encode(points),
                "valid": True,
                "scores": scores,
                "programs": programs,
            }
        )
    profile = json.loads(PROFILE.read_text())
    result = {
        "profile_id": profile["id"],
        "profile_sha256": hashlib.sha256(PROFILE.read_bytes()).hexdigest(),
        "metric": profile["metric"],
        "claim": "exact fixture replays; no minimality claim",
        "reports": reports,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n")
    print(json.dumps({"fixtures": len(reports), "scores": reports[0]["scores"]}, indent=2))


if __name__ == "__main__":
    main()
