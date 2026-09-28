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
