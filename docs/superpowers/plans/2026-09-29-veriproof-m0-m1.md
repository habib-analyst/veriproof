# VeriProof M0–M1 Implementation Plan (Foundation + EviForge-DB Screenshots)

> Note (2026-09-29, post-execution): `data_build.py` was later moved to `scripts/build_dataset.py` during the repo restructure. Task texts below describe the plan as written at execution time.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the VeriProof foundation (package, CI, Forensic Evidence Report schema, eval harness, CLI) and the EviForge-DB v1 screenshot dataset pipeline (synthetic messenger/payment UI renderer, tamper ops with masks, laundering chains, HF dataset builder).

**Architecture:** Layered Python package under `src/veriproof/`: `data` (render → tamper → launder → dataset), `models` (stub in M0/M1), `reports` (FER schema + Ed25519 signing), `api`/`cli` (thin), `eval` (protocol + metrics). Deterministic everything (seeded); masks are numpy uint8 0/1; laundering chains are recorded strings.

**Tech Stack:** Python 3.11, pip-installable package (setuptools + pyproject.toml), Pillow, NumPy, Pydantic v2, cryptography (Ed25519), Hugging Face `datasets` (builder only), pytest, ruff, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-29-veriproof-design.md` (this plan implements M0–M1 of §8)

## Global Constraints

- Python ≥3.11; all code in `src/veriproof/` (src layout); package name `veriproof`.
- Determinism: every generator function takes an explicit `seed`; no global RNG; no wall-clock timestamps inside hashed FER payloads.
- Masks: `np.ndarray` dtype `np.uint8`, values 0/1, same H×W as the image.
- No telemetry, no network calls at inference/report time (dataset build may hit HF hub only when publishing).
- Ruff lint (default rules) and pytest must pass in CI before any merge.
- Naming: modules under `data/` are `render.py`, `tamper.py`, `launder.py`, `dataset.py`; detector package `models/spectrace/`; report modules `reports/schema.py`, `reports/sign.py`.

---

### Task 1: Repo scaffold, git init, CI

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `src/veriproof/__init__.py`, `src/veriproof/version.py`, `src/veriproof/data/__init__.py`, `src/veriproof/models/__init__.py`, `src/veriproof/reports/__init__.py`, `src/veriproof/eval/__init__.py`, `src/veriproof/api/__init__.py`, `tests/__init__.py`, `tests/test_version.py`, `.github/workflows/ci.yml`, `README.md`

**Interfaces:**
- Produces: `veriproof.__version__` (read from `version.py`, single source of truth in pyproject via `dynamic = ["version"]`), importable subpackages `veriproof.data`, `veriproof.models`, `veriproof.reports`, `veriproof.eval`, `veriproof.api`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_version.py
import veriproof

def test_version_exists():
    assert isinstance(veriproof.__version__, str)
    assert veriproof.__version__.count(".") >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m venv .venv && .venv/Scripts/pip install -e ".[dev]" && .venv/Scripts/pytest tests/test_version.py -v` (Windows: use `.venv/Scripts/`; on POSIX `.venv/bin/`)
Expected: FAIL (package not installed / no `__version__`)

- [ ] **Step 3: Write minimal implementation**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "veriproof"
dynamic = ["version"]
description = "Tamper-evident forensic verification for everyday evidence media"
requires-python = ">=3.11"
dependencies = [
  "numpy>=1.26",
  "Pillow>=10.0",
  "pydantic>=2.5",
  "cryptography>=42.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4"]
data = ["datasets>=2.19"]

