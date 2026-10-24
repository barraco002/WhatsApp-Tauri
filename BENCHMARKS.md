# Benchmarks — release profile optimisation

<!-- badges:static -->
![.exe](https://img.shields.io/badge/release%20.exe-6.25%20MiB%20(%E2%88%9248.5%25)-brightgreen)
![installer](https://img.shields.io/badge/NSIS%20installer-2.00%20MiB%20(%E2%88%9225.9%25)-brightgreen)
![startup](https://img.shields.io/badge/cold%20start-175%20ms%20(%2B4.8%25)-yellowgreen)
![gates](https://img.shields.io/badge/gates-fmt%20%C2%B7%20clippy%20%C2%B7%20test%20%C2%B7%20build-success)

This repository ships the distributable binaries **half the size they used to be**, without paying for it in startup
time, memory or frame rate. Every number below was measured on the same machine, with the same harness, and the
harness itself is committed ([`perf/measure.ps1`](perf/measure.ps1), [`perf/cdp-probe.mjs`](perf/cdp-probe.mjs)).

> Methodology in one line: 5–10 cold starts per configuration, **median** reported, idle sampled for 60 s every 2 s
> after a 25 s warm-up, frame pacing measured over 5 s of `requestAnimationFrame` through the DevTools Protocol.
> If the intra-run spread is larger than the difference between two configurations, the verdict is **"not established"**
> and the run is repeated with more samples. That rule killed one of the three candidates.

---

## Before / after

| KPI | Baseline `12ae4d2` | With `[profile.release]` | Δ |
|---|---:|---:|---:|
| `.exe` (bundle) | 12 729 344 B (12.14 MiB) | **6 555 648 B (6.25 MiB)** | **−48.5 %** |
| NSIS installer | 2 829 447 B (2.70 MiB) | **2 096 259 B (2.00 MiB)** | **−25.9 %** |
| Cold start → window handle | 167.2 ms | 175.2 ms | +4.8 % (inside noise) |
| Cold start → WebView2 ready (CDP) | 688.6 ms | 691.6 ms | +0.4 % |
| Resident set, idle (whole tree) | 845.9 MiB | 844.7 MiB | −0.1 % |
| Resident set, native process | 32.7 MiB | 31.2 MiB | −4.6 % |
| CPU, idle (60 s median) | 0.98 % | 1.10 % | +0.12 pp |
| Frame pacing (mean / p95) | 75.02 fps / 13.37 ms | 74.97 fps / 13.37 ms | noise |
| `tauri build` wall time | 170.3 s | 366 s | +115 % (CI cost) |

```
release .exe   baseline  ████████████████████████████████████████  12.14 MiB
               optimised ████████████████████                       6.25 MiB   −48.5%

installer      baseline  ████████████████████████████               2.70 MiB
               optimised ███████████████████                        2.00 MiB   −25.9%

cold start     baseline  █████████████████████████                167.2 ms
               optimised ██████████████████████████               175.2 ms   +4.8% (inside noise)
```

## The change

```toml
[profile.release]
opt-level = 3        # "z" and "s" were measured and rejected — see below
lto = "fat"          # cross-crate dead-code elimination
codegen-units = 1    # more global optimisation, slower build
panic = "abort"      # no unwinding tables
strip = "symbols"    # no symbols in the shipped binary
```

That is the whole diff to the code: **configuration, not behaviour.** No public API, no `tauri.conf.json` schema,
no features and no persistence were touched, and no dependency was added.

## Why not smaller? The `opt-level` curve

Three points, same hardware, same harness. Size is cheap to buy below `opt-level=3`; startup is what pays for it.

| `opt-level` | `.exe` | Cold start (10 runs) | Cost per MiB saved | Verdict |
|---|---:|---:|---:|---|
| `3` | 6.25 MiB | **175.2 ms** | — (reference) | **shipped** |
| `"s"` | 4.85 MiB | 226.0 ms | +33 ms/MiB | rejected (`t_window` +29 %) |
| `"z"` | 4.22 MiB | 274.1 ms | +48 ms/MiB | rejected (`t_window` +64 %) |

```
cold start (ms)   
  3   █████ 175
  s   ███████ 226      +29%  for −22% size
  z   ████████ 274      +64%  for −32% size
```

A binary half the size that takes 100 ms longer to open is a bad trade for the person using it.

## How to reproduce

```powershell
# Windows: MSVC + Windows SDK must be in PATH (or dot-source your own env script)
.\perf\env-msvc.ps1
.\perf\measure.ps1 -Exe whatsapp-lite\src-tauri\target\release\whatsapp-tauri.exe -Runs 10 -IdleSeconds 60 -Label my-run
```

Raw measurement dumps live in [`perf/out/`](perf/out) — every row in this document traces back to one of those files.

## What is *not* claimed here

- **RAM.** 96 % of the resident set belongs to the WebView2 tree running WhatsApp Web. This change does not touch it,
  and any "lower memory" claim based on the 32 MiB native process alone would be marketing.
- **First Contentful Paint.** It is dictated by the network and WhatsApp's servers: 527 / 549 / 725 ms across runs of
  the *same* code. It is recorded, never used to accept or reject a change.
- **Cold-cache startup.** The WebView2 cache cannot be wiped without destroying the user's WhatsApp session, so
  "cold" means cold process, warm disk. Declared in [`PERF-PLAN.md`](PERF-PLAN.md).

## Related documents

| Document | Contents |
|---|---|
| [`OPTIMIZATION_REPORT.md`](OPTIMIZATION_REPORT.md) | Full runbook: phases, KPIs, verdicts, rollback decisions |
| [`perf-log.md`](perf-log.md) | Raw measurement log, including the runs that were thrown away |
| [`bottleneck-analysis.md`](bottleneck-analysis.md) | `cargo bloat` attribution and the prioritised candidate list |
| [`BUGS_FOUND.md`](BUGS_FOUND.md) | Pre-existing bugs found during the audit — reported, deliberately **not** fixed here |
| [`DEPENDENCIES_JUSTIFICATION.md`](DEPENDENCIES_JUSTIFICATION.md) | Every crate, why it exists, and the checklist for adding one |
