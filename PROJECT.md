# VeriProof — Everyday Evidence Verification

> **Tamper-evident, laundering-robust forensic verification for the media people actually forward: chat screenshots, payment proofs, and voice notes.**

---

## 1. One-liner

VeriProof is the first open-source, offline-first forensic verification system that detects, localizes, and proves tampering in everyday evidence media — forged chat screenshots, fake payment proofs, and synthetic voice notes — and emits a court-grade, tamper-evident **Forensic Evidence Report** instead of a bare probability.

---

## 2. The Problem

Generative AI has industrialized the forgery of everyday evidence:

- A cloned-voice WhatsApp note cost a Hong Kong man **$1.27M** (2026); the FBI counts **~$900M/year** in US losses to AI-powered scams.
- Fabricated AI chat texts caused a **wrongful detention** in Florida — the court's own report: *"No one verified the evidence."*
- AIForge-Doc (2026) shows the best document detector collapsing to **near-random (AUC 0.563)** on generative edits to financial records.
- **No benchmark, no dataset, and no detector exists for chat/messaging screenshots or voice notes** — the exact media used in daily-life fraud.
- Enterprises are unserved: **77%** of fraud teams see rising deepfake social engineering; only **7%** are prepared (SAS/ACFE 2026). Vendors sell cloud APIs that stop at a yes/no verdict — no evidence, no on-premise option, no explainability.

## 3. Why Now