[tool.setuptools.dynamic]
version = {attr = "veriproof.version.__version__"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# src/veriproof/version.py
__version__ = "0.1.0"
```

```python
# src/veriproof/__init__.py
from veriproof.version import __version__
```

```gitignore
# .gitignore
__pycache__/
*.pyc
.venv/
.pytest_cache/
.ruff_cache/
dist/
build/
*.egg-info/
data/raw/
data/processed/
```

```yaml
# .github/workflows/ci.yml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e ".[dev]"
      - run: ruff check src tests
      - run: pytest -v
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/Scripts/pytest tests/test_version.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd "D:/Projects by qoder/veriproof" && git init -b main
git add pyproject.toml .gitignore src tests .github README.md
git commit -m "feat: veriproof package scaffold with CI"
```

---

### Task 2: FER schema v0.1 + Ed25519 signing

**Files:**
- Create: `src/veriproof/reports/schema.py`, `src/veriproof/reports/sign.py`, `tests/test_reports.py`

**Interfaces:**
- Consumes: `veriproof.__version__`
- Produces (import from `veriproof.reports.schema`): `AnalysisResult`, `LocalizationEvidence`, `RegionFinding`, `CustodyMeta`, `ForensicReport`, `FER_SCHEMA_VERSION = "0.1"`; from `veriproof.reports.sign`: `SigningKeyBundle(private_key_pem: str)`, `sign_report(report: ForensicReport, bundle: SigningKeyBundle) -> ForensicReport` (returns report with `signature` filled), `verify_report(report: ForensicReport) -> bool`
- Canonical signing rule: serialize `report.payload_canonical_json()` (pydantic `model_dump_json` with sorted keys on all fields EXCEPT `signature`), sign bytes with Ed25519, store signature base64 in `report.signature`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_reports.py
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from veriproof.reports.schema import (AnalysisResult, LocalizationEvidence,
                                      RegionFinding, CustodyMeta, ForensicReport)
from veriproof.reports.sign import SigningKeyBundle, sign_report, verify_report

def _sample_report():
    analysis = AnalysisResult(
        model_id="spectrace-v0-dummy",
        model_version="0.0.0",
        detector_kind="image_tamper",
        tamper_probability=0.83,
        confidence=0.79,
        localization=LocalizationEvidence(
            heatmap_b64="iVBORw0KGgo=",
            regions=[RegionFinding(bbox=[10, 20, 100, 60], score=0.91)],
        ),
    )
    custody = CustodyMeta(
        tool_version="0.1.0",
        schema_version="0.1",
        media_sha256="a" * 64,
        media_format="png",
    )
    return ForensicReport(analysis=analysis, custody=custody, signature="")

def test_sign_and_verify_roundtrip():
    report = _sample_report()
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes_raw()  # 32 bytes seed; bundle wraps it
    bundle = SigningKeyBundle(private_key_pem=pem.hex())
    signed = sign_report(report, bundle)
    assert verify_report(signed) is True

def test_tampered_report_fails_verification():
    signed = sign_report(_sample_report(), SigningKeyBundle(private_key_pem=Ed25519PrivateKey.generate().private_bytes_raw().hex()))
    signed.analysis.tamper_probability = 0.01
    assert verify_report(signed) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_reports.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/veriproof/reports/schema.py
from pydantic import BaseModel, Field

FER_SCHEMA_VERSION = "0.1"

class RegionFinding(BaseModel):
    bbox: list[int] = Field(min_length=4, max_length=4)
    score: float = Field(ge=0.0, le=1.0)

class LocalizationEvidence(BaseModel):
    heatmap_b64: str = ""
    regions: list[RegionFinding] = []

class AnalysisResult(BaseModel):
    model_id: str
    model_version: str
    detector_kind: str
    tamper_probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    localization: LocalizationEvidence

class CustodyMeta(BaseModel):
    tool_version: str
    schema_version: str = FER_SCHEMA_VERSION
    media_sha256: str
    media_format: str

class ForensicReport(BaseModel):
    analysis: AnalysisResult
    custody: CustodyMeta
    signature: str = ""

    def payload_canonical_json(self) -> str:
        return self.model_dump_json(exclude={"signature"})
```

```python
# src/veriproof/reports/sign.py
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey)
from veriproof.reports.schema import ForensicReport

class SigningKeyBundle:
    def __init__(self, private_key_pem: str):
        seed = bytes.fromhex(private_key_pem)
        self._key = Ed25519PrivateKey.from_private_bytes(seed)

    def public_key_hex(self) -> str:
        return self._key.public_key().public_bytes_raw().hex()

def sign_report(report: ForensicReport, bundle: SigningKeyBundle) -> ForensicReport:
    payload = report.payload_canonical_json().encode()
    report.signature = base64.b64encode(bundle._key.sign(payload)).decode()
    return report

def verify_report(report: ForensicReport) -> bool:
    try:
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex("00" * 32))
    except Exception:
        pass
    # public key must come from the report itself for tamper-evidence:
    # v0.1 embeds the verifying key in custody; see step 4 fix below.
    raise NotImplementedError
```

**Step 3 fix (required — write it this way, not the stub above):** add `verifying_key_hex: str = ""` to `CustodyMeta`, set it inside `sign_report` (`report.custody.verifying_key_hex = bundle.public_key_hex()`), and implement `verify_report` as: parse public key from `report.custody.verifying_key_hex`, `Ed25519PublicKey.from_public_bytes(bytes.fromhex(...))`, then `key.verify(base64.b64decode(report.signature), report.payload_canonical_json().encode())`, return True on success, False on any exception. Update `_sample_report()` in the test to include the new field — the test above already works once `CustodyMeta` gains the field with default `""`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/pytest tests/test_reports.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/veriproof/reports tests/test_reports.py
git commit -m "feat: FER schema v0.1 with Ed25519 signing and tamper-evident verification"
```

---

### Task 3: Eval harness core (protocol + metrics + dummy run)

**Files:**
- Create: `src/veriproof/eval/protocol.py`, `src/veriproof/eval/metrics.py`, `src/veriproof/eval/runner.py`, `tests/test_eval.py`

**Interfaces:**
- Consumes: none (standalone)
- Produces (from `veriproof.eval.protocol`): `GroundTruth(label: int, mask: np.ndarray | None)`, `Prediction(label: int, proba: float, mask: np.ndarray | None)`; from `veriproof.eval.metrics`: `compute_detection_metrics(gt_labels: list[int], pred_labels: list[int], probas: list[float]) -> dict` with keys `accuracy`, `auc`; `compute_localization_metrics(gt_masks: list[np.ndarray], pred_masks: list[np.ndarray]) -> dict` with keys `iou`, `f1`; from `veriproof.eval.runner`: `run_eval(predict_fn, samples: list[tuple[GroundTruth, np.ndarray | None]]) -> dict` — the media arg is the raw image array; returns merged dict.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_eval.py
import numpy as np
from veriproof.eval.protocol import GroundTruth, Prediction
from veriproof.eval.metrics import compute_detection_metrics, compute_localization_metrics

def test_detection_metrics_perfect_and_chance():
    gt = [0, 1, 1, 0]
    pred = [0, 1, 1, 0]
    proba = [0.1, 0.9, 0.8, 0.2]
    m = compute_detection_metrics(gt, pred, proba)
    assert m["accuracy"] == 1.0
    assert m["auc"] == 1.0
    m2 = compute_detection_metrics([0, 1, 0, 1], [1, 0, 1, 0], [0.9, 0.1, 0.9, 0.1])
    assert m2["accuracy"] == 0.0

def test_localization_metrics():
    a = np.zeros((8, 8), dtype=np.uint8); a[2:6, 2:6] = 1
    b = np.zeros((8, 8), dtype=np.uint8); b[3:7, 3:7] = 1
    m = compute_localization_metrics([a], [b])
    assert 0.0 < m["iou"] < 1.0
    assert 0.0 < m["f1"] <= 1.0
    m2 = compute_localization_metrics([a], [a])
    assert m2["iou"] == 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_eval.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/veriproof/eval/protocol.py
from dataclasses import dataclass
import numpy as np

@dataclass
class GroundTruth:
    label: int          # 0=real, 1=tampered
    mask: np.ndarray | None = None

@dataclass
class Prediction:
    label: int
    proba: float
    mask: np.ndarray | None = None
```

```python
# src/veriproof/eval/metrics.py
import numpy as np

def _auc(y_true: list[int], proba: list[float]) -> float:
    y, p = np.asarray(y_true), np.asarray(proba)
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    n = len(pos) * len(neg)
    return float((pos[:, None] > neg[None, :]).sum() / n)

def compute_detection_metrics(gt_labels, pred_labels, probas):
    y, p = np.asarray(gt_labels), np.asarray(pred_labels)
    return {"accuracy": float((y == p).mean()), "auc": _auc(gt_labels, probas)}

def compute_localization_metrics(gt_masks, pred_masks):
    g = np.stack(gt_masks).astype(bool)
    p = np.stack(pred_masks).astype(bool)
    inter = (g & p).sum(axis=(1, 2)); union = (g | p).sum(axis=(1, 2))
    iou = np.mean(inter / np.maximum(union, 1))
    tp = inter.sum(); fp = (p & ~g).sum(); fn = (~p & g).sum()
    f1 = 2 * tp / max(2 * tp + fp + fn, 1)
    return {"iou": float(iou), "f1": float(f1)}
```

```python
# src/veriproof/eval/runner.py
from veriproof.eval.metrics import compute_detection_metrics, compute_localization_metrics

def run_eval(predict_fn, samples):
    gts, preds = [], []
    for gt, media in samples:
        preds.append(predict_fn(media))
        gts.append(gt)
    out = compute_detection_metrics([g.label for g in gts],
                                    [p.label for p in preds],
                                    [p.proba for p in preds])
    if all(g.mask is not None for g in gts) and all(p.mask is not None for p in preds):
        out.update(compute_localization_metrics([g.mask for g in gts], [p.mask for p in preds]))
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/pytest tests/test_eval.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/veriproof/eval tests/test_eval.py
git commit -m "feat: eval harness core with detection and localization metrics"
```

---

### Task 4: CLI skeleton (--version + verify stub)

**Files:**
- Create: `src/veriproof/cli.py`, `tests/test_cli.py`
- Modify: `pyproject.toml` (add `[project.scripts] veriproof = "veriproof.cli:main"`)

**Interfaces:**
- Consumes: `ForensicReport`, `AnalysisResult`, `LocalizationEvidence`, `CustodyMeta` (Task 2), `veriproof.__version__`
- Produces: `veriproof.cli.main(argv: list[str] | None = None) -> int` (exit code); console entry point `veriproof`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
from veriproof.cli import main
import veriproof

def test_version_flag(capsys):
    assert main(["--version"]) == 0
    out = capsys.readouterr().out
    assert veriproof.__version__ in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_cli.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/veriproof/cli.py
import argparse
import veriproof

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="veriproof",
        description="Tamper-evident forensic verification for everyday evidence media")
    parser.add_argument("--version", action="version", version=veriproof.__version__)
    sub = parser.add_subparsers(dest="cmd")
    v = sub.add_parser("verify", help="verify a media file (coming in M4)")
    v.add_argument("file")
    args = parser.parse_args(argv)
    if args.cmd == "verify":
        parser.exit(1, "verify: not implemented until M4\n")
    parser.print_help()
    return 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/Scripts/pytest tests/test_cli.py -v` then `.venv/Scripts/veriproof --version`
Expected: PASS; CLI prints `0.1.0`

- [ ] **Step 5: Commit**

```bash
git add src/veriproof/cli.py tests/test_cli.py pyproject.toml
git commit -m "feat: veriproof CLI with --version and verify stub"
```

---

### Task 5: Messenger + payment UI renderer

**Files:**
- Create: `src/veriproof/data/render.py`, `tests/test_render.py`

**Interfaces:**
- Consumes: none (Pillow only)
- Produces (from `veriproof.data.render`): `render_chat(seed: int, size=(1080, 1920)) -> PIL.Image.Image`, `render_payment(seed: int, size=(1080, 1920)) -> PIL.Image.Image`; `RENDER_STYLE_KEYS = ("chat", "payment")`
- Determinism rule: same seed → byte-identical PNG (assert in test).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_render.py
import io
from veriproof.data.render import render_chat, render_payment

def test_render_deterministic():
    a, b = render_chat(42), render_chat(42)
    buf_a, buf_b = io.BytesIO(), io.BytesIO()
    a.save(buf_a, "PNG"); b.save(buf_b, "PNG")
    assert buf_a.getvalue() == buf_b.getvalue()

def test_render_varied_and_correct_size():
    imgs = [render_chat(i) for i in range(3)] + [render_payment(i) for i in range(3)]
    assert all(im.size == (1080, 1920) for im in imgs)
    bufs = []
    for im in imgs:
        b = io.BytesIO(); im.save(b, "PNG"); bufs.append(b.getvalue())
    assert len(set(bufs)) == 6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_render.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/veriproof/data/render.py
import random
from PIL import Image, ImageDraw

def _rng(seed):
    return random.Random(f"veriproof-render-{seed}")

def render_chat(seed: int, size=(1080, 1920)) -> Image.Image:
    r = _rng(seed)
    W, H = size
    img = Image.new("RGB", size, (18, 140, 126))  # WhatsApp-dark teal backdrop
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 110], fill=(8, 84, 74))
    d.text((30, 35), f"Contact {r.randint(1, 999)}", fill=(255, 255, 255))
    names = ["You", "Them"]
    y = 160
    for i in range(r.randint(6, 12)):
        rng2 = _rng(seed + i)
        text = " ".join("word" for _ in range(rng2.randint(2, 8)))
        mine = i % 2 == 0
        w = rng2.randint(220, 620); h = rng2.randint(90, 160)
        x = W - w - 40 if mine else 40
        bubble = (66, 183, 66) if mine else (37, 45, 49)
        d.rounded_rectangle([x, y, x + w, y + h], 18, fill=bubble)
        d.text((x + 20, y + 15), text[:40], fill=(255, 255, 255))
        d.text((x + w - 90, y + h - 40), f"{rng2.randint(1,12)}:{rng2.randint(0,59):02d} PM", fill=(200, 200, 200))
        if mine:
            d.text((x + w - 60, y + h - 22), "\u2713\u2713", fill=(120, 200, 255))
        y += h + 30
    return img

def render_payment(seed: int, size=(1080, 1920)) -> Image.Image:
    r = _rng(seed)
    W, H = size
    img = Image.new("RGB", size, (245, 247, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 150], fill=(21, 101, 192))
    d.text((40, 50), "BankApp", fill=(255, 255, 255))
    card = [60, 240, W - 60, 720]
    d.rounded_rectangle(card, 24, fill=(255, 255, 255), outline=(200, 205, 210), width=2)
    d.text((110, 300), f"Rs {r.randint(5000, 900000):,}", fill=(20, 20, 20))
    d.text((110, 380), "Transfer Successful", fill=(46, 125, 50))
    d.text((110, 460), f"Ref: VRF{r.randint(10**8, 10**9)}", fill=(90, 90, 90))
    d.text((110, 520), f"{r.randint(1,28):02d} Sep 2026, {r.randint(9,20)}:{r.randint(0,59):02d}", fill=(90, 90, 90))
    d.text((110, 600), "To: Account ****" + str(r.randint(1000, 9999)), fill=(90, 90, 90))
    return img
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/pytest tests/test_render.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/veriproof/data/render.py tests/test_render.py
git commit -m "feat: deterministic messenger and payment UI renderer"
```

