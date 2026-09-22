from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Module:
    name: str
    ects: float
    outcomes: str
    assessment: str


@dataclass(frozen=True)
class RecognitionCandidate:
    source: Module
    target: Module
    outcome_overlap: float
    ects_ratio: float
    assessment_compatible: bool

    @property
    def score(self):
        return round(100*(.65*self.outcome_overlap + .25*min(1,self.ects_ratio) + .10*self.assessment_compatible))


def tokens(text):
    return {word.lower() for word in re.findall(r"[A-Za-zÄÖÜäöüß]{3,}",text)}


def compare(source: Module, target: Module) -> RecognitionCandidate:
    left, right = tokens(source.outcomes), tokens(target.outcomes)
    overlap = len(left & right)/len(right) if right else 0
    compatible = source.assessment == target.assessment or target.assessment == "mixed"
    return RecognitionCandidate(source,target,overlap,source.ects/target.ects if target.ects else 0,compatible)


def rank_candidates(sources, target):
    return sorted((compare(source,target) for source in sources),key=lambda item:item.score,reverse=True)

