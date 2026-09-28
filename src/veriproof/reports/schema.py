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
    verifying_key_hex: str = ""

class ForensicReport(BaseModel):
    analysis: AnalysisResult
    custody: CustodyMeta
    signature: str = ""

    def payload_canonical_json(self) -> str:
        return self.model_dump_json(exclude={"signature"})
