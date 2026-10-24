# OPTIMIZATION_REPORT.md — Optimización extrema de una app Tauri

**Proyecto:** `whatsapp-tauri` v0.3.3 (Tauri v2 + WebView2, carga `https://web.whatsapp.com`)
**Repositorio:** `D:\dev\whatsapp-tauri` · **Ejecutor:** dsh (runbook auditable, fases, KPIs, rollback)
**Fecha de cierre:** 2026-10-24 (America/Lima) · **Baseline:** commit `12ae4d2` · **Punta tras la iteración 1:** `467f7f5`

---

## 1. Resumen ejecutivo

| KPI | Baseline | Tras la iteración 1 | Δ | Estado |
|---|---|---|---|---|
| Binario `.exe` (release) | 12 729 344 B (12.14 MiB) | 6 555 648 B (6.25 MiB) | **−48.5 %** | mejora medida |
| Instalador NSIS | 2 829 447 B (2.70 MiB) | 2 096 343 B (2.00 MiB) | **−25.9 %** | mejora medida |
| Arranque: ventana nativa (`t_window`) | 167.2 ms | 175.2 ms (10 tomas) | +4.8 % | dentro de la incertidumbre |
| Arranque: webview listo (`t_cdp`) | 688.6 ms | 691.6 ms | +0.4 % | neutro |
| RAM en idle (árbol completo) | 845.9 MiB | 844.7 MiB | −0.1 % | neutro |
| RAM proceso nativo | 32.7 MiB | 31.2 MiB | −4.6 % | neutro |
| CPU en idle (mediana 60 s) | 0.98 % | 1.10 % | +0.12 pp | dentro de la incertidumbre |
| Fluidez (rAF medio) | 75.02 fps | 74.97 fps | −0.1 % | neutro |
| Tiempo de build release | 170.3 s | 366 s | +115 % | coste de CI, no de usuario |

**Veredicto:** se aceptó **un** cambio (perfil de compilación de release, variante `opt-level=3`). Reduce el
peso distribuible a la mitad sin coste medible en arranque, memoria ni fluidez. Dos candidatos más del catálogo
se prepararon y **no** se ejecutaron: el presupuesto de la sesión se agotó antes (ver §7).

---

## 2. Contexto del proyecto (lo que el runbook exige declarar)

| Campo | Valor |
|---|---|
| Framework | Tauri v2 (`tauri = { version = "2", features = ["tray-icon", "unstable"] }`) |
| Motor de render | WebView2 (Chromium) sobre Windows 10 Pro 19045 |
| Frontend | **Ninguno propio.** `frontendDist = "icons"`; la UI es WhatsApp Web remoto |
| Plugins (7) | opener, notification, autostart, global-shortcut, deep-link, single-instance, dialog |
| Comandos `invoke` | **Ninguno** (no hay `#[tauri::command]` ni `invoke_handler`) |
| Persistencia | Archivos JSON/ajustes del sistema (autostart, deep-link, descargas) |
| Toolchain | Rust 1.99.1 MSVC, Node 24.20.0, npm 11.19.0 |
| Hardware de medida | 8 cores, mismo equipo para todas las tomas |

Consecuencia metodológica: los KPI "latencia de `invoke`" y "tamaño del bundle JS" del catálogo del runbook
**no existen estructuralmente** en esta app. Se sustituyeron por equivalentes declarados en `PERF-PLAN.md`
(assets empaquetados y métricas de WebView2). No se inventó ninguna cifra para rellenar un KPI vacío.

---

## 3. Metodología

- `perf/measure.ps1`: mide artefactos y arranque en frío (5 tomas por defecto, **mediana**), ventana nativa
  por sondeo de `MainWindowHandle` cada 20 ms y webview por `/json/list` del puerto CDP cada 50 ms.
  Idle = 60 s de muestreo cada 2 s tras 25 s de warmup. FPS = 5 s de `requestAnimationFrame` vía
  `Runtime.evaluate`, métricas V8 vía `Performance.getMetrics`.
