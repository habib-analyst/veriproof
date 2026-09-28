# src/veriproof/reports/sign.py
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from veriproof.reports.schema import ForensicReport


class SigningKeyBundle:
    def __init__(self, private_key_pem: str):
        seed = bytes.fromhex(private_key_pem)
        self._key = Ed25519PrivateKey.from_private_bytes(seed)

    def public_key_hex(self) -> str:
        return self._key.public_key().public_bytes_raw().hex()

def sign_report(report: ForensicReport, bundle: SigningKeyBundle) -> ForensicReport:
    report.custody.verifying_key_hex = bundle.public_key_hex()
    payload = report.payload_canonical_json().encode()
    report.signature = base64.b64encode(bundle._key.sign(payload)).decode()
    return report

def verify_report(report: ForensicReport) -> bool:
    try:
        key = Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(report.custody.verifying_key_hex))
        key.verify(
            base64.b64decode(report.signature),
            report.payload_canonical_json().encode())
        return True
    except Exception:  # noqa: BLE001 - verification of untrusted input must not raise
        return False
