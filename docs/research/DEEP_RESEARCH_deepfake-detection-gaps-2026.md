# Deep Research: Gaps in Deepfake / Harm-AI Detection (2026)

> Generated 2026-09-29 | Depth: deep | Sources: 36 | For: project ideation in `D:\Projects by qoder`

## TL;DR

Every major subsystem of deepfake detection — evaluation, detection models, tooling, provenance, robustness, efficiency — has independently converged on the same failure mode: strong one-off results, no durable integrated infrastructure. The most evidence-backed white space is a **continuously updated audio-visual (AV) benchmark that jointly scores detection, temporal localization, and attribution under adversarial stress and real-world laundering**, paired with a **calibrated, offline, explainable detection toolkit** built on an efficient Fourier-based detector. No existing project occupies this intersection.

## Executive Summary

Across 36 sources (2021–2026, mostly 2025–2026), the literature tells one story: benchmark scores are a poor proxy for competence. The best cross-benchmark study shows per-dataset AUROC swings of 77.7–99.6% and full fine-tuning degrading to ~57% mean AUROC from dataset memorization [1]; the newest AV SOTA (X-AVDT) hits 99.69% AUROC on FakeAVCeleb but 89.55% on FaceForensics++ and takes ~1 minute per clip [2]. On LLM-era audio, the top detector achieves only 28.98% EER with half of systems at chance [12]. Practitioners are unserved: public tools score 79% vs 94% for human investigators, falsely flag up to 62% of genuine media, and get 0% on newer generators [28]. Detectors are miscalibrated [22], poisonable with invisible triggers [29], and their benchmarks omit adversarial, laundering, and aging tests [7][31]. Provenance (C2PA/SynthID) is trivially strippable [21][26] and subject to desynchronization attacks that require detector cross-checking nobody ships [23]. Efficiency research is real (25 ms on mobile [34]) but unconsolidated. The gaps converge on: **fragmented/static evaluation, no trustworthy outputs, no maintained offline tooling, unexplored AV robustness, and underserved threat classes (partial-spoof localization, social-media laundering, singing voice, live calls)**.

## 1. Status Quo [Confidence: High]

### 1.1 State of the art: generalization is the field's central problem

The most systematic evidence comes from Yermakov et al. [1], who re-evaluated GenD variants across 14 public benchmarks (FF++, DFDC, CDFv2/v3, FFIW, KoDF, DSv2, PGF, IDF, 2019–2025). Per-dataset AUROC ranges 77.7–99.6%; models trained on recent data collapse on older benchmarks; full fine-tuning degrades mean AUROC to ~57% via dataset-specific memorization. Their generalization recipe is deliberately minimal: freeze all but ~0.03% of parameters (LayerNorm), L2-normalize features onto a hypersphere, and train on paired real–fake sequences. The same work documents a measurement hazard: the FF++ validation set is a near-duplicate of its training set, making model selection on it invalid [1].

Methodologically the field has split into two camps. The first builds on frozen self-supervised AV backbones, anchored by RealForensics' finding that learning real-only AV correspondence generalizes better than memorizing generation artifacts [4], with AV-HuBERT remaining the dominant backbone [5]; this is now the crowded 2026 direction [3]. The second invests in heavyweight task-specific pipelines, exemplified by X-AVDT [2]: DDIM-inversion reconstruction plus AV cross-attention alignment reports 95.29% AUROC on its new MMDF benchmark (28.8k clips) and 99.69% on FakeAVCeleb, but 89.55% on FF++, roughly one minute of inversion per 16-frame clip, and outright failure on non-speech segments and multi-speaker scenes. The tension — minimal-parameter tuning for robustness vs expensive reconstruction for accuracy — is unresolved, and [1] notes older-trained models sometimes generalize better than recent ones: the first hint of detector aging.

### 1.2 Evaluation infrastructure is the binding constraint

