# perf-log.md — registro crudo de mediciones

Metodología: `perf/measure.ps1` (5 tomas de arranque, mediana; idle = 60 s de muestreo cada 2 s tras 25 s de warmup;
FPS = 5 s de rAF vía DevTools Protocol). Todo sobre build **release**, mismo equipo (8 cores),
sin builds ni clippy en paralelo. Ver `PERF-PLAN.md` para los límites declarados.

## Baseline

| Fecha ISO | Commit | KPI | Valor | Unidad | Notas |
|---|---|---|---|---|---|
| 2026-10-24T09:46Z | 12ae4d2 | kpi1_exe | 12.14 | MiB | `cargo build --release`; 12 729 344 B |
| 2026-10-24T09:46Z | 12ae4d2 | kpi1_installer | 2.70 | MiB | NSIS x64-setup, 2 829 447 B |
| 2026-10-24T09:46Z | 12ae4d2 | assets_icons | 224 046 | B | `src-tauri/icons` (frontend empaquetado = icons) |
| 2026-10-24T09:45Z | 12ae4d2 | kpi3_t_window | 167.2 | ms | mediana de 5 (141.4–267.3) |
| 2026-10-24T09:45Z | 12ae4d2 | kpi3_t_cdp | 688.6 | ms | mediana de 5 (656–938), primer target CDP del webview |
| 2026-10-24T09:45Z | 12ae4d2 | kpi3_fcp | 549.0 | ms | `first-contentful-paint` de la navegación (1 toma) |
| 2026-10-24T09:45Z | 12ae4d2 | kpi3_dom_content | 570.4 | ms | `domContentLoadedEventEnd` |
| 2026-10-24T09:45Z | 12ae4d2 | kpi2_rss_total | 871.3 | MiB | mediana 60 s; árbol completo (app + WebView2) |
| 2026-10-24T09:47Z | 12ae4d2 | kpi2_rss_total | 845.9 | MiB | segunda tanda (SkipStartup), mediana 60 s |
| 2026-10-24T09:47Z | 12ae4d2 | kpi2_rss_main | 32.7 | MiB | **solo proceso nativo Rust** |
| 2026-10-24T09:47Z | 12ae4d2 | kpi2_rss_webview | 813.2 | MiB | árbol `msedgewebview2` (8 procesos) |
| 2026-10-24T09:47Z | 12ae4d2 | kpi2_procs | 8 | procs | mediana del árbol en idle |
| 2026-10-24T09:47Z | 12ae4d2 | kpi4_cpu_median | 0.98 | % | 60 s, normalizado por 8 cores |
| 2026-10-24T09:47Z | 12ae4d2 | kpi4_cpu_max | 2.68 | % | pico de una muestra de 2 s |
| 2026-10-24T09:47Z | 12ae4d2 | kpi5_fps_avg | 75.02 | fps | rAF 5 s en web.whatsapp.com |
| 2026-10-24T09:47Z | 12ae4d2 | kpi5_frame_p95 | 13.37 | ms | 0 frames > 50 ms |
| 2026-10-24T09:47Z | 12ae4d2 | kpi5_js_heap | 147.99 | MB | `JSHeapUsedSize` del webview |
| 2026-10-24T09:46Z | 12ae4d2 | kpi8_build_release | 170.3 | s | `npm run build` (tauri build, deps release recompiladas) |
| 2026-10-24T09:44Z | 12ae4d2 | kpi8_cargo_release | 10.1 | s | `cargo build --release` tras `cargo clean -p whatsapp-tauri` |

### Gate base (antes de tocar nada)

| Fecha ISO | Commit | Gate | Resultado |
|---|---|---|---|
| 2026-10-24T09:30Z | 12ae4d2 | `cargo fmt --check` | verde |
| 2026-10-24T09:31Z | 12ae4d2 | `cargo clippy --all-targets -- -D warnings` | verde |
| 2026-10-24T09:31Z | 12ae4d2 | `cargo test --all-targets` | 9/9 ok |
| 2026-10-24T09:26Z | 12ae4d2 | `npm run build` | verde (NSIS generado) |

### Nota de atribución (importante para el scoring)

El 96,1 % del RSS en idle (813 de 846 MiB) pertenece al árbol **WebView2 + WhatsApp Web**, no al binario.
El proceso nativo ocupa 32,7 MiB. Por tanto:

- El KPI 2 se evalúa sobre `kpi2_rss_total` (lo que siente el usuario) **y** sobre `kpi2_rss_main`
  (lo que controla el código). Ambas filas se registran en cada iteración.
- Ninguna afirmación de "RAM mejorada" vale si solo mueve `rss_main` un 3 % del total sin tocar el árbol.
