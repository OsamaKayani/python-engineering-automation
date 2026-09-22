from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

STOPWORDS = {"and", "der", "die", "das", "for", "mit", "the", "und", "von"}


@dataclass(frozen=True)
class Module:
    name: str
    ects: float
    outcomes: str
    assessment: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.outcomes.strip():
            raise ValueError("module name and outcomes are required")
        if self.ects <= 0:
            raise ValueError("ECTS must be positive")
        if self.assessment not in {"exam", "project", "lab", "oral", "mixed"}:
            raise ValueError(f"unsupported assessment: {self.assessment}")


@dataclass(frozen=True)
class RecognitionCandidate:
    source: Module
    target: Module
    outcome_overlap: float
    ects_ratio: float
    assessment_compatible: bool

    @property
    def score(self) -> int:
        weighted = (
            0.65 * self.outcome_overlap
            + 0.25 * min(1.0, self.ects_ratio)
            + 0.10 * self.assessment_compatible
        )
        return round(100 * weighted)

    @property
    def review_reason(self) -> str:
        if not self.assessment_compatible:
            return "assessment mismatch requires manual review"
        if self.ects_ratio < 0.8:
            return "source module has substantially fewer ECTS"
        if self.outcome_overlap < 0.5:
            return "learning-outcome overlap is weak"
        return "candidate for detailed syllabus review"


def tokens(text: str) -> set[str]:
    words = re.findall(r"[A-Za-zÄÖÜäöüß]{3,}", text)
    return {word.lower() for word in words if word.lower() not in STOPWORDS}


def compare(source: Module, target: Module) -> RecognitionCandidate:
    left, right = tokens(source.outcomes), tokens(target.outcomes)
    overlap = len(left & right) / len(right) if right else 0.0
    compatible = source.assessment == target.assessment or target.assessment == "mixed"
    return RecognitionCandidate(
        source=source,
        target=target,
        outcome_overlap=overlap,
        ects_ratio=source.ects / target.ects,
        assessment_compatible=compatible,
    )


def rank_candidates(sources: Iterable[Module], target: Module) -> list[RecognitionCandidate]:
    return sorted(
        (compare(source, target) for source in sources),
        key=lambda item: item.score,
        reverse=True,
    )


def _module(data: dict[str, object]) -> Module:
    return Module(
        name=str(data["name"]),
        ects=float(data["ects"]),
        outcomes=str(data["outcomes"]),
        assessment=str(data["assessment"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank module-recognition candidates")
    parser.add_argument("input", type=Path, help="JSON with target and source modules")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    target = _module(data["target"])
    sources = [_module(item) for item in data["sources"]]
    for candidate in rank_candidates(sources, target):
        print(f"{candidate.score:3d}  {candidate.source.name}: {candidate.review_reason}")


if __name__ == "__main__":
    main()