- `perf/cdp-probe.mjs`: sonda con *deadline* duro y tiempo límite por RPC (una sonda colgada invalidó una
  tanda anterior; se corrigió la herramienta, no se maquilló el dato).
- Regla de decisión aplicada: **tres tomas como mínimo; si la dispersión intra-tanda supera la diferencia
  entre configuraciones, el veredicto es "no establecido"** (lección L-0008 del workspace).
- Una idea por rama. Nada de mediciones con builds o clippy corriendo en paralelo.

---

## 4. Baseline (commit `12ae4d2`)

| Métrica | Valor |
|---|---|
| `.exe` release | 12 729 344 B |
| Instalador NSIS | 2 829 447 B |
| `t_window` (mediana 5) | 167.2 ms (141.4 – 267.3) |
| `t_cdp` (mediana 5) | 688.6 ms |
| FCP / DOMContentLoaded | 549.0 / 570.4 ms |
| RSS total (main / webview) | 845.9 MiB (32.7 / 813.2), 8 procesos |
| CPU idle (mediana / máx) | 0.98 % / 2.68 % |
| rAF medio / p95 | 75.02 fps / 13.37 ms (0 frames > 50 ms) |
| JS heap | 148 MB |
| Build release | 170.3 s |
| Gates | `fmt` verde, `clippy -D warnings` verde, `test` 9/9 |

**Atribución honesta:** el 96.1 % del RSS es el árbol WebView2 + WhatsApp Web. El binario Rust son 32.7 MiB.
Cualquier afirmación de "RAM mejorada" que solo mueva el proceso nativo un 3 % sería propaganda, y no se hace.

---

## 5. Iteración 1 — perfil de release (`perf/release-profile`)

### 5.1 Variante A — `opt-level = "z"` → **rollback**

Bloque aplicado: `lto="fat"`, `codegen-units=1`, `panic="abort"`, `strip="symbols"`, `opt-level="z"`.

| KPI | Baseline | Variante A | Δ |
|---|---|---|---|
| `.exe` | 12.14 MiB | 4.22 MiB | −65.2 % |
| Instalador | 2.70 MiB | 1.56 MiB | −42.2 % |
| `t_window` | 167.2 ms | **274.1 ms** | **+64.0 %** |
| `t_cdp` | 688.6 ms | 784.8 ms | +13.9 % |

Regla §6 del runbook: un KPI crítico que empeora más del 10 % obliga a descartar el cambio. Un `.exe` la mitad
de pequeño que tarda 107 ms más en mostrar la ventana es un mal negocio para el usuario. **Descartada sin
negociar**, no "compensada" con el argumento del tamaño.

### 5.2 Variante B — `opt-level = 3` → **aceptada**

```toml
# Perfil de release para distribución (iteración perf/release-profile).
[profile.release]
opt-level = 3        # variante "z" medida y descartada: t_window +64%; ver perf-log.md
lto = "fat"
codegen-units = 1
panic = "abort"
strip = "symbols"
```

| KPI | Baseline | Variante B | Δ | Lectura |
|---|---|---|---|---|
| `.exe` | 12 729 344 B | 6 555 648 B | **−48.5 %** | determinista |
| Instalador | 2 829 447 B | 2 096 343 B | **−25.9 %** | determinista |
| `t_window` | 167.2 ms | 175.2 ms (10 tomas) | +4.8 % | < umbral 10 %; ver 5.3 |
| `t_cdp` | 688.6 ms | 691.6 ms | +0.4 % | neutro |
| RSS total / nativo | 845.9 / 32.7 MiB | 844.7 / 31.2 MiB | −0.1 % / −4.6 % | neutro |
| CPU idle | 0.98 % | 1.10 % | +0.12 pp | neutro |
| rAF medio / p95 | 75.02 / 13.37 ms | 74.97 / 13.37 ms | −0.1 % / 0 % | neutro |
| Build release | 170.3 s | 366 s | +115 % | coste de CI |

### 5.3 Por qué se repitió la medición de arranque

