# src/veriproof/data/dataset.py
import random

import numpy as np
from PIL import Image

from veriproof.data import launder, tamper
from veriproof.data.render import render_chat, render_payment

_TAMPER_FNS = {"copy_move": lambda im, d, s: tamper.apply_copy_move(im, s),
               "splice": lambda im, d, s: tamper.apply_splice(im, d, s),
               "text_edit": lambda im, d, s: tamper.apply_text_edit(im, s),
               "inpaint": lambda im, d, s: tamper.apply_inpaint(im, s)}
_RENDER_FNS = {"chat": render_chat, "payment": render_payment}
_CHAINS = [[], ["jpeg85"], ["resize05", "jpeg85"], ["sos"],
           ["png", "noise"], ["contrast", "jpeg85"]]

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
        samples.append({"image": img,
                        "mask": np.zeros((img.size[1], img.size[0]), dtype=np.uint8),
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
    per_op = {k: 0 for k in tamper.TAMPER_OPS}
    per_chain = {}
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
    rows = {k: [] for k in ("image", "mask", "label", "tamper_op",
                            "launder_chain", "seed", "style", "split")}
    for s in samples:
        rows["image"].append(s["image"])
        rows["mask"].append(Image.fromarray(s["mask"] * 255))
        rows["label"].append(s["label"])
        rows["tamper_op"].append(s["tamper_op"])
        rows["launder_chain"].append(s["launder_chain"])
        rows["seed"].append(s["seed"])
        rows["style"].append(s["style"])
        rows["split"].append(s["split"])
    ds = datasets.Dataset.from_dict(rows)
    ds_dict = datasets.DatasetDict(
        {k: ds.filter(lambda x, k=k: x["split"] == k) for k in ("train", "val", "test")})
    ds_dict.save_to_disk(out_dir)
    return ds_dict
