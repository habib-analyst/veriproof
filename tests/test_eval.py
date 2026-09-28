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