La primera tanda (5 tomas) dio `t_window` = 201.5 ms y se leía como regresión del +20 %. La dispersión
intra-tanda era 151–284 ms: **mayor que la diferencia que se pretendía detectar**. Con esa relación
señal/ruido el veredicto correcto es "no establecido", no "regresión" ni "mejora". Se repitió con 10 tomas →
175.2 ms. Se documentan ambas tandas y el criterio; no se elige la que conviene.

### 5.4 Efectos secundarios conocidos y aceptados

1. **Build más lento** (170 → 366 s) por `lto="fat"` + `codegen-units=1`. Afecta a la CI y al desarrollador,
   no al usuario. `lto="thin"` no se midió: queda como candidato (probablemente recupere la mitad del coste
   con casi el mismo tamaño).
2. **`panic = "abort"`** elimina el `unwind`. Ningún `catch_unwind` en el código; los 9 tests pasan igual.
3. **`strip = "symbols"`** deja los binarios sin símbolos: los *crash dumps* de campo serán menos legibles.
   Es el precio habitual de distribuir; si se quiere diagnóstico, mantener una build aparte sin `strip`.

---

## 6. Verificación (gates §3 del runbook)

| Gate | Resultado |
|---|---|
| `cargo fmt --check` | verde |
| `cargo clippy --all-targets -- -D warnings` | verde |
| `cargo test --all-targets` | 9/9 ok |
| `npm run build` (`tauri build`) | verde — NSIS 2 096 343 B |

Contrato de compatibilidad respetado: no se tocó la API pública, ni `tauri.conf.json` (esquema intacto), ni la
persistencia, ni se añadió ninguna dependencia. El cambio es **solo** configuración de compilación.

---

## 7. Candidatos preparados y no ejecutados (con motivo)

| Candidato | Evidencia que lo respalda | Por qué no se ejecutó |
|---|---|---|
| `hidden-until-ready` (ventana oculta hasta el primer *paint*) | `t_cdp` 691 ms ⇒ ~0.7 s de pantalla en blanco | Requiere cambiar el orden de `setup` y validar el *flash* visual, que la sonda actual no mide: haría falta un KPI de primer pintado **visible** |
| `menu-cache` (cachear las 3 lecturas de disco de `build_native_menu`) | `main.rs:288`, llamado en `setup` (526) y en **cada** evento de menú (579-581) | Toca el mismo código que el bug B-02 (doble reconstrucción). Arreglarlo sería arreglar un bug, y §0 lo prohíbe en este runbook |
| `webview2-flags` (`--disable-features`, `--js-flags`) | `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` ya se usa para CDP | Todo su efecto cae en el territorio de WhatsApp Web (RSS, FCP), dominado por la red; sin un KPI aislable el resultado sería "no establecido" por diseño |
| `no-blocking-sleep` | `main.rs:513-524`: `thread::sleep(1500 ms)` dentro de `spawn` | Es el bug **B-01**, no una optimización. Registrado en `BUGS_FOUND.md`; tocarlo aquí violaría §0 |
| `trim-unused-features` | `infer` 33.6 KiB en `.text` pese a `disable_drag_drop_handler()` | Cambia features: requiere aprobación explícita (§3) y no había presupuesto para medirla |
| `split-setup-closure` | closure `setup` = 1.0 MiB (12.2 % del `.text`) | Reestructuración grande, no medible en una sola iteración pequeña |

**Stop condition citada (§7 del runbook):** "el presupuesto de la sesión se agota antes de completar el
catálogo" — se detiene la fase de iteración con **una** optimización aceptada, sus gates en verde y la lista de
candidatos priorizada arriba, en vez de abrir cambios a medias que no se puedan verificar.

---

## 8. Bugs preexistentes encontrados (registrados, **no** arreglados — §0)

Detalle completo en `BUGS_FOUND.md`:

- **B-01** `thread::sleep(1500 ms)` dentro de `tauri::async_runtime::spawn` (`main.rs:513-524`): bloquea un
  hilo del pool de Tokio en cada arranque.
