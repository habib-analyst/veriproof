# VeriProof

**Proof for the media you actually forward.**

VeriProof checks whether everyday media has been faked or edited: chat screenshots, payment proofs, and voice notes. It finds the tampered parts, scores its own confidence, and returns a signed report you can defend in a court, a bank dispute, or a newsroom.

Built on the first open benchmark for forged messenger screenshots (EviForge-DB), a laundering-robust detector (SpecTrace), and a standardized Forensic Evidence Report format (FER).

## What it does

- **Detects** whether a screenshot or voice note is real, tampered, or AI-generated.
- **Localizes** the edited regions and marks them on the image.
- **Reports** a calibrated confidence with evidence, in a signed, tamper-evident format (FER).
- **Runs offline** as a CLI, a Python library, or a REST API. No telemetry. Your media never leaves the machine.

## The problem it solves

- A cloned-voice WhatsApp note cost a Hong Kong man $1.27M (2026). The FBI counts ~$900M a year in US losses to AI-powered scams.
- A US court jailed a woman over fabricated AI chat texts. The court's own review said: "No one verified the evidence."
- The best existing document detector scores near random (AUC 0.563) on AI-edited records. No dataset, benchmark, or detector exists for chat and payment screenshots. We verified this against papers, patents, and products before starting.
- 77% of fraud teams report rising deepfake fraud. 7% say they are prepared. (SAS/ACFE 2026)

## Who is this for

| Person | What they do with VeriProof |
|---|---|
| Someone who got a suspicious voice note or payment screenshot | Drops the file in, reads the verdict, keeps their money |
| Journalist | Checks a leaked chat screenshot before publishing |
| Lawyer or court | Gets an evidence report showing exactly what was edited, with a signed hash for chain of custody |
| Bank or fintech fraud team | Runs it on their own servers (GDPR-safe) to verify payment proofs in disputes |
| Marketplace or insurer | Verifies seller payment screenshots, receipts, and claim photos |
| Researcher | Uses EviForge-DB as the benchmark, submits models to the leaderboard |

## Status

M0 and M1 are done: package, CI, FER v0.1 (schema + Ed25519 signing), eval harness, CLI, and the EviForge-DB pipeline (synthetic messenger/payment UI, four tamper ops with pixel masks, six laundering ops, HF dataset export). The detector (M2) and voice-note branch (M3) are next.

## Install

```bash
git clone https://github.com/habib-analyst/veriproof.git
cd veriproof
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"    # Windows; .venv/bin/ on Linux/macOS
.venv/Scripts/pip install -e ".[data]"   # optional: Hugging Face dataset export
```

Python 3.11+.

## Quickstart

```bash
.venv/Scripts/veriproof --version
.venv/Scripts/python scripts/build_dataset.py --out data/processed/eviforge-db-v1 --n-real 200 --n-tampered 200 --seed 20260929
.venv/Scripts/pytest tests/ -v
```

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

## Roadmap

| Milestone | What ships |
|---|---|
| M0 done | Package, CI, FER schema, eval harness, CLI |
| M1 done | EviForge-DB v1: screenshots, tamper ops, laundering chains |
| M1.5 | Generative-edit lane (diffusion inpainting) + UI-semantic metadata in the dataset |
| M2 | SpecTrace detector with laundering-robust training + calibrated confidence |
| M3 | Voice-note branch + Opus/AMR-WB codec benchmark |
| M4 | Full FER pipeline, CLI verify, REST API, key registry design |
| M5 | Public leaderboard + community submission guide + papers |

## Honest limitations

This project is early. The dataset is synthetic; the detector does not exist yet; the report's trust model (who signs, who to trust) is not solved. Full list in [PROJECT.md](PROJECT.md), section 14, kept current.

## Research base

The project is grounded in two citation-backed research reports:

- [Gaps in deepfake / harm-AI detection](docs/research/DEEP_RESEARCH_deepfake-detection-gaps-2026.md) (36 sources)
- [Enterprise-urgent problems and prior art](docs/research/DEEP_RESEARCH_deepfake-enterprise-gaps-2026.md) (38 sources)

## License

[MIT](LICENSE) © 2026 Habib Ur Rehman
