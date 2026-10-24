
import sys
try:
    import yaml
except ImportError:
    print("no pyyaml")
    sys.exit(7)
base = r"D:\dev\whatsapp-tauri\.github"
files = [base + r"\ISSUE_TEMPLATE\bug.yml", base + r"\ISSUE_TEMPLATE\feature.yml", base + r"\ISSUE_TEMPLATE\config.yml",
         base + r"\workflows\perf-guard.yml", base + r"\workflows\release.yml"]
for f in files:
    try:
        d = yaml.safe_load(open(f, encoding="utf-8"))
        top = list(d.keys()) if isinstance(d, dict) else type(d).__name__
        print("OK  ", f.split("github\\")[-1], "->", top)
    except Exception as e:
        print("FAIL", f, e)
