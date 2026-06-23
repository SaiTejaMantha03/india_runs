import argparse
import csv
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.scorer import score_candidate
from src.reasoning import generate_reasoning

TOP_N = 100
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs"
DEFAULT_OUTPUT_FILE = DEFAULT_OUTPUT_DIR / "submission.csv"


def find_default_candidates_path() -> Path:
    plain = REPO_ROOT / "candidates.jsonl"
    gzipped = REPO_ROOT / "candidates.jsonl.gz"
    if plain.exists():
        return plain
    if gzipped.exists():
        return gzipped
    raise FileNotFoundError(
        f"Could not find candidates.jsonl or candidates.jsonl.gz in {REPO_ROOT}.\n"
        f"Copy your candidates.jsonl into the repo root, or run with:\n"
        f"  python3 rank.py --candidates /path/to/candidates.jsonl"
    )


def load_candidates(path: str):
    p = Path(path)
    opener = gzip.open if p.suffix == ".gz" else open
    candidates = []
    with opener(p, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            candidates.append(json.loads(line))
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Rank candidates for the Redrob hackathon JD.")
    parser.add_argument(
        "--candidates", default=None,
        help="Path to candidates.jsonl (or .jsonl.gz). "
             "Defaults to candidates.jsonl/.gz in the repo root if not given."
    )
    parser.add_argument(
        "--out", default=None,
        help="Output path for the ranked submission CSV. "
             "Defaults to outputs/submission.csv in the repo root if not given."
    )
    args = parser.parse_args()

    candidates_path = Path(args.candidates) if args.candidates else find_default_candidates_path()
    out_path = Path(args.out) if args.out else DEFAULT_OUTPUT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Candidate Profile Ranker", file=sys.stderr)

    print(f"Loading candidates : {candidates_path}", file=sys.stderr)
    candidates = load_candidates(candidates_path)
    print(f"  {len(candidates)} candidates loaded.", file=sys.stderr)

    candidates_by_id = {c["candidate_id"]: c for c in candidates}

    print("Scoring candidates ", file=sys.stderr)
    results = [score_candidate(c) for c in candidates]
    print(f"  {len(results)} candidates scored.", file=sys.stderr)

    print(f"Ranking and selecting top {TOP_N}...", file=sys.stderr)
    results.sort(key=lambda r: (-r["final_score"], r["candidate_id"]))
    top = results[:TOP_N]

    print("Generating reasoning and writing CSV...", file=sys.stderr)
    rows = []
    for rank, r in enumerate(top, start=1):
        candidate = candidates_by_id[r["candidate_id"]]
        reasoning = generate_reasoning(candidate, r, rank)
        rows.append({
            "candidate_id": r["candidate_id"],
            "rank": rank,
            "score": r["final_score"],
            "reasoning": reasoning,
        })

    for i in range(len(rows) - 1):
        assert rows[i]["score"] >= rows[i + 1]["score"], (
            f"Score ordering violated at rank {i+1}->{i+2}: "
            f"{rows[i]['score']} < {rows[i+1]['score']}"
        )

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. {len(rows)} rows written to: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(f"\nERROR: {e}\n", file=sys.stderr)
        sys.exit(1)