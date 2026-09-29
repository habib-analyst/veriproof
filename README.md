# VeriProof

**Tamper-evident forensic verification for everyday evidence media** — detects and localizes tampering in chat/payment screenshots and voice notes, and emits a signed Forensic Evidence Report (FER) instead of a bare probability.

> Working names: VeriProof (system) · EviForge-DB (dataset) · SpecTrace (detector) · FER (report format). See [PROJECT.md](PROJECT.md) for the full charter and novelty claims.

## Status

M0–M1 in progress: package foundation, FER schema, eval harness, CLI, and the EviForge-DB screenshot generation pipeline (render → tamper → launder → dataset).

## Install (dev)

```bash
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"    # Windows; use .venv/bin/ on POSIX
.venv/Scripts/pip install -e ".[data]"   # optional: HF datasets export
```

## Quickstart

```bash
.venv/Scripts/veriproof --version
.venv/Scripts/python data_build.py --out data/processed/eviforge-db-v1 --n-real 200 --n-tampered 200 --seed 20260929
.venv/Scripts/pytest tests/ -v
```

## Layout

```
src/veriproof/
├── data/        # EviForge-DB: render (UI templates) → tamper (ops + masks) → launder → dataset
├── models/      # SpecTrace detector (M2)
├── reports/     # FER schema v0.1 + Ed25519 signing/verification
├── eval/        # protocol, detection/localization metrics, runner
├── api/         # FastAPI REST (M4)
└── cli.py       # veriproof CLI
```

## License

MIT
