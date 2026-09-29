import random

from PIL import Image, ImageDraw

RENDER_STYLE_KEYS = ("chat", "payment")

def _rng(seed):
    return random.Random(f"veriproof-render-{seed}")

def render_chat(seed: int, size=(1080, 1920)) -> Image.Image:
    r = _rng(seed)
    W, _H = size
    img = Image.new("RGB", size, (18, 140, 126))  # WhatsApp-dark teal backdrop
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 110], fill=(8, 84, 74))
    d.text((30, 35), f"Contact {r.randint(1, 999)}", fill=(255, 255, 255))
    y = 160
    for i in range(r.randint(6, 12)):
        rng2 = _rng(seed + i)
        text = " ".join("word" for _ in range(rng2.randint(2, 8)))
        mine = i % 2 == 0
        w = rng2.randint(220, 620)
        h = rng2.randint(90, 160)
        x = W - w - 40 if mine else 40
        bubble = (66, 183, 66) if mine else (37, 45, 49)
        d.rounded_rectangle([x, y, x + w, y + h], 18, fill=bubble)
        d.text((x + 20, y + 15), text[:40], fill=(255, 255, 255))
        d.text((x + w - 90, y + h - 40), f"{rng2.randint(1,12)}:{rng2.randint(0,59):02d} PM", fill=(200, 200, 200))
        if mine:
            d.text((x + w - 60, y + h - 22), "\u2713\u2713", fill=(120, 200, 255))
        y += h + 30
    return img

def render_payment(seed: int, size=(1080, 1920)) -> Image.Image:
    r = _rng(seed)
    W, _H = size
    img = Image.new("RGB", size, (245, 247, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 150], fill=(21, 101, 192))
    d.text((40, 50), "BankApp", fill=(255, 255, 255))
    card = [60, 240, W - 60, 720]
    d.rounded_rectangle(card, 24, fill=(255, 255, 255), outline=(200, 205, 210), width=2)
    d.text((110, 300), f"Rs {r.randint(5000, 900000):,}", fill=(20, 20, 20))
    d.text((110, 380), "Transfer Successful", fill=(46, 125, 50))
    d.text((110, 460), f"Ref: VRF{r.randint(10**8, 10**9)}", fill=(90, 90, 90))
    d.text((110, 520), f"{r.randint(1,28):02d} Sep 2026, {r.randint(9,20)}:{r.randint(0,59):02d}", fill=(90, 90, 90))
    d.text((110, 600), "To: Account ****" + str(r.randint(1000, 9999)), fill=(90, 90, 90))
    return img