---

### Task 6: Tamper ops v1 (copy-move, splice, text-edit, inpaint) with masks

**Files:**
- Create: `src/veriproof/data/tamper.py`, `tests/test_tamper.py`

**Interfaces:**
- Consumes: `render_chat`, `render_payment` (Task 5)
- Produces (from `veriproof.data.tamper`): `apply_copy_move(img, seed) -> tuple[Image.Image, np.ndarray]`, `apply_splice(img, donor_img, seed) -> ...`, `apply_text_edit(img, seed) -> ...`, `apply_inpaint(img, seed) -> ...`, `TAMPER_OPS = ("copy_move", "splice", "text_edit", "inpaint")`
- Contract: returned mask is `np.uint8` 0/1, same H×W; mask is non-empty (sum > 0) for every op.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tamper.py
import numpy as np
from veriproof.data.render import render_chat
from veriproof.data.tamper import (apply_copy_move, apply_splice, apply_text_edit,
                                   apply_inpaint, TAMPER_OPS)

def test_all_ops_return_valid_masks():
    img = render_chat(7)
    donor = render_chat(8)
    results = {
        "copy_move": apply_copy_move(img, 1),
        "splice": apply_splice(img, donor, 1),
        "text_edit": apply_text_edit(img, 1),
        "inpaint": apply_inpaint(img, 1),
    }
    assert set(results) == set(TAMPER_OPS)
    for name, (out, mask) in results.items():
        assert out.size == img.size, name
        assert mask.shape == (img.size[1], img.size[0]), name
        assert mask.dtype == np.uint8, name
        assert set(np.unique(mask)) <= {0, 1}, name
        assert mask.sum() > 0, name
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_tamper.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/veriproof/data/tamper.py
import random
import numpy as np
from PIL import Image

