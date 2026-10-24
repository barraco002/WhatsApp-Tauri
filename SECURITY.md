# Security policy

## What this project is (and is not)

This is a thin native window around `https://web.whatsapp.com`. It does not implement the WhatsApp protocol, it does not
hold your messages, and it does not proxy anything: the page you see is served by WhatsApp and rendered by the WebView2
runtime that ships with Windows. Message encryption is WhatsApp's, end to end, and untouched by this project.

That shapes what a vulnerability here can actually be:

| In scope | Out of scope |
|---|---|
| Navigation escapes (letting the WebView reach a host that is not an approved WhatsApp origin) | Anything inside `web.whatsapp.com` itself - report it to Meta |
| Deep-link parsing that could launch an unintended URL or executable | Vulnerabilities in WebView2 or Tauri - report them upstream |
| Download path handling (traversal, overwriting files, reserved Windows names) | Your WhatsApp account being compromised by someone with your phone |
| Local privilege issues in the installer or the auto-start entry | The app reading your chat database - it never opens it |

## Reporting

Open a [private security advisory](https://github.com/barraco002/whatsapp-tauri-lite/security/advisories/new) instead of a
public issue. Include the version (`Settings` shows it, or the installer filename), what you did, and what happened.

Expect an answer within a few days. There is no bug bounty: this is a single-person project with no funding, and saying
so is more honest than pretending otherwise.

## What you can check yourself

The navigation allowlist and the download sanitizer are the two surfaces that matter, and both have unit tests:

```powershell
cd whatsapp-lite\src-tauri
cargo test --all-targets
```

Nine tests cover host validation, deep-link parsing, path writability, reserved Windows names, duplicate handling and
simultaneous reservations. If you find a case they miss, that is a useful issue even without an exploit.
