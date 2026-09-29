# src/veriproof/data/launder.py
import io

import numpy as np
from PIL import Image, ImageEnhance

LAUNDER_OPS = ("jpeg85", "resize05", "sos", "png", "noise", "contrast")

def _op_jpeg85(img):
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=85); buf.seek(0)
    return Image.open(buf).convert("RGB")

def _op_resize05(img):
    return img.resize((img.width // 2, img.height // 2), Image.BILINEAR).resize(img.size, Image.BILINEAR)

def _op_sos(img):
    w, h = img.size
    crop = img.crop((int(w*0.02), int(h*0.02), int(w*0.98), int(h*0.98)))
    out = crop.resize((w, h), Image.BILINEAR)
    return _op_jpeg85(out)

def _op_png(img):
    buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
    return Image.open(buf).convert("RGB")

def _op_noise(img):
    arr = np.asarray(img).astype(np.float32)
    arr += np.random.default_rng(0).normal(0, 6, arr.shape)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def _op_contrast(img):
    return ImageEnhance.Contrast(img).enhance(1.25)

_OPS = {"jpeg85": _op_jpeg85, "resize05": _op_resize05, "sos": _op_sos,
        "png": _op_png, "noise": _op_noise, "contrast": _op_contrast}

def apply_launder(img: Image.Image, chain: list[str]) -> tuple[Image.Image, str]:
    if not chain:
        return img, "none"
    out = img
    for op in chain:
        if op not in _OPS:
            raise ValueError(f"unknown laundering op: {op}")
        out = _OPS[op](out)
    return out, "|".join(chain)
