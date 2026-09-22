# JobIntel AI + Engineering Automation

An explainable Python tool that maps job requirements to verified project evidence, flags honest gaps and generates an interview brief. The runtime is dependency-free and deterministic, so every score can be inspected.

```bash
python jobintel.py sample_job.json
python -m pip install -r requirements-dev.txt
pytest -q
```

The central product rule is simple: missing experience is reported as a gap rather than invented. Sample inputs contain only public role wording and personal experience summaries—no employer source code or confidential data.