- **B-02** `build_native_menu` se reconstruye **dos veces** por evento de menú y hace 3 lecturas de disco cada
  vez (`main.rs:288`, `526`, `565-581`).
- **B-03** El crate `infer` se compila aunque el *drag & drop* está deshabilitado (33.6 KiB de `.text`).

---

## 9. Comandos git/gh — **impresos, NO ejecutados** (§9 del runbook)

```bash
# Estado real del repositorio local tras este trabajo
git -C D:/dev/whatsapp-tauri log --oneline --graph 12ae4d2..main
git -C D:/dev/whatsapp-tauri diff --stat 12ae4d2..main

# Publicación (NO ejecutar sin decisión explícita; este runbook prohíbe push)
git -C D:/dev/whatsapp-tauri push origin main
git -C D:/dev/whatsapp-tauri push origin perf/release-profile

# Etiqueta de la medición
git -C D:/dev/whatsapp-tauri tag -a perf-baseline-2026-10-24 12ae4d2 -m "baseline medido (12.14 MiB, t_window 167.2 ms)"

# Pull request con la evidencia
gh pr create --base main --head perf/release-profile \
  --title "perf(build): perfil de release LTO fat — .exe -48.5%" \
  --body "Ver OPTIMIZATION_REPORT.md y perf-log.md. KPI1 -48.5%, KPI3 +4.8% (dentro de incertidumbre), gates verdes."
```

Ninguno de estos comandos se ha ejecutado. No hay nada publicado en ningún remoto.

---

## 10. Límites declarados de este informe

1. **Medido en un solo equipo** (8 cores, Windows 10 19045). Los valores absolutos de arranque y RSS no son
   extrapolables a otro hardware; las **direcciones** de las mejoras sí.
2. **FCP no es concluyente**: 527 / 549 / 725 ms entre tandas con el mismo código de aplicación. Lo dicta la
   red y el servidor de WhatsApp. No se usa para aceptar ni rechazar nada.
3. **No se puede vaciar la caché de WebView2** sin destruir la sesión de WhatsApp del usuario; por tanto el
   "arranque en frío" es frío en proceso, tibio en disco. Está declarado en `PERF-PLAN.md`.
4. **La pantalla medida es la de arranque** (QR o lista de chats), no una conversación con medios pesados.
5. El tamaño del `.exe` sí es determinista y reproducible: es la cifra más sólida de todo el informe.

---

## 11. Autochequeo final (§12 del runbook)

| Punto | Estado |
|---|---|
| ¿Se midió antes de optimizar? | Sí — baseline completo en `perf-log.md` antes de tocar `Cargo.toml` |
| ¿Una idea por iteración? | Sí — solo el perfil de release |
| ¿Rollback sin piedad cuando un KPI empeoró? | Sí — variante `opt-level="z"` descartada (+64 % en `t_window`) |
| ¿Se registraron los bugs sin arreglarlos? | Sí — B-01, B-02, B-03 en `BUGS_FOUND.md` |
| ¿API pública, `tauri.conf.json`, features y persistencia intactas? | Sí — el diff es configuración de compilación |
| ¿Dependencias nuevas? | Ninguna |
| ¿Gates en verde? | `fmt`, `clippy -D warnings`, `test` 9/9, `npm run build` |
| ¿Se hizo push? | **No.** Comandos impresos en §9, no ejecutados |
| ¿Cada afirmación tiene una cifra detrás? | Sí, con la incertidumbre declarada (§5.3, §10) |
| ¿Entregables completos? | `OPTIMIZATION_REPORT.md`, `perf-log.md`, `bottleneck-analysis.md`, `BUGS_FOUND.md`, `DEPENDENCIES_JUSTIFICATION.md`, `PERF-PLAN.md`, `perf/out/*.json` |

---

*Fin del informe. Los datos crudos que lo respaldan están en `perf/out/` y se pueden reproducir con
`perf/measure.ps1` tras dot-sourcear `perf/env-msvc.ps1`.*