TAMPER_OPS = ("copy_move", "splice", "text_edit", "inpaint")

def _rng(seed):
    return random.Random(f"veriproof-tamper-{seed}")

def _region(rng, w, h, max_frac=0.35):
    rw = int(w * rng.uniform(0.1, max_frac)); rh = int(h * rng.uniform(0.1, max_frac))
    x = rng.randint(0, w - rw); y = rng.randint(0, h - rh)
    return x, y, rw, rh

def _mask_from_region(size, x, y, rw, rh):
    m = np.zeros((size[1], size[0]), dtype=np.uint8)
    m[y:y+rh, x:x+rw] = 1
    return m

def apply_copy_move(img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height)
    src = img.crop((x, y, x+rw, y+rh))
    x2, y2 = r.randint(0, img.width - rw), r.randint(0, img.height - rh)
    out = img.copy(); out.paste(src, (x2, y2))
    return out, _mask_from_region(img.size, x2, y2, rw, rh)

def apply_splice(img, donor_img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height)
    src = donor_img.crop((x, y, x+rw, y+rh))
    out = img.copy(); out.paste(src, (x, y))
    return out, _mask_from_region(img.size, x, y, rw, rh)

def apply_text_edit(img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height, max_frac=0.25)
    out = img.copy(); d = ImageDraw.Draw(out)
    d.rectangle([x, y, x+rw, y+rh], fill=(255, 255, 255))
    d.text((x + 5, y + 5), "edited " + str(r.randint(1000, 9999)), fill=(0, 0, 0))
    return out, _mask_from_region(img.size, x, y, rw, rh)

