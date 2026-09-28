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
        verifying_key_hex="",
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
