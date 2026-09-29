# tests/test_reports.py
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from veriproof.reports.schema import (
    AnalysisResult,
    CustodyMeta,
    ForensicReport,
    LocalizationEvidence,
    RegionFinding,
)
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


def _bundle():
    return SigningKeyBundle(
        private_key_seed_hex=Ed25519PrivateKey.generate().private_bytes_raw().hex()
    )


def test_sign_and_verify_roundtrip():
    report = _sample_report()
    signed = sign_report(report, _bundle())
    assert signed.custody.verifying_key_hex
    assert verify_report(signed) is True


def test_tampered_payload_fails_verification():
    signed = sign_report(_sample_report(), _bundle())
    signed.analysis.tamper_probability = 0.01
    assert verify_report(signed) is False


def test_swapped_verifying_key_fails_verification():
    signed = sign_report(_sample_report(), _bundle())
    attacker = sign_report(_sample_report(), _bundle())
    signed.custody.verifying_key_hex = attacker.custody.verifying_key_hex
    assert verify_report(signed) is False


def test_corrupted_signature_fails_verification():
    signed = sign_report(_sample_report(), _bundle())
    chars = list(signed.signature)
    chars[0] = "A" if chars[0] != "A" else "B"
    signed.signature = "".join(chars)
    assert verify_report(signed) is False


def test_empty_verifying_key_fails_verification():
    report = _sample_report()
    report.signature = "AAAA"
    assert verify_report(report) is False