DeepfakeBench [7] demonstrated the cost of fragmentation: under one standardized protocol (15 methods, 9 datasets), methods exploiting data-specific forensic cues degraded sharply. Yet DeepfakeBench itself is video/image-only — no AV localization or attribution tracks. ASVspoof 5 [8] gives the audio community a standardized EER-based challenge; no equivalent standardized challenge exists for audiovisual or video detection. AV-Deepfake1M [6] is the strongest scale-and-richness attempt: >1M videos, >2K subjects, LLM-driven manipulations across video-only/audio-only/combined settings, attribution labels, and temporal forgery boundaries. Its best localization baseline (UMMAFormer, 51.64) shows temporal grounding far behind classification, and the 1M++ extension adds real-world perturbations precisely because detection models drop significantly on them [6]. LAV-DF [10] established in 2022 that clip-level classification is insufficient (136k+ temporal segments), yet most 2026 AV work still evaluates classification-only. FakeAVCeleb [9], though foundational, is small, celebrity-only, and built on older generators — an inflated-scores risk wherever it is used as a headline number. DeepfakeImpact [11] signals where benchmarking is heading (two-stage, real-world-impact metrics), but no such protocol exists for AV. None of the foundational datasets is maintained as a living benchmark; all are static snapshots aging against new generators.

## 2. Emerging Trends [Confidence: High]

### 2.1 The threat has shifted faster than the research community

VoxENES 2026 [12] — 53,628 bilingual recordings across ten LLM-era synthesis pipelines and ten transmission augmentations — found the best untuned detector at 28.98% EER, five of eight systems at or below chance, Seed-VC (diffusion voice conversion) above 41% EER, and several older models inverting their decisions. This is not a laboratory concern: the Resemble AI H1 2026 threat report [13] counts 821 verified attacks, 3.46M synthetic files, 15,736 victims, 22 political disinformation incidents exceeding one billion impressions, and corporate voice fraud that is "almost completely dark in the press" — attackers now target employment and identity rather than direct transfers [13]. Partial manipulation is the second consensus threat: insert/replace/delete edits bypass whole-utterance anti-spoofing [14], and SIDA [15] extends the pattern to social-media imagery, where detectors "struggle with issues of generalization" under realistic platform processing, motivating joint detection + mask localization + textual explanation. Minority positions are instructive: gaze-based conversational biometrics reach 99% against FaceShifter but only 73% against the real-time generator DeepFaceLive, and remain lab-only with no group calls [17]. SingFake [18] shows speech anti-spoofing fails on singing voice. Europol's law-enforcement report [16] frames the verification gap as an operational, institutional problem — not merely academic.

### 2.2 Efficiency: real progress, no consolidation

DeFakeQ [34] proves on-device deepfake detection is feasible: adaptive bit-width allocation plus channel-level feature restoration reaches 10–20% of full-precision storage, ~25 ms per frame (≤50 ms peak), 87 mW on Android/iOS/Raspberry Pi/ESP32 — but the paper's central finding is that general-purpose quantization fails for this task because fine-grained forensic cues are highly sensitive to compression. Surrounding work is fragmented: lightweight-model papers [35] and distillation approaches [36] share no common efficiency metric and no deployment packaging. No cross-model efficiency benchmark exists, and no study examines the compounding interaction of compression + adversarial robustness.

## 3. Critical Assessment [Confidence: High]

### 3.1 Neither detectors nor provenance are trustworthy as standalone evidence

Practitioners already treat detectors as supplementary evidence only, citing narrow training data, evasion, and ambiguous probabilities [20]. The empirical basis is strong: benchmark scores collapse in the wild [25]; mainstream detectors emit rigid labels with miscalibrated probabilities and "lack research on uncertainty estimation" [22]; and a 2026 audit of six public tools found humans at 94% accuracy vs 79% for the best system, forensic tools flagging up to 62% of genuine images as fake, AI classifiers missing ~half of fakes and scoring 0% on HeyGen content, and confidence scores incomparable across tools [28]. On the provenance side, C2PA dies on recompression and screenshots, forged content can carry technically valid manifests, and trust-list fees exclude small actors [21]; free one-click tools now strip C2PA and SynthID [26]. Adversarial desynchronization attacks show validly signed provenance can coexist with manipulated content — provenance must be cross-checked against detectors, an integration nobody ships [23]. Watermarking and detection communities remain disconnected [27].

Attribution is the area's genuine contradiction: TADA [24] shows training-free attribution is feasible (frozen self-supervised encoders + distance neighbors: .93 macro-F1 across five benchmarks, .84 cross-collection), but it degrades under support-set shift, and AV/open-world attribution remains unsolved. The only open-world attribution tooling (Tencent [24] — image-only, research-grade) has no maintained multimodal equivalent. The gap appears to be engineering and evaluation, not fundamentals.

