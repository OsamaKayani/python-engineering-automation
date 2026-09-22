import json

import pytest

from jobintel import load_job, markdown_report, match_job


def test_exact_domain_evidence_scores_strongly() -> None:
    result = match_job(["Python automation"], ["Python automation for engineering reports"])
    assert result.strong == 1 and result.score == 100


def test_missing_evidence_is_a_gap() -> None:
    result = match_job(["Kubernetes operations"], ["CAD design for robot gripper"])
    assert result.gaps == 1 and result.matches[0].evidence is None


def test_empty_inputs_are_safe() -> None:
    result = match_job([], [])
    assert result.score == 0
    assert result.matches == ()


def test_report_labels_score_as_evidence_organization() -> None:
    result = match_job(["Python automation"], ["Python automation"])
    report = markdown_report("Engineer", "Example", result)
    assert "not hiring predictions" in report
    assert "Strong" in report


def test_input_schema_rejects_unexpected_keys(tmp_path) -> None:
    path = tmp_path / "job.json"
    path.write_text(json.dumps({"role": "Engineer", "company": "Example"}))
    with pytest.raises(ValueError, match="missing"):
        load_job(path)
