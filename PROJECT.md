# VeriProof — Project Charter

**Proof for the media you actually forward.** VeriProof detects and localizes tampering in chat screenshots, payment proofs, and voice notes, and returns a signed Forensic Evidence Report (FER) instead of a bare probability.

Working names: VeriProof (system), EviForge-DB (dataset), SpecTrace (detector), FER (report format).

## 1. The problem

Generative AI has industrialized the forgery of everyday evidence.

- A cloned-voice WhatsApp note cost a Hong Kong man $1.27M (2026). The FBI counts ~$900M a year in US losses to AI-powered scams.
- Fabricated AI chat texts caused a wrongful detention in Florida. The court's report: "No one verified the evidence."
- AIForge-Doc (2026) shows the best document detector collapsing to near random (AUC 0.563) on generative edits of financial records.
- No benchmark, dataset, or detector exists for chat and messaging screenshots or voice notes. Verified against papers, patents, and products (see research reports in docs/research/).
- 77% of fraud teams see rising deepfake fraud. 7% are prepared (SAS/ACFE 2026). Vendors sell cloud APIs that return a yes/no and stop there. No evidence output, no on-premise option, no explainability.

## 2. Why now

- EU AI Act transparency rules for synthetic media are enforceable since August 2026. Enterprises need independent verification, not just metadata.
- UK Government (DSIT) 2026 assessment: in-the-wild tools fail and no standardized evidence output exists for courts, banks, or platforms.
- US courts are actively seeking authentication mechanisms. Rule 901 reform proposals exist because the tools do not work.
- Prior art is mapped. Every individual technique is claimed by someone. The system that combines them is not (section 4).

## 3. Novelty

| # | What we add | Closest prior art (verified) | Why it is open |
|---|---|---|---|
| 1 | EviForge-DB screenshots: first open dataset and benchmark for tampered messenger and payment screenshots, with pixel masks, generator labels, and laundering chains | FSTS (Nov 2025) covers synthetic text images including chat records, but template-generated, not real messenger UI. TextFake (May 2026) is AI-generation detection, not tamper localization (no method above 80%). DocTamper covers documents. TruFor/PSCC/CAT-Net are trained on photos and degrade on screenshots. | First real-UI screenshot tamper benchmark. UI semantics (ticks, timestamps, status bar, encryption notices) as a detection signal is unused by everyone. |
| 2 | EviForge-DB voice notes: first public benchmark for 1-30 s WhatsApp/Telegram voice notes under Opus/AMR-WB codec degradation | VoxENES 2026 uses MP3/AAC (top detector 28.98% EER). VoiceWukong (USENIX 25) is telephony. UncovAI and others sell closed voice-note tools. | First open, codec-realistic short voice-note benchmark. Codec-aware training for 1-3 s clips, where EER is highest and least studied. |
| 3 | SpecTrace: laundering-robust tamper localization with calibrated confidence | Recompression-based methods exploit recompression artifacts to find fakes. Spectral detection (F3Net/SPSL/frequency-ViT) is image-level and mature. Nobody trains localization to survive laundering (recompression, resize, screenshot-of-screenshot, transcoding). | Laundering robustness as a training goal, not an afterthought. |
| 4 | FER: standardized, tamper-evident evidence report for detector output | C2PA is a provenance manifest, not detector output. ProofMode signs captures without a report schema. NIST is only beginning to evaluate detector outputs for forensic use. | First report schema that courts and auditors can act on. |
| 5 | Offline open SDK (pip + CLI + REST) with evidence output | All current tools are closed cloud APIs (TrueDoc, Checkfile.ai, Fauxlens, UncovAI, Pindrop). | First self-hostable, GDPR-safe option with an evidence report. |

Honest statement: spectral analysis, tamper localization, and codec-robust detection are individually mature. We do not claim Fourier transforms. The open space is the system: benchmark + laundering-robust localization + evidence-report standard + offline SDK for everyday evidence media. TD Bank's defensive publication blocks patenting payment-screenshot verification as a concept. The protectable pieces are the FER schema, laundering-robust training, and dataset specifics.