### 3.2 The tooling ecosystem is a research-artifact graveyard

Deepware Scanner is unmaintained legacy software [20]; attribution tooling is research-grade only [24]; no open standard eval harness exists, so every paper reinvents comparison [1]. For journalists, platform trust-and-safety teams, and law enforcement there is no maintained, offline-capable, explainable open-source system — the nearest alternative is a patchwork of proprietary APIs. Notably, no source set audits public AV/video tools the way [28] audits image tools: the AV tooling landscape is unmeasured, itself a finding.

### 3.3 Robustness is broken, and no benchmark keeps score

Silent dataset poisoning [29] is the most severe result: invisible triggers in 5–10% of training data yield ~91–97% attack success across four backbones while benign accuracy stays ~96–99%; fine-tuning, pruning, and distillation all fail (residual ASR >84%); triggers survive JPEG and cropping. Evasion has been known-broken since 2021 [32], and generation-side anti-forgery perturbations [33] are never tested by standard benchmarks. The benchmark layer systematically omits these threats: DeepfakeBench lacks adaptive attacks, laundering pipelines, and temporal aging [7]; TalkingHeadBench lacks real-world noise, compression, aging, and adversarial stress [30]; and AADD-2025, the first community-wide adversarial challenge against detectors, was a one-off with no recurring successor [31]. The generalization paper [1] is equally telling by omission: it explicitly excludes adversarial evasion, fairness, temporal modeling, and incremental learning — the field's strongest methods and its hardest problems are studied in separate rooms.

## 4. Action Plan

- [ ] Discuss the converging gap with Habib and select the flagship direction (candidates below).
- [ ] Define the novelty claim precisely against the literature (this report is the baseline evidence).
- [ ] Scope a first milestone that runs on Kaggle/OpenToken GPUs (feature extraction + lightweight heads).
- [ ] Design the eval protocol as code first (pytest harness), before any model training.
- [ ] Pick datasets to close specific gaps: AV-Deepfake1M subsets for localization, VoxENES-style transmission augmentations for laundering, FakeAVCeleb/LAV-DF for AV classification.
- [ ] Decide the tooling surface (offline CLI / report export) that serves journalists and moderators.
- [ ] Reserve an adversarial/aging track from day one — it is the least-occupied, most-cited gap.

**Candidate flagship directions** (to be discussed, in priority order):
1. **Unified AV benchmark + leaderboard** (detection + temporal localization + attribution tracks, laundering/aging suites, continuously updated) — directly fills the [6][7][8][31] gap; novel; citable; the natural home for Multimodal-FNet as flagship baseline.
2. **Explainable forensic-evidence detector** — joint detection + localization + calibrated uncertainty + artifact-level evidence report, offline CLI, robust after social-media laundering — fills [14][15][22][28][20].
3. **Robustness/aging gym** — plug-and-play evasion + laundering + generator-zoo stress suite with rolling evaluation — fills [29][30][31][7].
4. **Training-free AV attribution layer fused with provenance cross-check** — fills [24][23][21].
5. **CPU-only efficient AV detector** (quantization-aware, Fourier-based) with efficiency-annotated leaderboard — fills [34][35][36].

## 5. Open Questions & Caveats

- **Title-level sources**: [3], [11], [16] carry weight but were not full-text verified — treat their specifics as directional.
- **AV tooling unmeasured**: no audit equivalent to [28] exists for AV/video public tools; the claim "no maintained AV tool" is inference from fragmentation, not direct measurement.
- **Efficiency area is thin**: three sources, one Tier 2; the standardization gap is well-evidenced, individual claims less so.
- **VoxENES numbers are brand-new** (2026-07) and may be contested; the direction (LLM-era audio collapse) is corroborated by [13] and [14].
- **Attribution feasibility tension**: TADA shows training-free attribution works in-domain; whether it survives generator fine-tuning and laundering is unresolved [24].
- **No end-to-end "detect + attribute + certify" system exists** — the integration itself is unvalidated territory.
- DeepfakeBench venue listed variously as NeurIPS 2023/2024 D&B across sources; treat as "NeurIPS Datasets & Benchmarks" without year certainty.

