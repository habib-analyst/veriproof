# VeriProof

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://github.com/habib-analyst/veriproof)
[![GitHub stars](https://img.shields.io/github/stars/habib-analyst/veriproof.svg)](https://github.com/habib-analyst/veriproof)

Tamper-evident forensic verification for everyday media — chat screenshots, payment proofs, and voice notes. Finds the tampered parts, scores its own confidence, and returns a signed report you can defend in a court, a bank dispute, or a newsroom.

## Quickstart

```bash
git clone https://github.com/habib-analyst/veriproof.git
cd veriproof
python -m venv .venv
.venv/bin/pip install -e ".[dev]"    # .venv\Scripts\ on Windows

.venv/bin/veriproof --version
.venv/bin/python scripts/build_dataset.py --out data/processed/eviforge-db-v1 --n-real 200 --n-tampered 200 --seed 20260929
.venv/bin/pytest tests/ -v
```

Python 3.11+.

## How it works

Three parts, one pipeline:

1. **EviForge-DB** — the first open benchmark for forged messenger screenshots: synthetic messenger/payment UI rendering, four tamper operations with pixel masks, six laundering operations (recompression, resizing, screenshots-of-screenshots), and Hugging Face dataset export.
2. **SpecTrace** — a laundering-robust detector trained on that benchmark (in progress).
3. **FER (Forensic Evidence Report)** — a standardized evidence report format (schema v0.1 + Ed25519 signing) with calibrated confidence and evidence pointers.

Runs offline as a CLI, a Python library, or a REST API. No telemetry — your media never leaves the machine.

## Status and honest limitations

This project is early. M0 (package, CI, FER schema + signing, eval harness, CLI) and M1 (EviForge-DB pipeline) are done; the detector (M2) and voice-note branch (M3) are next. The dataset is synthetic, and the report's trust model (who signs, who to trust) is not solved. The detector does not exist yet — what's here is the benchmark, the format, and the infrastructure it will plug into.

## Layout

```
src/veriproof/
├── data/       # EviForge-DB: render (UI templates) → tamper (ops + masks) → launder → dataset
├── models/     # SpecTrace detector (M2)
├── reports/    # FER schema v0.1 + Ed25519 signing/verification
├── eval/       # protocol, detection + localization metrics, runner
├── api/        # REST API (M4)
└── cli.py      # veriproof command line
scripts/        # dataset build entry point
docs/           # design spec, implementation plan, research reports
```

## License

MIT © 2026 Habib Ur Rehman

---
Built by [Habib Ur Rehman](https://github.com/habib-analyst) · ML/AI Engineer & healthcare-AI researcher ·
[LinkedIn](https://www.linkedin.com/in/hur-dev) · [habib.top](https://habib.top)