## 4. Who uses it and how

- A person gets a suspicious voice note or payment screenshot. They run it through the tool and get a plain-language verdict with reasons. Today the advice is a secret codeword.
- A journalist verifies a leaked chat screenshot before publishing.
- A court authenticates evidence. The report shows which message bubbles were edited, with a signed hash for chain of custody.
- A bank verifies payment proofs in dispute resolution, on its own servers (GDPR, EU AI Act).
- A marketplace verifies seller payment screenshots. An insurer verifies claim receipts. HR verifies documents.
- A researcher uses EviForge-DB as the benchmark and submits models to the leaderboard.

## 5. Technical approach

1. Normalize input (metadata strip, format handling).
2. SpecTrace: spectral and RGB streams, cross-scale analysis of edit boundaries, laundering-robust training curriculum, calibrated confidence (temperature scaling or packed ensembles).
3. FER: deterministic, signed report. Tamper heatmap, per-region evidence, confidence, content hash, tool version, schema version.
4. SDK: pip + CLI + REST. Offline-first, no telemetry, deterministic inference.
5. Evaluation as code: pytest harness, protocol fixed before model work, per-laundering-condition breakdowns, CI on GitHub Actions.

## 6. Milestones

| Milestone | Deliverable | Status |
|---|---|---|
| M0 | Repo scaffold, CI, eval harness, FER schema v0.1, CLI | done |
| M1 | EviForge-DB v1: screenshot renderer, 4 tamper ops with masks, 6 laundering ops, HF export | done |
| M1.5 | Generative-edit lane (diffusion inpainting) + UI-semantic metadata per sample | next |
| M2 | SpecTrace image detector + baseline reimplementation + laundering benchmark | |
| M3 | Voice-note branch + codec benchmark | |
| M4 | FER pipeline + signing + CLI verify + REST + key registry design | |
| M5 | Leaderboard + submission guide + papers | |

## 7. Stack

Python 3.11+, PyTorch (M2), Pillow, NumPy, Pydantic v2, cryptography, Hugging Face datasets (export only), FastAPI (M4), pytest, ruff, GitHub Actions, Docker (M4).

## 8. Keywords

deepfake detection, deepfake forensics, audio deepfake, synthetic voice detection, voice cloning detection, harm AI, synthetic media detection, AI-generated content detection, generative AI fraud, media authenticity, evidence authentication, AI forensics, tamper localization, image forgery detection, media forensics, evidence integrity, chain of custody, tamper-evident reporting, forensic evidence report, calibrated uncertainty, laundering robustness, compression-robust forensics, Fourier-domain analysis, spectral artifacts, cross-scale consistency, document forgery, screenshot forensics, voice-note verification, on-premise SDK, offline-first, GDPR-compliant, EU AI Act, benchmark, leaderboard, fraud prevention

Keyword rule: deepfake and synthetic media terms lead because that is the umbrella people search and the category this work lives in (voice notes are audio deepfakes, forged screenshots are AI-manipulated content). Domain terms follow so niche audiences find us too.

## 9. Risks

| Risk | Mitigation |
|---|---|
| Detector weak on laundering | Laundering curriculum is a training-time feature. The benchmark reports per-condition, honestly. |
| Sim2real gap (synthetic data) | Real-world seed set, platform-realistic rendering, cross-style generalization protocol, renderer-seed-isolated splits. |
| Scope creep | Milestones are binding. New scope means a new plan. |
| Prior-art collision | Monthly sweep of arXiv, patents, products. Section 11 log updated every time. |

## 10. Publication plan

1. Dataset and benchmark paper (EviForge-DB). NeurIPS D&B or a journal.
2. Method paper (SpecTrace + laundering robustness). CVPR/ICCV/TIFS.
3. System paper (FER standard + SDK). Forensics or security venue (IH&MMSec, IEEE TIFS).

## 11. Novelty tracking log

Every prior-art sweep gets a row. If evidence challenges a claim, the claim changes the same day.

