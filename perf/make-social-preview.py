
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = r"D:\dev\whatsapp-tauri\assets\social-preview.png"
ICON = r"D:\dev\whatsapp-tauri\whatsapp-lite\src-tauri\icons\icon.png"
W, H = 1280, 640

BG_TOP = (11, 20, 26)
BG_BOT = (17, 27, 33)
GREEN = (37, 211, 102)
DIM = (134, 150, 160)
WHITE = (240, 246, 248)
CARD = (24, 37, 45)
EDGE = (42, 60, 70)

base = Image.new("RGB", (W, H), BG_TOP)
d = ImageDraw.Draw(base)
for y in range(H):
    t = y / (H - 1)
    d.line([(0, y), (W, y)], fill=(
        int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t),
        int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t),
        int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)))

# glow verde suave arriba a la izquierda
glow = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-260, -320, 620, 300], fill=(14, 70, 40))
glow = glow.filter(ImageFilter.GaussianBlur(120))
base = Image.blend(base, Image.blend(base, glow, 0.55), 1.0)
d = ImageDraw.Draw(base)

def font(path, size):
    return ImageFont.truetype(path, size)

fb = r"C:\Windows\Fonts\segoeuib.ttf"
fr = r"C:\Windows\Fonts\segoeui.ttf"
fs = r"C:\Windows\Fonts\seguisb.ttf"

# icono
icon = Image.open(ICON).convert("RGBA").resize((112, 112), Image.LANCZOS)
mask = Image.new("L", (112, 112), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, 111, 111], radius=26, fill=255)
base.paste(icon, (80, 64), mask)

d.text((216, 84), "WhatsApp Tauri Lite", font=font(fb, 52), fill=WHITE)
d.text((218, 146), "The desktop client that is not an Electron app.", font=font(fr, 27), fill=DIM)

# pastilla
px, py = 218, 196
label = "Tauri v2  +  WebView2  -  MIT"
fw = d.textlength(label, font=font(fs, 19))
d.rounded_rectangle([px, py, px + fw + 34, py + 38], radius=19, fill=(22, 44, 34), outline=(31, 74, 52))
d.text((px + 17, py + 9), label, font=font(fs, 19), fill=(140, 220, 170))

# tarjetas
stats = [("6.25", "MiB", "binary"), ("2.00", "MiB", "installer"), ("175", "ms", "cold start")]
cw, ch, gap = 348, 176, 22
x0, y0 = 80, 300
for i, (num, unit, cap) in enumerate(stats):
    x = x0 + i * (cw + gap)
    d.rounded_rectangle([x, y0, x + cw, y0 + ch], radius=20, fill=CARD, outline=EDGE)
    d.rounded_rectangle([x, y0, x + 5, y0 + ch], radius=3, fill=GREEN)
    d.text((x + 30, y0 + 34), num, font=font(fb, 68), fill=WHITE)
    nw = d.textlength(num, font=font(fb, 68))
    d.text((x + 34 + nw, y0 + 64), unit, font=font(fs, 30), fill=GREEN)
    d.text((x + 32, y0 + 126), cap, font=font(fr, 24), fill=DIM)

# pie
d.text((80, 528), "-48.5% binary vs the previous release profile", font=font(fs, 21), fill=(150, 168, 178))
d.text((80, 566), "github.com/barraco002/whatsapp-tauri-lite", font=font(fr, 20), fill=(96, 112, 122))

base.save(OUT, "PNG", optimize=True)
print("saved", OUT, os.path.getsize(OUT), "bytes", base.size)