def apply_inpaint(img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height)
    arr = np.asarray(img).astype(np.float32)
    patch = arr[y:y+rh, x:x+rw]
    arr[y:y+rh, x:x+rw] = patch.mean(axis=(0, 1), keepdims=True) + r.uniform(-8, 8)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return out, _mask_from_region(img.size, x, y, rw, rh)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/pytest tests/test_tamper.py -v`
Expected: PASS (1 test, 4 ops)

- [ ] **Step 5: Commit**

```bash
git add src/veriproof/data/tamper.py tests/test_tamper.py
git commit -m "feat: tamper ops v1 with pixel masks"
```

---

### Task 7: Laundering pipeline

**Files:**
- Create: `src/veriproof/data/launder.py`, `tests/test_launder.py`

**Interfaces:**
- Consumes: none (Pillow/numpy)
- Produces (from `veriproof.data.launder`): `apply_launder(img, chain: list[str]) -> tuple[Image.Image, str]` (second value = canonical chain string, e.g. `"jpeg85|resize05|sos"`); `LAUNDER_OPS = ("jpeg85", "resize05", "sos", "png", "noise", "contrast")`
- Contract: unknown op name → `ValueError`; empty chain → image unchanged, returns `"none"`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_launder.py
import io
import pytest
from PIL import Image
from veriproof.data.launder import apply_launder, LAUNDER_OPS

def _img():
    return Image.new("RGB", (640, 640), (120, 40, 200))

def test_empty_chain_unchanged():
    img = _img()
    out, chain = apply_launder(img, [])
    assert chain == "none"
    assert list(out.getdata()) == list(img.getdata())

def test_jpeg85_changes_and_marks_chain():
    out, chain = apply_launder(_img(), ["jpeg85"])
    assert chain == "jpeg85"
    assert out.size == (640, 640)

def test_unknown_op_raises():
    with pytest.raises(ValueError):
        apply_launder(_img(), ["not_an_op"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_launder.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/veriproof/data/launder.py
import io
import numpy as np
from PIL import Image, ImageEnhance

LAUNDER_OPS = ("jpeg85", "resize05", "sos", "png", "noise", "contrast")

def _op_jpeg85(img):
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=85); buf.seek(0)
    return Image.open(buf).convert("RGB")

def _op_resize05(img):
    return img.resize((img.width // 2, img.height // 2), Image.BILINEAR).resize(img.size, Image.BILINEAR)

def _op_sos(img):
    w, h = img.size
    crop = img.crop((int(w*0.02), int(h*0.02), int(w*0.98), int(h*0.98)))
    out = crop.resize((w, h), Image.BILINEAR)
    return _op_jpeg85(out)

def _op_png(img):
    buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
    return Image.open(buf).convert("RGB")

def _op_noise(img):
    arr = np.asarray(img).astype(np.float32)
    arr += np.random.default_rng(0).normal(0, 6, arr.shape)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def _op_contrast(img):
    return ImageEnhance.Contrast(img).enhance(1.25)

_OPS = {"jpeg85": _op_jpeg85, "resize05": _op_resize05, "sos": _op_sos,
        "png": _op_png, "noise": _op_noise, "contrast": _op_contrast}

def apply_launder(img, chain):
    if not chain:
        return img, "none"
    out = img
    for op in chain:
        if op not in _OPS:
            raise ValueError(f"unknown laundering op: {op}")
        out = _OPS[op](out)
    return out, "|".join(chain)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/pytest tests/test_launder.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/veriproof/data/launder.py tests/test_launder.py
git commit -m "feat: laundering pipeline with chain recording"
```

