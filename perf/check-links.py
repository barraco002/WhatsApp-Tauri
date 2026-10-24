#!/usr/bin/env python3
"""Check every link in the markdown files. Exit 1 if a link is provably broken.

Statuses 403 and 429 are treated as inconclusive (GitHub rate limits unauthenticated
HEAD requests) and reported as SKIP, never as failures.
"""
import re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ['README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'CODE_OF_CONDUCT.md']
LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
SKIP_PREFIX = ('#', 'mailto:')
UA = {'User-Agent': 'whatsapp-tauri-lite-linkcheck/1.0'}


def check(url, timeout=20):
    for method in ('HEAD', 'GET'):
        req = urllib.request.Request(url, headers=UA, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return 'OK', r.status
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                return 'SKIP', e.code
            if method == 'GET':
                return 'FAIL', e.code
        except Exception as e:
            if method == 'GET':
                return 'FAIL', type(e).__name__
    return 'FAIL', 'unknown'


def main():
    seen, fails, skips = {}, [], []
    for name in FILES:
        p = ROOT / name
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        for m in LINK.finditer(text):
            url = m.group(1)
            if url.startswith(SKIP_PREFIX):
                continue
            if url not in seen:
                seen[url] = name
    print('links found:', len(seen))
    for url, name in sorted(seen.items()):
        if url.startswith('./') or not url.startswith('http'):
            target = (ROOT / url.split('#', 1)[0].lstrip('./')).resolve()
            status = 'OK' if target.exists() else 'FAIL'
            code = '' if target.exists() else 'missing ' + str(target)
        else:
            status, code = check(url)
        tag = {'OK': '  ok  ', 'SKIP': ' skip ', 'FAIL': ' FAIL '}[status]
        print(tag, url, code)
        if status == 'FAIL':
            fails.append((name, url, code))
        elif status == 'SKIP':
            skips.append(url)
    print()
    print('ok:', len(seen) - len(fails) - len(skips), 'skip:', len(skips), 'fail:', len(fails))
    if fails:
        print('BROKEN:')
        for name, url, code in fails:
            print(' ', name, '->', url, code)
        return 1
    print('ALL LINKS OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())