## Methodology

- **Depth**: deep. **Agents**: 4 parallel retrieval subagents (Wave 1, areas 1–7), 1 verification subagent (Phase 3.1, 10 claims), 1 synthesis subagent (Phase 5).
- **Waves**: one retrieval wave — the post-wave quality gate passed (every area ≥2 sources; ≥1 critical/opposing source per area; 36 unique sources ≥ deep-mode target of 30).
- **Citation corrections applied (Phase 3.1)**: (a) AV-Deepfake1M — "best localization baseline UMMAFormer 51.64" without asserting the exact metric label, and "detection models drop significantly" (not "evaluation frameworks"); (b) backdoor poisoning attack success corrected to ~91–97% (no reported number reaches 100%); (c) partial-spoof survey quote corrected to the verbatim "more detailed physical evidence is needed to support the results", and long-recording localization softened to "needs further validation".
- **Degradation notes**: three sources title-level only (marked); one 403-blocked MDPI survey dropped from the bibliography.
- **Renumbering**: retrieval agents used non-contiguous index ranges (1–12, 30–36, 60–70, 90–99); the bibliography below is renumbered cleanly and duplicates merged ([69],[91]→[1]; [95]→[7]).

## Bibliography

[1] Yermakov, Cech, Matas, Fritz — *Deepfake Detection that Generalizes Across Benchmarks* — https://arxiv.org/html/2508.06248v4 — v4 May 2026 — Tier 1
[2] Kim, Yun, Hong, Cha, Koo, Noh — *X-AVDT: Audio-Visual Cross-Attention for Robust Deepfake Detection* — https://arxiv.org/html/2603.08483v1 — Mar 2026 — Tier 1
[3] Boldisor et al. — *Investigating Self-Supervised Representations for Audio-Visual Deepfake Detection* — CVPR 2026 — Tier 1 (title-level)
[4] Haliassos, Mira, Petridis, Pantic — *RealForensics* — ICLR 2022 — Tier 1 [foundational]
[5] Shi et al. — *AV-HuBERT* — ICLR 2022 — Tier 1 [foundational]
[6] Cai, Ghosh, Dhall et al. — *AV-Deepfake1M* — https://github.com/controlnet/av-deepfake1m — ACM MM 2024 — Tier 1
[7] Yan, Zhang, Yuan, Lyu, Wu — *DeepfakeBench* — https://arxiv.org/html/2307.01426v2 — NeurIPS D&B — Tier 1 [foundational]
[8] Wang et al. — *ASVspoof 5* — arXiv 2408.08739 — INTERSPEECH 2024 — Tier 1 [foundational]
[9] Khalid, Tariq, Kim, Woo — *FakeAVCeleb* — NeurIPS 2021 D&B — Tier 1 [foundational]
[10] Cai, Stefanov, Dhall, Hayat — *LAV-DF* — CVPR 2022 — Tier 1 [foundational]
[11] Gong et al. — *DeepfakeImpact* — CVPR 2026 — Tier 1 (title-level)
[12] *VoxENES 2026: Benchmarking Generalization of Speech Deepfake Detectors* — https://arxiv.org/html/2607.11706v1 — Jul 2026 — Tier 1
[13] Resemble AI — *H1 2026 Deepfake Threat Report* — https://www.resemble.ai/resources/h1-2026-deepfake-threat-report — Aug 2026 — Tier 2
[14] *Manipulated Regions Localization for Partially Deepfake Audio: A Survey* — https://arxiv.org/html/2506.14396 — Jul 2025 — Tier 1
[15] Huang et al. — *SIDA* — CVPR 2025 — Tier 1
[16] Europol Innovation Lab — *Facing reality? Law enforcement and the challenge of deepfakes* — Tier 1 (title-level)
[17] *DeepFake Detection in Dyadic Video Calls using Point of Gaze* — https://arxiv.org/html/2509.25503v2 — Sep 2025 — Tier 1
[18] Zang et al. — *SingFake* — arXiv 2309.07525 — 2023 — Tier 1 [foundational]
[19] *TADA: Training-free Attribution and Out-of-Domain Detection of Synthetic Speech* — https://arxiv.org/html/2506.05802v3 — Jun 2025 — Tier 1
[20] Tow Center for Digital Journalism (Columbia) — *What Journalists Should Know About Deepfake Detection Technology in 2025* — cjr.org — Mar 2025 — Tier 2
[21] TrueScreen — *What Is C2PA? The Standard, Its Metadata and Real Limits* — truescreen.io — Mar 2026 — Tier 3
[22] *Towards reliable deepfake detection from uncertainty calibration perspective* — sciopen.com — 2025 — Tier 1
[23] *Authenticated Contradictions from Desynchronized Watermarks/C2PA* — arXiv 2603.02378 — Mar 2026 — Tier 1
[24] Tencent Youtu Lab — *Open-World DeepFake Attribution* — github.com/TencentYoutuResearch/OpenWorld-DeepFakeAttribution — 2024 — Tier 2
[25] Garg, Sharan et al. (UC Berkeley) — *Beyond the Benchmark: Generalization Limits of Deepfake Detectors in the Wild* — 2025 — Tier 1
[26] metastrip.app — *Remove AI Watermarks: C2PA, EXIF & SynthID* — Jun 2026 — Tier 3
[27] Xu et al. — *InvisMark* — WACV 2025 — Tier 1
[28] *How Effective Are Publicly Accessible Deepfake Detection Tools* — https://arxiv.org/html/2603.04456v1 — Mar 2026 — Tier 1
[29] Yuan, Dong, Li — *Deepfake Detectors Can No Longer Be Trusted* — https://arxiv.org/html/2505.08255v1 — May 2025 — Tier 1
[30] Xiong et al. — *TalkingHeadBench* — WACV 2026 — Tier 1
[31] AADD-2025 organizers — *Adversarial Attacks on Deepfake Detectors, ACM MM 2025 Grand Challenge* — dl.acm.org/doi/10.1145/3746027.3761983 — Oct 2025 — Tier 1
[32] Hussain et al. — *Evaluating the Vulnerability of Deepfake Detectors to Adversarial Attacks* — WACV 2021 — Tier 1 [foundational]
[33] *Anti-Forgery: Towards a Stealthy and Robust DeepFake Disruption Attack* — IJCAI 2022 — Tier 1 [foundational]
[34] Li, Sun, Zheng, Ma, Lam — *DeFakeQ* — https://arxiv.org/html/2604.08847v1 — Apr 2026 — Tier 1
[35] *LightFakeDetect* — MDPI Mathematics 13(19):3088 — 2025 — Tier 2
[36] *SPEED-Q* — AAAI 2025 — Tier 1

