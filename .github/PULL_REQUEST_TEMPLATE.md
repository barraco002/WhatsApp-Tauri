## What this changes

<!-- One paragraph. What behaviour is different after this patch? -->

## Why

<!-- If it fixes an issue: Fixes #000 -->

## Checks

- [ ] `cargo fmt --check`
- [ ] `cargo clippy --all-targets -- -D warnings`
- [ ] `cargo test --all-targets`
- [ ] The release binary is still under 7 000 000 bytes (CI will tell you)

## If this touches the release profile or the measurement harness

<!-- Before/after with perf/measure.ps1, ten runs, and the spread. A change smaller than its own spread is noise. -->

| | before | after |
|---|---:|---:|
| binary | | |
| cold start (median of 10) | | |
| spread | | |
