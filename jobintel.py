from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}")
STOP = {"and", "the", "with", "for", "from", "that", "this", "into", "are", "you", "our"}


def _tokens(text: str) -> list[str]:
    return [t.lower().strip(".-") for t in TOKEN.findall(text) if t.lower() not in STOP]


def _cosine(left: str, right: str) -> float:
    a, b = Counter(_tokens(left)), Counter(_tokens(right))
    if not a or not b:
        return 0.0
    dot = sum(value * b[word] for word, value in a.items())
    return dot / math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))


@dataclass(frozen=True)
class RequirementMatch:
    requirement: str
    evidence: str | None
    score: float
    status: str


@dataclass(frozen=True)
class MatchResult:
    score: int
    strong: int
    partial: int
    gaps: int
    matches: tuple[RequirementMatch, ...]


def match_job(requirements: list[str], evidence: list[str]) -> MatchResult:
    if any(not item.strip() for item in requirements):
        raise ValueError("requirements cannot contain blank items")
    if any(not item.strip() for item in evidence):
        raise ValueError("evidence cannot contain blank items")
    matches: list[RequirementMatch] = []
    for requirement in requirements:
        ranked = sorted(((_cosine(requirement, item), item) for item in evidence), reverse=True)
        similarity, best = ranked[0] if ranked else (0.0, None)
        status = "strong" if similarity >= 0.34 else "partial" if similarity >= 0.14 else "gap"
        matches.append(RequirementMatch(requirement, best if status != "gap" else None, similarity, status))
    points = {"strong": 1.0, "partial": 0.5, "gap": 0.0}
    score = round(100 * sum(points[m.status] for m in matches) / max(1, len(matches)))
    return MatchResult(score, sum(m.status == "strong" for m in matches), sum(m.status == "partial" for m in matches), sum(m.status == "gap" for m in matches), tuple(matches))


def markdown_report(role: str, company: str, result: MatchResult) -> str:
    rows = [f"# {role} — {company}", "", f"Fit score: **{result.score}%**", ""]
    for item in result.matches:
        rows.append(f"- **{item.status.title()}** — {item.requirement}\n  - {item.evidence or 'No verified evidence yet'}")
    rows += ["", "> Scores organize evidence; they are not hiring predictions."]
    return "\n".join(rows)


def load_job(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"role", "company", "requirements", "evidence"}
    if set(data) != required:
        missing = required - set(data)
        extra = set(data) - required
        raise ValueError(f"invalid input keys; missing={sorted(missing)}, extra={sorted(extra)}")
    if not isinstance(data["requirements"], list) or not isinstance(data["evidence"], list):
        raise TypeError("requirements and evidence must be lists")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Map verified experience to job requirements")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("job-fit.md"))
    args = parser.parse_args()
    data = load_job(args.input)
    result = match_job(data["requirements"], data["evidence"])
    args.output.write_text(markdown_report(data["role"], data["company"], result), encoding="utf-8")
    print(f"{result.score}% fit; report written to {args.output}")


if __name__ == "__main__":
    main()
