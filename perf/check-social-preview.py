
from PIL import Image, ImageDraw, ImageFont
fb = r"C:\Windows\Fonts\segoeuib.ttf"
fr = r"C:\Windows\Fonts\segoeui.ttf"
fs = r"C:\Windows\Fonts\seguisb.ttf"
img = Image.open(r"D:\dev\whatsapp-tauri\assets\social-preview.png")
W, H = img.size
d = ImageDraw.Draw(img)
def f(p, s): return ImageFont.truetype(p, s)
items = [
  ("title", "WhatsApp Tauri Lite", fb, 52, 216, 84),
  ("sub", "The desktop client that is not an Electron app.", fr, 27, 218, 146),
  ("pill", "Tauri v2  +  WebView2  -  MIT", fs, 19, 235, 205),
  ("stat0", "6.25", fb, 68, 110, 334),
  ("stat1", "2.00", fb, 68, 480, 334),
  ("stat2", "175", fb, 68, 850, 334),
  ("foot1", "-48.5% binary vs the previous release profile", fs, 21, 80, 528),
  ("foot2", "github.com/barraco002/whatsapp-tauri-lite", fr, 20, 80, 566),
]
ok = True
for name, text, font, size, x, y in items:
    w = d.textlength(text, font=f(font, size))
    right = x + w
    inside = right <= W - 40
    print(f"{name:6s} x={x:4d} w={w:6.1f} right={right:7.1f} inside={inside}")
    ok = ok and inside
print("size", img.size, "mode", img.mode)
print("cards right edge", 80 + 3*348 + 2*22, "<= 1240:", 80 + 3*348 + 2*22 <= 1240)
print("ALL_INSIDE", ok)
