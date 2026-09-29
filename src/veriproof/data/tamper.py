import random

import numpy as np
from PIL import Image, ImageDraw

TAMPER_OPS = ("copy_move", "splice", "text_edit", "inpaint")

def _rng(seed):
    return random.Random(f"veriproof-tamper-{seed}")

def _region(rng, w, h, max_frac=0.35):
    rw = int(w * rng.uniform(0.1, max_frac)); rh = int(h * rng.uniform(0.1, max_frac))
    x = rng.randint(0, w - rw); y = rng.randint(0, h - rh)
    return x, y, rw, rh

def _mask_from_region(size, x, y, rw, rh):
    m = np.zeros((size[1], size[0]), dtype=np.uint8)
    m[y:y+rh, x:x+rw] = 1
    return m

def apply_copy_move(img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height)
    src = img.crop((x, y, x+rw, y+rh))
    x2, y2 = r.randint(0, img.width - rw), r.randint(0, img.height - rh)
    out = img.copy(); out.paste(src, (x2, y2))
    return out, _mask_from_region(img.size, x2, y2, rw, rh)

def apply_splice(img, donor_img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height)
    src = donor_img.crop((x, y, x+rw, y+rh))
    out = img.copy(); out.paste(src, (x, y))
    return out, _mask_from_region(img.size, x, y, rw, rh)

def apply_text_edit(img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height, max_frac=0.25)
    out = img.copy(); d = ImageDraw.Draw(out)
    d.rectangle([x, y, x+rw, y+rh], fill=(255, 255, 255))
    d.text((x + 5, y + 5), "edited " + str(r.randint(1000, 9999)), fill=(0, 0, 0))
    return out, _mask_from_region(img.size, x, y, rw, rh)

def apply_inpaint(img, seed):
    r = _rng(seed)
    x, y, rw, rh = _region(r, img.width, img.height)
    arr = np.asarray(img).astype(np.float32)
    patch = arr[y:y+rh, x:x+rw]
    arr[y:y+rh, x:x+rw] = patch.mean(axis=(0, 1), keepdims=True) + r.uniform(-8, 8)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return out, _mask_from_region(img.size, x, y, rw, rh)