## Source Extracts

### [1] Deepfake Detection that Generalizes Across Benchmarks
- **Summary:** Freeze most weights, tune only LayerNorm (~0.03%), L2-normalize onto hypersphere, train on paired real–fake sequences. GenD across 14 benchmarks (2019–2025): AUROC 77.7–99.6%; recent-trained models collapse on older benchmarks; full fine-tuning → ~57% mean AUROC; FF++ validation set near-duplicate of training set. Omits adversarial evasion, fairness, temporal modeling, incremental learning.
- **Key quotes:** "We noticed that the FF++ validation set is very similar to the training set." "Full fine-tuning catastrophically degrades to ~57% mean AUROC due to dataset-specific memorization."
- **Source type:** academic | **Tier:** 1

### [2] X-AVDT
- **Summary:** DDIM inversion + AV cross-attention; introduces MMDF (28.8k clips). 95.29% AUROC MMDF, 99.69% FakeAVCeleb, 89.55% FF++; ~1 min inversion per 16-frame clip; fails on non-speech/multi-speaker scenes.
- **Source type:** academic | **Tier:** 1

### [3] Self-Supervised Representations for AV Deepfake Detection (CVPR 2026)
- **Summary:** Title-level: self-supervised AV representation analysis is the crowded 2026 direction; spectral/mixing-based efficient alternatives remain unclaimed.
- **Source type:** academic | **Tier:** 1 (title-level)

### [4] RealForensics (ICLR 2022) [foundational]
- **Summary:** Train on real-only talking-face videos with AV correspondence losses to avoid fake-artifact overfitting; still a standard baseline in 2026.
- **Source type:** academic | **Tier:** 1

