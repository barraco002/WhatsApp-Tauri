<img src="assets/whatsapp-tauri.svg" alt="logo" align="left" width="64" height="64">

# WhatsApp Tauri Lite

**A WhatsApp desktop client in 6 MB, not 200.** Native window, system WebView, no bundled Chromium.

[![Release](https://img.shields.io/github/v/release/barraco002/whatsapp-tauri-lite?label=download&color=brightgreen)](https://github.com/barraco002/whatsapp-tauri-lite/releases/latest)
[![Stars](https://img.shields.io/github/stars/barraco002/whatsapp-tauri-lite?style=flat&color=yellow)](https://github.com/barraco002/whatsapp-tauri-lite/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](#installation)

```
Electron WhatsApp wrapper   ████████████████████████████████████████  ~200 MB
Discord                     ███████████████████████████████████████  ~180 MB
This app                    ████                                       6.25 MB
```

---

## Why this exists

Most WhatsApp desktop wrappers ship an entire Chromium build to render one web page. That is 180–200 MB of disk and
hundreds of megabytes of RAM for a chat window.

This one uses **Tauri v2** and the WebView your operating system already has (WebView2 on Windows, WebKitGTK on
Linux). The installer is **2.0 MB**. The binary is **6.25 MB**. Cold start is **~175 ms** to a visible window.

It is also the only build of this app where the release profile was tuned with measurements instead of vibes —
`[profile.release]` with fat LTO and `codegen-units = 1` cut the binary **48.5 %** with no measurable cost in startup,
memory or frame pacing. Every number, including the two variants that were rejected, is in [BENCHMARKS.md](BENCHMARKS.md).

## Features

- Native window and tray — no Chromium, no Electron runtime
- Global shortcut `Ctrl + Alt + W` to show/hide
- Optional auto-start with the system
- Native dark title bar and menus on Windows
- Downloads with sanitised filenames (reserved Windows names, duplicate handling)
- Deep links (`whatsapp://`), single-instance lock, native notifications
- Windows `.exe` installer and Linux `.deb` / `.AppImage`

## Installation

### Windows

1. Grab the installer from [**Releases**](https://github.com/barraco002/whatsapp-tauri-lite/releases/latest)
2. Run `whatsapp-tauri-lite_0.3.3_x64-setup.exe`
3. The app registers itself for the current user — no admin prompt

### Linux

```bash
sudo dpkg -i whatsapp-tauri-lite_0.3.3_amd64.deb
# or
chmod +x WhatsApp_Tauri_0.3.3_amd64.AppImage && ./WhatsApp_Tauri_0.3.3_amd64.AppImage
```

## Numbers (measured, not estimated)

| | value |
|---|---:|
| Installer (NSIS) | **2.00 MiB** |
| Binary | **6.25 MiB** |
| Cold start → window visible | **175 ms** (median of 10) |
| Cold start → WebView ready | 692 ms |
| Idle RSS (incl. WebView2) | 845 MiB |
| Idle CPU | ~1 % |
| Frame pacing | 75 fps, p95 13.4 ms |

Same machine, same harness, raw dumps committed in [`perf/out/`](perf/out). Reproduce with `perf/measure.ps1`.
The honest caveats (network-bound FCP, WebView2 dominating RSS, warm disk cache) are written down in [BENCHMARKS.md](BENCHMARKS.md#what-is-not-claimed-here).

## Building from source

Requirements: Rust + Cargo, Node.js, and on Windows the MSVC build tools & Windows SDK; on Linux WebKit2GTK.

```bash
git clone https://github.com/barraco002/whatsapp-tauri-lite.git
cd whatsapp-tauri-lite/whatsapp-lite
npm install
npm run tauri dev      # development
npm run tauri build    # release binaries + installer
```

## Project structure

```
whatsapp-lite/            # the Tauri app
  src-tauri/src/main.rs   # window, menus, downloads, deep links, tray
  src-tauri/Cargo.toml    # deps + the tuned [profile.release]
perf/                     # measurement harness and raw evidence
BENCHMARKS.md             # what changed and what it cost
OPTIMIZATION_REPORT.md    # full audit: phases, KPIs, rejected variants
BUGS_FOUND.md             # pre-existing bugs, documented not fixed
```

## Credits and licence

MIT. Based on [Wpnnt/WhatsApp-Tauri](https://github.com/Wpnnt/WhatsApp-Tauri) — all credit for the original client
goes to its author. This fork adds the release-profile work, the measurement harness, hardening fixes from a source
audit, and a CI guard that fails any PR pushing the binary past 7 MB.

Not affiliated with WhatsApp or Meta. Unofficial client, use at your own risk.

---

If this saved you 200 MB of disk, a star costs you nothing and helps other people find it.