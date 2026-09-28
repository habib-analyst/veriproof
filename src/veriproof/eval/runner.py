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
