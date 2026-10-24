# Contributing

Small project, one maintainer, no funding. That means the useful contribution is a precise report or a small patch,
not a large refactor. Here is what gets merged quickly.

## Before you write code

Open an issue first if the change touches the window, the menus, the tray or the download path. Those four things are
where the app's behaviour actually lives, and a surprise rewrite of any of them is hard to review.

## The build

```bash
cd whatsapp-lite
npm install
npm run tauri dev
```

Windows needs the MSVC build tools and the Windows SDK; Linux needs WebKit2GTK (`libwebkit2gtk-4.1-dev` and friends).
The toolchain is plain stable Rust - no nightly features anywhere.

## The gates

Every PR runs these on Ubuntu and they are the same commands you can run locally:

```bash
cd whatsapp-lite/src-tauri
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test --all-targets
```

Nine tests today, all on the parts where a mistake is dangerous: host allowlisting, deep-link parsing, download path
writability, reserved Windows filenames, duplicate and simultaneous reservations. A patch that changes one of those
paths without a test is not ready.

## The size budget

`perf-guard.yml` fails any PR whose release binary passes **7 000 000 bytes**. The current binary is 6 555 648 B, so
there is about 450 KB of headroom. This is deliberate: the whole point of the project is that it is small, and a
dependency that adds 2 MB is a product decision, not a detail. If your change needs more room, say why in the PR and
bring a measurement.

## Changes to the release profile

`[profile.release]` in `whatsapp-lite/src-tauri/Cargo.toml` is the result of measurements, and the two variants that
were rejected (`opt-level = "s"` and `"z"`) are still in the repository as branches. If you want to change it, bring a
before/after with `perf/measure.ps1` on both sides, ten runs, and the spread. A change that is smaller than its own
spread is not a win, it is noise - that rule has already cost this project one false conclusion.

## Reporting a bug worth fixing

Useful:

- the exact version (the installer filename has it, or `Settings` inside the app)
- Windows version, and whether WebView2 is the one shipped with the OS
- what you did, what you expected, what happened
- for a download bug: the original filename you were downloading

Not useful: "it does not work". There is nothing to reproduce there.

## What will be declined

- Bundling a Chromium or a JavaScript framework. The point is the system WebView.
- Adding telemetry, analytics or crash reporting with a remote endpoint.
- Re-adding an installer prompt for admin rights: it installs per-user on purpose.
- Anything that grows the binary past the budget without a measurement.

## Licence

MIT. By sending a patch you agree it ships under the same licence.