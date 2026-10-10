"""Side-by-side sheet: shipped gpt-image-1.5 master (left) vs gpt-image-2 probe (right).
Usage: python _proto/compare_sheet.py   -> _proto/gpt-image-2/compare_sheet.jpg"""
import os
from PIL import Image, ImageDraw, ImageFont
P = "_proto/gpt-image-2"
keys = sorted(f[:-4] for f in os.listdir(P) if f.endswith(".png"))
W, H, LBL, GAP = 768, 512, 34, 12
sheet = Image.new("RGB", (2 * W + 3 * GAP, len(keys) * (H + LBL + GAP) + LBL + GAP), "white")
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
except OSError:
    font = ImageFont.load_default()
d.text((GAP, 6), "gpt-image-1.5 (shipped)", fill="black", font=font)
d.text((2 * GAP + W, 6), "gpt-image-2 (probe, same prompt)", fill="black", font=font)
y = LBL + GAP
for k in keys:
    d.text((GAP, y + 4), k, fill="black", font=font)
    for i, path in enumerate((f"out_deck/{k}.png", f"{P}/{k}.png")):
        if os.path.exists(path):
            im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
            sheet.paste(im, (GAP + i * (W + GAP), y + LBL))
    y += H + LBL + GAP
sheet.save(f"{P}/compare_sheet.jpg", quality=85)
print(f"{len(keys)} pairs -> {P}/compare_sheet.jpg")