---

### Task 8: EviForge-DB builder (HF datasets + splits + card + stats)

**Files:**
- Create: `src/veriproof/data/dataset.py`, `tests/test_dataset.py`, `data_build.py` (repo root, build entry point)

**Interfaces:**
- Consumes: Tasks 5–7 (`render_chat/render_payment`, tamper ops, `apply_launder`), `GroundTruth` (Task 3)
- Produces (from `veriproof.data.dataset`): `generate_samples(n_real: int, n_tampered: int, seed: int) -> list[dict]` where each dict = `{"image": PIL.Image, "mask": np.ndarray, "label": int, "tamper_op": str, "launder_chain": str, "seed": int, "style": str}`; `build_hf_dataset(out_dir: str, n_real: int, n_tampered: int, seed: int) -> DatasetDict` with splits `train/test/val` (70/15/15 by seed ranges); `compute_stats(samples: list[dict]) -> dict` with keys `n_real`, `n_tampered`, `per_op: dict`, `per_chain: dict`
- Split rule: `seed % 10 < 7` → train, `< 8.5` → val, else test (applies to tampered-sample seeds; real samples get independent seed space `seed + 1_000_000`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_dataset.py
from veriproof.data.dataset import generate_samples, compute_stats

def test_generate_samples_shape_and_balance():
    samples = generate_samples(n_real=4, n_tampered=6, seed=3)
    labels = [s["label"] for s in samples]
    assert labels.count(0) == 4 and labels.count(1) == 6
    for s in samples:
        assert s["mask"].shape == (s["image"].size[1], s["image"].size[0])
        assert s["launder_chain"] in ("none",) or "|" in s["launder_chain"]

def test_stats_counts():
    samples = generate_samples(n_real=2, n_tampered=8, seed=5)
    st = compute_stats(samples)
    assert st["n_real"] == 2 and st["n_tampered"] == 8
    assert sum(st["per_op"].values()) == 8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_dataset.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/veriproof/data/dataset.py
import random
import numpy as np
from veriproof.data.render import render_chat, render_payment
from veriproof.data import tamper, launder

_TAMPER_FNS = {"copy_move": lambda im, d, s: tamper.apply_copy_move(im, s),
               "splice": lambda im, d, s: tamper.apply_splice(im, d, s),
               "text_edit": lambda im, d, s: tamper.apply_text_edit(im, s),
               "inpaint": lambda im, d, s: tamper.apply_inpaint(im, s)}
_RENDER_FNS = {"chat": render_chat, "payment": render_payment}
_CHAINS = [[], ["jpeg85"], ["resize05", "jpeg85"], ["sos"], ["png", "noise"], ["contrast", "jpeg85"]]

def _split_of(seed: int) -> str:
    r = seed % 10
    return "train" if r < 7 else ("val" if r < 8.5 else "test")

def generate_samples(n_real, n_tampered, seed):
    rng = random.Random(f"veriproof-ds-{seed}")
    samples = []
    for i in range(n_real):
        s = seed + 1_000_000 + i
        style = rng.choice(list(_RENDER_FNS))
        img = _RENDER_FNS[style](s)
        img, chain = launder.apply_launder(img, rng.choice(_CHAINS))
        samples.append({"image": img, "mask": np.zeros((img.size[1], img.size[0]), dtype=np.uint8),
                        "label": 0, "tamper_op": "none", "launder_chain": chain,
                        "seed": s, "style": style, "split": _split_of(s % 1000)})
    for i in range(n_tampered):
        s = seed + i
        style = rng.choice(list(_RENDER_FNS))
        img = _RENDER_FNS[style](s)
        donor = _RENDER_FNS[style](s + 500_000)
        op = rng.choice(list(_TAMPER_FNS))
        img, mask = _TAMPER_FNS[op](img, donor, s)
        img, chain = launder.apply_launder(img, rng.choice(_CHAINS))
        samples.append({"image": img, "mask": mask, "label": 1, "tamper_op": op,
                        "launder_chain": chain, "seed": s, "style": style, "split": _split_of(s)})
    return samples

def compute_stats(samples):
    per_op = {k: 0 for k in tamper.TAMPER_OPS}; per_chain = {}
    for s in samples:
        if s["label"] == 1:
            per_op[s["tamper_op"]] += 1
        per_chain[s["launder_chain"]] = per_chain.get(s["launder_chain"], 0) + 1
    return {"n_real": sum(1 for s in samples if s["label"] == 0),
            "n_tampered": sum(1 for s in samples if s["label"] == 1),
            "per_op": per_op, "per_chain": per_chain}

def build_hf_dataset(out_dir, n_real, n_tampered, seed):
    import datasets
    samples = generate_samples(n_real, n_tampered, seed)
    rows = {k: [] for k in ("image", "mask", "label", "tamper_op", "launder_chain", "seed", "style", "split")}
    for s in samples:
        rows["image"].append(s["image"]); rows["mask"].append(Image.fromarray(s["mask"] * 255))
        rows["label"].append(s["label"]); rows["tamper_op"].append(s["tamper_op"])
        rows["launder_chain"].append(s["launder_chain"]); rows["seed"].append(s["seed"])
        rows["style"].append(s["style"]); rows["split"].append(s["split"])
    ds = datasets.Dataset.from_dict(rows)
    return datasets.DatasetDict({k: ds.filter(lambda x, k=k: x["split"] == k) for k in ("train", "val", "test")})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/pytest tests/test_dataset.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/veriproof/data/dataset.py tests/test_dataset.py
git commit -m "feat: EviForge-DB v1 generator with splits and stats"
```

---

### Task 9: Golden regression tests + build entry point + README

**Files:**
- Create: `data_build.py`, `tests/test_golden.py`, golden fixture generated at test time (no committed binary)
- Modify: `README.md`

**Interfaces:**
- Consumes: all of Tasks 1–8
- Produces: `data_build.py` CLI: `python data_build.py --out data/processed/eviforge-db-v1 --n-real 2000 --n-tampered 2000 --seed 20260929` → prints `compute_stats` JSON and writes a `stats.json`; golden test pins hashes of `render_chat(42)` and `apply_copy_move(render_chat(7), 1)` outputs.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_golden.py
import hashlib, io
from veriproof.data.render import render_chat
from veriproof.data.tamper import apply_copy_move

def _png_sha(img):
    b = io.BytesIO(); img.save(b, "PNG")
    return hashlib.sha256(b.getvalue()).hexdigest()

def test_render_golden_hash():
    assert _png_sha(render_chat(42)) == _png_sha(render_chat(42))  # determinism anchor
    # The golden VALUE is pinned on first CI run and recorded in this file after
    # visual inspection; until then this only locks determinism.
    assert _png_sha(render_chat(42)) == "PINNED_AFTER_FIRST_CI_RUN"

def test_tamper_golden_hash():
    img, mask = apply_copy_move(render_chat(7), 1)
    assert _png_sha(img) == "PINNED_AFTER_FIRST_CI_RUN"
    assert mask.sum() > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/Scripts/pytest tests/test_golden.py -v`
Expected: FAIL (hash mismatch — expected, placeholder values)

- [ ] **Step 3: Pin the real hashes**

Run: `.venv/Scripts/python -c "import hashlib,io;from veriproof.data.render import render_chat;from veriproof.data.tamper import apply_copy_move;b=io.BytesIO();render_chat(42).save(b,'PNG');print('render',hashlib.sha256(b.getvalue()).hexdigest());im,_=apply_copy_move(render_chat(7),1);b=io.BytesIO();im.save(b,'PNG');print('tamper',hashlib.sha256(b.getvalue()).hexdigest())"`
Then replace both `"PINNED_AFTER_FIRST_CI_RUN"` strings in `tests/test_golden.py` with the printed values (render hash → render test, tamper hash → tamper test).

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/Scripts/pytest tests/ -v` and `.venv/Scripts/ruff check src tests`
Expected: all PASS, lint clean

- [ ] **Step 5: Commit**

```bash
git add tests/test_golden.py data_build.py README.md
git commit -m "test: golden hashes + dataset build entry point"
```

---

## Self-Review Notes

- Spec §8 M0 exit criteria (pytest green, version works, CI passes): Tasks 1–4. M1 exit criteria (dataset builds reproducibly, stats reported): Tasks 5–9. Spec §4.2 (contracts) covered by Task interfaces. Spec §7 testing strategy: unit (all tasks), golden (Task 9), protocol-first (Task 3 before any model), CI (Task 1).
- Placeholder scan: the only intentional placeholders are the two golden hash strings, resolved by a concrete pinning step inside Task 9 (Step 3) — no open-ended placeholders remain.
- Type consistency: `apply_copy_move(img, seed) -> (Image, np.ndarray)` used identically in Tasks 6, 8, 9; `GroundTruth` from Task 3 imported in Task 8's docstring contract only — dataset module itself does not depend on eval to avoid a data→eval coupling.
