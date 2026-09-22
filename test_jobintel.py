from jobintel import match_job


def test_exact_domain_evidence_scores_strongly() -> None:
    result = match_job(["Python automation"], ["Python automation for engineering reports"])
    assert result.strong == 1 and result.score == 100


def test_missing_evidence_is_a_gap() -> None:
    result = match_job(["Kubernetes operations"], ["CAD design for robot gripper"])
    assert result.gaps == 1 and result.matches[0].evidence is None