### [5] AV-HuBERT (ICLR 2022) [foundational]
- **Summary:** Dominant self-supervised AV speech backbone; repurposing it for detection has known speech-dependence limits.
- **Source type:** academic | **Tier:** 1

### [6] AV-Deepfake1M (ACM MM 2024)
- **Summary:** >1M videos, >2K subjects, LLM-driven; video/audio/AV manipulations; attribution labels + temporal boundaries. UMMAFormer best localization baseline at 51.64; 1M++ adds real-world perturbations after detection models dropped significantly vs previous datasets.
- **Source type:** academic + repo | **Tier:** 1

### [7] DeepfakeBench (NeurIPS D&B) [foundational]
- **Summary:** 15 methods, 9 datasets, standardized protocol; data-specific-cue methods degrade under unified protocol; video/image-only — no AV localization/attribution/adversarial/aging tracks.
- **Source type:** academic | **Tier:** 1

### [8] ASVspoof 5 (INTERSPEECH 2024) [foundational]
- **Summary:** Standard audio-only anti-spoofing challenge (EER-based); no equivalent standardized challenge exists for AV/video — evidence of fragmentation.
- **Source type:** academic | **Tier:** 1

### [9] FakeAVCeleb (NeurIPS 2021) [foundational]
- **Summary:** 500+ celebrity videos, 4 audio + 4 video manipulation methods, per-modality labels; small, celebrity-only, older generators — inflated-scores risk.
- **Source type:** academic | **Tier:** 1

### [10] LAV-DF (CVPR 2022) [foundational]
- **Summary:** Temporal forgery localization, 136k+ segments; established clip-level classification insufficiency; most 2026 AV work still classification-only.
- **Source type:** academic | **Tier:** 1

### [11] DeepfakeImpact (CVPR 2026)
- **Summary:** Title-level: two-stage benchmarking with real-world-impact metrics; no such protocol exists for AV.
- **Source type:** academic | **Tier:** 1 (title-level)

### [12] VoxENES 2026
- **Summary:** 53,628 bilingual recordings, ten LLM-era pipelines, ten transmission augmentations; top untuned detector 28.98% EER; 5/8 at or below chance; Seed-VC >41% EER; older models invert decisions.
- **Source type:** academic | **Tier:** 1

### [13] Resemble AI H1 2026 Threat Report
- **Summary:** 821 verified attacks, 3.46M synthetic files, 15,736 victims, 22 political disinfo incidents >1B impressions; corporate voice fraud "almost completely dark in the press"; attackers target employment/identity.
- **Source type:** industry | **Tier:** 2

### [14] Partial-Spoof Localization Survey
- **Summary:** Insert/replace/delete edits bypass whole-utterance anti-spoofing; open problems: localization on multi-hour recordings needs further validation, outputs lack forensic justification ("more detailed physical evidence is needed to support the results"), AV imbalance.
- **Source type:** academic | **Tier:** 1

### [15] SIDA (CVPR 2025)
- **Summary:** SID-Set 300K social-media images; detectors "struggle with issues of generalization" under realistic platform processing; joint detection + mask localization + textual explanation.
- **Source type:** academic | **Tier:** 1

### [16] Europol Innovation Lab — Facing reality?
- **Summary:** Title-level: law-enforcement framing of the media-authentication verification gap.
- **Source type:** government | **Tier:** 1 (title-level)

### [17] Dyadic Video Calls using Point of Gaze
- **Summary:** Gaze biometrics + spectrograms, 2D CNN; 82% avg acc, 88.2% ROC-AUC, 47 subjects lab-only; 99% vs FaceShifter, 73% vs DeepFaceLive; no group calls, limited demographics.
- **Source type:** academic | **Tier:** 1

### [18] SingFake [foundational]
- **Summary:** Speech anti-spoofing fails on singing voice; singing/music sub-modality underserved.
- **Source type:** academic | **Tier:** 1

### [19] TADA
- **Summary:** Training-free attribution: frozen SSL encoder temporal averages + distance neighbors; .93 macro-F1 (5 benchmarks), .84 cross-collection; degrades under support-set shift; AV/open-world attribution unsolved.
- **Source type:** academic | **Tier:** 1

