# VeriProof — Design Spec

> 2026-09-29 · Status: approved for implementation (autonomous mode) · Charter: `../PROJECT.md` (repo root)

## 1. Goals & Non-Goals

**Goals (M0–M5):**
1. EviForge-DB: first open dataset + benchmark for tampered messenger/payment-app screenshots (M1) and Opus/AMR-WB voice notes (M3), with pixel/segment masks, generator labels, laundering pipeline.
2. SpecTrace: laundering-robust tamper localization detector with calibrated confidence (M2 images, M3 audio).
3. FER: standardized, tamper-evident Forensic Evidence Report (signed machine-readable JSON + human-readable render) (M4).
4. Offline-first SDK: pip package + CLI + FastAPI REST, deterministic, no telemetry (M4).
5. Eval-as-code: pytest harness + GitHub Actions CI; protocol frozen before model work (M0/M1).

**Non-goals (v1):** video/AV content, real-time streaming inference, blockchain anchoring, mobile apps, multilingual UI (English first), patents.

## 2. Prior-Art Positioning (binding)

Position against in every paper/README: FSTS (synthetic text-image tampering incl. chat records), TextFake (AI-generated screenshot detection, no localization), DocTamper (documents), TruFor/PSCC/CAT-Net (natural photos), recompression-localization (2407.02942, DiffForensics — exploit artifacts; we train to survive), VoxENES/VoiceWukong (MP3-AAC / telephony; we do Opus/AMR-WB short voice notes), TD Bank defensive publication (payment-screenshot field cross-checks — we do pixel-level forensics + open benchmark), C2PA/ProofMode (provenance manifests; we standardize detector *output*). No claim of novelty on Fourier transforms per se.

## 3. Architecture

```
veriproof/
├── src/veriproof/
│   ├── data/            # EviForge-DB generation + laundering pipeline
│   │   ├── render/      # messenger/payment UI synthetic renderer (chat, bank app)
│   │   ├── tamper/      # tampering ops: copy-move, splice, inpainting, text-edit, generative edit
│   │   ├── launder/     # recompression, resize, screenshot-of-screenshot, codecs (Opus/AMR-WB)
│   │   └── dataset.py   # HF datasets builder: samples + masks + labels + provenance JSON
│   ├── models/
│   │   ├── spectrace/   # SpecTrace image branch: encoder + spectral stream + localization head + calibration
│   │   ├── audiotrace/  # SpecTrace audio branch: codec-aware frontend + detector + segment scores
│   │   └── registry.py  # model registry + checkpoints + ONNX export hook
│   ├── reports/
│   │   ├── schema.py    # FER JSON Schema (v0.1): verdict, confidence, heatmap ref, hashes, custody
│   │   ├── sign.py      # Ed25519 signing + verification
│   │   └── render.py    # human-readable Markdown/PDF render
│   ├── api/             # FastAPI REST: POST /verify (media in, FER out), GET /health
│   ├── cli.py           # veriproof verify <file> [--json|--report]
│   └── version.py
├── eval/                # protocol, metrics, laundering breakdowns, pytest golden tests
├── tests/               # unit + integration
├── .github/workflows/   # CI: lint, tests, eval smoke, benchmark tracking
└── docs/                # spec, plans, novelty log
```

## 4. Component Contracts

- **`data.render`** → produces synthetic real messenger/payment screenshots (templates: chat bubbles, ticks, timestamps, status bar, bank transfer card). Deterministic seed-driven.
- **`data.tamper`** → `(real_image, spec) -> (tampered_image, mask)` where spec = op type + region + params. Mask = pixel-level binary + per-region metadata.
- **`data.launder`** → applies laundering chains; each sample records its chain (e.g. `jpeg_q85 → resize_0.5 → png → screenshot_crop`).
- **`models.spectrace`** → `image -> (tamper_prob, localization_heatmap, calibration_params)`; trained with laundering curriculum; spectral stream = multi-scale DCT/FFT features fused with RGB encoder features.
- **`models.audiotrace`** → `(wav, codec_meta) -> (fake_prob, per-segment scores, calibration)`; codec-aware augmentation; supports 1–30 s inputs.
- **`reports`** → `(media_hash, model_outputs, custody_meta) -> FER_v0.1`; signed; verification function `verify_report(report) -> bool`.
- **`api`/`cli`** → thin wrappers; no business logic in transport.

## 5. Data Flow (verify path)

```
media file → preprocess (metadata strip, normalize) → SpecTrace/AudioTrace
  → {tamper_prob, heatmap, confidence} → FER builder → sign → JSON + Markdown/PDF
  → optional: report verification (signature + hash check)
```

## 6. Error Handling

- Deterministic output: same input + same model version → identical FER (pinned seeds, sorted dicts, no timestamps in hash inputs).
- Graceful degradation: unsupported format → `unsupported_media` error code with guidance; model load failure → explicit exit code, never silent fallback to weaker model without labeling it in FER.
- All FER fields versioned (`schema_version`, `model_version`) — reports remain interpretable across upgrades.
- No telemetry; all processing local.

## 7. Testing Strategy

- Unit: tamper ops produce valid masks (IoU checks); laundering chains idempotent; FER schema validation; signature round-trip.
- Golden: fixed seeds → pinned hashes for renderer/tamper outputs (regression protection).
- Protocol tests: eval harness runs a dummy model end-to-end before any real training.
- CI: lint + tests on push; eval smoke on schedule; benchmark JSON tracked in repo.

## 8. Milestones → Artifacts

| Milestone | Artifacts | Exit criteria |
|---|---|---|
| M0 | repo scaffold, config, CI, eval harness skeleton, FER schema v0.1, docs | `pytest` green; `veriproof --version` works; CI passes |
| M1 | EviForge-DB v1 (screenshots: ≥20k images, ≥6 tamper ops, laundering chains, masks, HF dataset card) | dataset builds reproducibly; stats report generated; dataset card published |
| M2 | SpecTrace image branch v1 + baseline reimplementation (TruFor/PSCC adapted) + laundering benchmark | localization F1/IoU beats adapted baselines on EviForge-DB, reported per laundering condition |
| M3 | Voice-note subset + AudioTrace v1 + codec benchmark | EER/segment scores reported per codec; beats codec-naive baseline |
| M4 | FER full pipeline + signing + CLI/SDK + REST + docs/demo | end-to-end verify on real WhatsApp screenshot sample; report verifies |
| M5 | leaderboard + community submission guide + publication drafts | leaderboard live; dataset + method papers drafted |

## 9. Risks

| Risk | Mitigation |
|---|---|
| Detector weak on laundering | laundering curriculum is a training-time feature, benchmark exposes it — honest reporting |
| Renderer realism gap vs real screenshots | real-world seed set + style randomization; eval split separated by renderer seed |
| Scope creep (video, apps) | non-goals list is binding; new scope = new spec |
| Prior-art collision | monthly novelty sweep → update PROJECT.md §4 + log (section 13) |

## 10. Decisions Deferred

GPU scheduling (Kaggle vs OpenToken), HF dataset repo naming, exact encoder backbone (tested at M2), ONNX export timing.
