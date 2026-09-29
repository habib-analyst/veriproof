from veriproof.data.dataset import compute_stats, generate_samples
from veriproof.data.launder import LAUNDER_OPS


def test_generate_samples_shape_and_balance():
    samples = generate_samples(n_real=4, n_tampered=6, seed=3)
    labels = [s["label"] for s in samples]
    assert labels.count(0) == 4 and labels.count(1) == 6
    for s in samples:
        assert s["mask"].shape == (s["image"].size[1], s["image"].size[0])
        assert s["launder_chain"] == "none" or all(
            op in LAUNDER_OPS for op in s["launder_chain"].split("|")
        )


def test_stats_counts():
    samples = generate_samples(n_real=2, n_tampered=8, seed=5)
    st = compute_stats(samples)
    assert st["n_real"] == 2 and st["n_tampered"] == 8
    assert sum(st["per_op"].values()) == 8