- **EU AI Act** transparency obligations for synthetic media became enforceable **August 2026** — enterprises need verification of machine-readable provenance *and* independent detection.
- **UK Government (DSIT) 2026** assessment: in-the-wild tools fail and no standardized evidence output exists that courts, banks, or platforms can rely on.
- **Courts** are actively seeking authentication mechanisms (US Rule 901 reform proposals exist *because* tools don't work).
- The prior-art space is provably open: every individual technique is claimed (patents, CVPR/ACM papers), but **no system fuses them** into a laundering-robust, evidence-carrying, offline-deployable product.

---

## 4. Novelty — What We Invent (refined after prior-art sweep 2026-09-29)

| # | Invention | Closest prior art (verified) | Our unclaimed contribution |
|---|---|---|---|
| 1 | **EviForge-DB (screenshots)** — first open dataset + benchmark for tampered messenger/payment-app screenshots with pixel-level tamper masks and messenger-UI forensic semantics (timestamps, ticks/checkmarks, encryption notices, status bars) | FSTS (Nov 2025) covers synthetic "text images" incl. chat records but is template-generated, not real messenger UI; TextFake (May 2026) is AI-generation detection, not tamper localization (no method >80%); DocTamper is documents; TruFor/PSCC/CAT-Net are natural-photo trained and degrade on screenshots | First real-UI screenshot tamper-localization benchmark; UI-semantic forensics as a detection signal |
| 2 | **EviForge-DB (voice notes)** — first public benchmark for 1–30 s WhatsApp/Telegram voice notes under Opus/AMR-WB codec degradation | VoxENES 2026 uses MP3/AAC (top detector 28.98% EER); VoiceWukong (USENIX '25) is telephony channels; UncovAI etc. are closed commercial tools | First open, codec-realistic short voice-note benchmark; codec-aware augmentation for 1–3 s clips (least studied, highest EER) |
| 3 | **SpecTrace detector** — laundering-robust tamper localization for screenshots + voice notes, with calibrated confidence | Recompression-based methods (arXiv 2407.02942, DiffForensics) *exploit* recompression artifacts to localize; spectral detection (F3Net/SPSL/frequency-ViT) is image-level and mature; nobody trains localization to *survive* laundering (recompression, resize, screenshot-of-screenshot, transcoding) | Laundering-robustness as a training goal for localization; domain-targeted spectral analysis for UI + short audio; calibrated uncertainty |
| 4 | **Forensic Evidence Report (FER)** — standardized, tamper-evident detector output: localized heatmap, calibrated confidence, generator-likelihood, content hash, chain-of-custody; human-readable + signed machine-readable JSON | C2PA is a provenance manifest, not detector output; ProofMode signs captures without a report schema; NIST is only beginning to evaluate detector outputs for forensic use; DeepFake Forensics AI (arXiv 2605.29353) hashes to IPFS ad hoc | First standardized, non-expert-readable, tamper-evident evidence-report schema for synthetic-media detection |
| 5 | **Offline-first open SDK** (pip + CLI + REST) | All current tools are closed/cloud (TrueDoc, Checkfile.ai, Fauxlens, UncovAI, Pindrop) | First open-source, self-hostable, GDPR-safe evidence-verification layer |

**Honest novelty statement:** spectral/frequency analysis, tamper localization, and codec-robust detection are individually mature. What does not exist — verified against papers, patents (TD Bank defensive publication blocks the payment-screenshot *concept*; no messenger-screenshot or voice-note forensic patent found), and products — is the **system**: open benchmark + laundering-robust localization + calibrated evidence-report standard + offline SDK for everyday evidence media. Note: we do NOT claim novelty on Fourier transforms per se; SpecTrace uses them as one tool inside a laundering-robust, domain-targeted design.

---

## 5. Impact

### End users
- **Fraud victims & targets:** verify a voice note or payment screenshot in seconds — with an explanation, not a black-box score.
- **Marketplace sellers/buyers:** verify payment proofs before shipping goods.
- **Victims of fabricated chats:** receive a report showing *exactly which message bubbles were tampered* — evidence usable in court.
- **Journalists:** authenticate leaked chat screenshots before publishing.

### Companies & integrations
| Sector | Integration |
|---|---|
| Banks / fintech | Dispute resolution (payment-proof verification), fraud-triaging queues, on-prem deployment (GDPR) |
| Marketplaces (eBay, OLX, Facebook Marketplace) | Seller payment-proof & document verification at listing/report time |
| Insurance | Claim photo/receipt authenticity |
| HR platforms | Document and interview-media verification |
| Courts / legal | Evidence authentication, Rule-901-grade reports |
| Messaging & social platforms | EU AI Act transparency compliance, synthetic-media moderation |

---

## 6. Technical Approach

1. **Input normalization** — screenshot/audio ingestion → modality-specific preprocessing (JPEG/PNG grid analysis, waveform/spectrogram extraction).
2. **SpecTrace detector** — Fourier-domain cross-scale spectral analysis of edit-boundary inconsistencies; splice-seam and generative-artifact signatures; trained with a laundering-augmentation curriculum; calibrated confidence (temperature scaling / packed ensembles).
3. **FER generation** — deterministic, signed report: tamper heatmap, per-region evidence, confidence, content SHA-256, tool version, timestamp. Machine-readable JSON + human-readable PDF/Markdown.
4. **SDK surface** — Python package + CLI + FastAPI REST; offline-first, no telemetry; deterministic inference; batch and streaming modes.
5. **Evaluation-as-code** — pytest harness; benchmark protocol fixed *before* model development; per-laundering-condition breakdowns; CI on GitHub Actions.

## 7. Milestones

| Phase | Deliverable | Outcome |
|---|---|---|
| M0 | Repo scaffold, protocol spec, CI, eval harness | Foundation |
| M1 | EviForge-DB v1: forged chat + payment screenshots (generators + laundering) | First-of-kind dataset → dataset paper |
| M2 | SpecTrace image detector: localization + calibration, laundering-robust | SOTA-on-new-benchmark results |
| M3 | Voice-note forgery dataset + audio branch | Milestone-2 modality |
| M4 | FER schema + signed reports + CLI/SDK packaging | Usable tool for end users |
| M5 | Leaderboard + publication + community submission pipeline | Adoption & citations |

## 8. Stack

Python · PyTorch · Hugging Face (datasets, hub) · FastAPI · pytest · GitHub Actions · Docker · (optionally) ONNX for edge export

## 9. Keywords

media forensics · tamper localization · synthetic media detection · AI-generated content detection · deepfake detection · evidence integrity · chain of custody · tamper-evident reporting · forensic evidence report · calibrated uncertainty · laundering robustness · compression-robust forensics · Fourier-domain analysis · spectral artifacts · cross-scale consistency · document forgery · screenshot forensics · voice-note verification · audio deepfake · on-premise SDK · offline-first · GDPR-compliant · EU AI Act · benchmark · leaderboard · fraud prevention · generative AI fraud

## 10. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Detector underperforms on laundering | Laundering curriculum from day one; benchmark designed to expose it; honest reporting |
| Dataset construction is costly | Synthetic-first generation pipeline (generative UI editors, TTS voice cloning), small real-world seed set |
| Prior art emerges mid-project | Monthly prior-art re-scan (patents + arXiv); novelty lives in the *system*, not one trick |
| Scope creep | Hard milestone gates; screenshots first, voice notes second |

## 11. Publication Plan

1. **Dataset & benchmark paper** (EviForge-DB) — NeurIPS D&B / journal.
2. **Method paper** (SpecTrace + laundering robustness) — CVPR/ICCV/TIFS.
3. **System paper** (FER standard + SDK) — security/forensics venue (e.g., IH&MMSec, IEEE TIFS).

## 12. References (evidence base)

- Full research reports: `D:\Projects by qoder\DEEP_RESEARCH_deepfake-detection-gaps-2026.md`, `D:\Projects by qoder\DEEP_RESEARCH_deepfake-enterprise-gaps-2026.md`
- Key anchors: AIForge-Doc (arXiv 2602.20569) · NCSC courts report · SAS/ACFE 2026 · UK DSIT 2026 · EU AI Act Art. 50 · Pindrop WO2022082036A1 · arXiv 2503.17577 (laundering) · DocTamper · ForenDeX · SAVe/EVAS/SAGA (claimed-territory map)

---

*Working names: VeriProof (system), EviForge-DB (dataset), SpecTrace (detector), FER (report format). All subject to change before first release.*

---

## 13. Novelty Tracking Log

> **Living log.** Updated on every prior-art sweep. Each entry: date, what was searched, what changed in our claims. Rule: never let a claim stay in this doc after evidence challenges it.

| Date | Sweep | Finding | Action taken |
|---|---|---|---|
| 2026-09-29 | Wave 1: SOTA/datasets/threats/tooling/robustness/efficiency (36 sources) | Field fragmented; no unified AV benchmark; no evidence-report standard; laundering-robust detector unbuilt | Charter drafted; FER + benchmark framed as core novelty |
| 2026-09-29 | Wave 2: enterprise demand + live defense + media integrity + patents (38 sources) | Chat/payment screenshot + voice-note forgery has no benchmark/dataset/detector; Pindrop AV-sync patent silent on provenance; EU AI Act live Aug 2026 | Direction locked: everyday-evidence verification (VeriProof) |
| 2026-09-29 | Wave 3: targeted prior art — screenshot forgery, voice-note forgery, spectral localization + report standards (35 sources) | FSTS (Nov 2025) & TextFake (May 2026) are adjacent — must position against; TD Bank defensive publication blocks patenting payment-screenshot concept; UncovAI sells voice-note detection (closed); recompression-localization exists but *exploits* artifacts (we train to *survive*); "ForenDeX" unverifiable — removed; NIST has no report standard | Section 4 rewritten: 5 refined claims; dropped Fourier-per-se novelty; added prior-art positioning |

**Next scheduled sweeps:** monthly re-scan of arXiv/patents/products for: messenger-screenshot forgery datasets, voice-note benchmarks, laundering-robust localization, detector evidence-report standards. Any claim collision → update Section 4 and this log same day.