| Date | Sweep | Finding | Action |
|---|---|---|---|
| 2026-09-29 | Wave 1: SOTA, datasets, threats, tooling, robustness, efficiency (36 sources) | Field fragmented. No unified AV benchmark. No evidence-report standard. Laundering-robust detector unbuilt. | Charter drafted. FER and benchmark framed as core novelty. |
| 2026-09-29 | Wave 2: enterprise demand, live defense, media integrity, patents (38 sources) | Chat/payment screenshot and voice-note forgery have no benchmark, dataset, or detector. Pindrop AV-sync patent is silent on provenance. EU AI Act live Aug 2026. | Direction locked: everyday evidence verification (VeriProof). |
| 2026-09-29 | Wave 3: targeted prior art (35 sources) | FSTS and TextFake are adjacent prior art. TD Bank defensive publication blocks the patent concept. UncovAI sells voice-note detection (closed). Recompression localization exists but exploits artifacts; we train to survive. NIST has no report standard. | Section 3 rewritten with 5 refined claims. Fourier-per-se novelty dropped. ForenDeX removed (unverifiable). |

Next sweeps: monthly. Targets: messenger-screenshot forgery datasets, voice-note benchmarks, laundering-robust localization, detector evidence-report standards.

## 12. Known flaws

Kept current. Fixed items marked.

**State, not flaws:** detector not built yet (M2). Voice-note branch not built (M3). Leaderboard not built (M5). No papers yet.

1. **Sim2real gap.** EviForge-DB v1 is fully synthetic PIL-rendered UI. Real screenshots differ (fonts, DPI, OS rendering, photos of screens). Risk: detector memorizes template style. Fix planned: real-world seed set, platform-realistic rendering, generalization protocol.
2. **Tamper ops are weak vs real forgers.** Copy-move, splice, redraw, mean-fill are pre-GenAI attacks. Real forgers use diffusion inpainting. Fix planned: generative-edit lane (M1.5).
3. **FER trust model incomplete.** v0.1 embeds the verifying key in the report, so anyone can sign a report about any file. Credibility needs a key registry. Design planned in M4.
4. **Calibration unproven.** Confidence numbers are placeholders until M2.
5. **Golden hashes.** Fixed 2026-09-29: hashes now pin raw pixels, not encoded bytes (zlib/libjpeg differences across platforms broke this).
6. **Empty-input and degenerate-region crashes.** Fixed 2026-09-29: metrics raise on empty input; regions are at least 1x1; splice validates donor size.
7. **No adversarial or robustness track yet.** Planned; must actually ship, not just promise.
8. **Determinism vs forensics tension.** FER excludes timestamps for determinism. Real chain of custody needs them. Fix: separate payload determinism from custody metadata (M4).
9. **First mover partly gone.** Closed competitors exist. Differentiation is open + offline + evidence report + benchmark.
10. **IP limited.** TD Bank publication blocks the concept patent. Protectable: FER schema, laundering-robust training, dataset specifics.
11. **Distribution gap.** pip/CLI serves developers, not the person receiving a WhatsApp voice note. A simple web or desktop front-end is needed (M4+).
12. **No deadline, broad scope.** Three papers planned, zero results. Milestone gates are the discipline.

## 13. References

- Research reports: docs/research/DEEP_RESEARCH_deepfake-detection-gaps-2026.md, docs/research/DEEP_RESEARCH_deepfake-enterprise-gaps-2026.md
- Design spec: docs/superpowers/specs/2026-09-29-veriproof-design.md
- Implementation plan: docs/superpowers/plans/2026-09-29-veriproof-m0-m1.md
- Key anchors: AIForge-Doc (arXiv 2602.20569), FSTS (arXiv 2511.12658), TextFake (arXiv 2606.01050), NCSC courts report, SAS/ACFE 2026, UK DSIT 2026, EU AI Act Art. 50, Pindrop WO2022082036A1, arXiv 2503.17577 (laundering), DocTamper, TD Bank defensive publication (TD Commons 7477).
