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