### [20] Tow Center (Columbia) 2025
- **Summary:** Journalists treat detectors as supplementary evidence only; narrow training data, evasion, ambiguous probabilities; no offline/reporting workflow; Deepware Scanner unmaintained.
- **Source type:** journalism-practice | **Tier:** 2

### [21] TrueScreen — C2PA limits
- **Summary:** Platform recompression strips C2PA; screenshots remove all metadata; forged content can carry valid manifests; trust-list fees exclude small actors.
- **Source type:** vendor | **Tier:** 3

### [22] Uncertainty calibration for deepfake detection
- **Summary:** Packed ensembles give calibration at no extra inference cost; mainstream detectors output rigid labels with miscalibrated probabilities; "lack research on uncertainty estimation".
- **Source type:** academic | **Tier:** 1

### [23] Authenticated Contradictions (desynchronization)
- **Summary:** Adversarial desynchronization: validly signed provenance coexists with manipulated content; provenance must be cross-checked against detectors.
- **Source type:** academic | **Tier:** 1

### [24] Tencent Open-World DeepFake Attribution
- **Summary:** Image-only, research-grade attribution framework; no maintained multimodal attribution tooling exists.
- **Source type:** repo | **Tier:** 2

### [25] Berkeley — Beyond the Benchmark
- **Summary:** Strong benchmark scores collapse in the wild; quantifies the benchmark-overfitting gap.
- **Source type:** academic | **Tier:** 1

### [26] metastrip.app — Remove AI Watermarks
- **Summary:** Free one-click tools strip C2PA/SynthID — provenance metadata trivially defeatable; detectors remain necessary.
- **Source type:** vendor | **Tier:** 3

### [27] InvisMark (WACV 2025)
- **Summary:** Robust invisible watermarking survives some transformations; watermarking and detection communities disconnected; robustness-vs-detection tradeoffs.
- **Source type:** academic | **Tier:** 1

### [28] How Effective Are Publicly Accessible Deepfake Detection Tools
- **Summary:** Six public tools: humans 94% vs best system 79%; forensic tools flag up to 62% of genuine images; AI classifiers miss ~half of fakes, 0% on HeyGen; confidence scores incomparable; results are time-stamped assessments.
- **Source type:** academic | **Tier:** 1

### [29] Deepfake Detectors Can No Longer Be Trusted
- **Summary:** Invisible backdoor triggers in 5–10% of training data → ~91–97% ASR across four backbones; benign accuracy ~96–99%; fine-tuning/pruning/distillation fail (residual ASR >84%); triggers survive JPEG/cropping.
- **Source type:** academic | **Tier:** 1

### [30] TalkingHeadBench (WACV 2026)
- **Summary:** Uneven cross-generator drops (EMOPortraits, Hallo2); misclassification from background attention; lacks real-world noise, compression, temporal aging, adversarial stress tests.
- **Source type:** academic | **Tier:** 1

### [31] AADD-2025 Grand Challenge
- **Summary:** First community-wide adversarial challenge against detectors (ACM MM 2025); one-off — no recurring, continuously updated evasion benchmark.
- **Source type:** academic + repo | **Tier:** 1

### [32] Vulnerability of Deepfake Detectors (WACV 2021) [foundational]
- **Summary:** Black-box attacks evade detectors via face-extraction and classification stages; robustness known broken for years.
- **Source type:** academic | **Tier:** 1

### [33] Anti-Forgery (IJCAI 2022) [foundational]
- **Summary:** Generation-side "unforgeable" perturbations; standard benchmarks never test this threat model.
- **Source type:** academic | **Tier:** 1

### [34] DeFakeQ
- **Summary:** Adaptive bit-width + channel feature restoration: 10–20% storage, ~25 ms/frame, 87 mW on mobile/edge; general-purpose quantization fails because forensic cues are highly sensitive to compression.
- **Source type:** academic | **Tier:** 1

### [35] LightFakeDetect (MDPI 2025)
- **Summary:** MobileNet-tradition lightweight image detector; light-model papers share no common efficiency metric or deployment packaging.
- **Source type:** academic | **Tier:** 2

### [36] SPEED-Q (AAAI 2025)
- **Summary:** Staged processing + enhanced distillation; efficiency work disconnected from unified benchmarks and compression-robustness analysis.
- **Source type:** academic | **Tier:** 1
