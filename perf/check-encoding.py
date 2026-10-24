
import io
p = r"D:\dev\whatsapp-tauri\CHANGELOG.md"
b = open(p, "rb").read()
print("bytes", len(b), "BOM", b[:3] == b"\xef\xbb\xbf")
try:
    s = b.decode("utf-8")
    print("utf8_strict OK chars", len(s))
except UnicodeDecodeError as e:
    print("utf8 FAIL", e)
print("has en-dash", s.count("\u2013"), "has mojibake seq", s.count("\u00e2\u20ac"))
i = s.find("\u2013")
print("context:", repr(s[max(0, i-60):i+20]) if i >= 0 else "none")
