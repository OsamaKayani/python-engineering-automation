# JobIntel AI + Engineering Automation

An explainable Python tool that maps job requirements to verified project evidence, flags honest gaps, and generates an interview brief. The runtime is dependency-free and deterministic, so every score and threshold can be inspected.

```bash
python -m pip install -e ".[dev]"
jobintel sample_job.json --output job-fit.md
pytest -q
```

## Design decisions

- token-vector similarity keeps the first version reproducible and debuggable;
- strict JSON keys catch stale or malformed input instead of silently ignoring it;
- each requirement receives one best evidence item and an explicit status;
- a missing match remains a gap rather than being filled by generated language;
- Markdown output is easy to inspect, diff, and use as an interview brief.

`anerkannt_ai.py` is a second, early prototype in this repository. It compares source and target university modules using learning-outcome overlap, ECTS coverage, and assessment compatibility. It is a triage aid, not an official recognition decision.

Sample inputs contain only public role wording and personal experience summaries—no employer source code or confidential data.
