# DEPENDENCIES_JUSTIFICATION.md

Registro de dependencias del proyecto `whatsapp-tauri` v0.3.3 y de la regla aplicada durante el runbook
de optimización: **ninguna dependencia nueva**. Este documento existe para que cualquier adición futura tenga
que justificarse aquí, con coste medido y alternativa considerada.

---

## 1. Regla aplicada (§3 del runbook)

> "Prohibido añadir dependencias nuevas."

Estado: **cumplida**. La iteración aceptada (`perf/release-profile`) no toca `[dependencies]` ni
`[build-dependencies]`: solo añade un bloque `[profile.release]` a `src-tauri/Cargo.toml`.

Verificación:

```bash
git -C D:/dev/whatsapp-tauri diff 12ae4d2..main -- whatsapp-lite/src-tauri/Cargo.toml
# Solo aparece el bloque [profile.release]; ninguna línea en [dependencies]/[dev-dependencies].
```

---

## 2. Dependencias actuales y por qué están

| Crate / paquete | Versión | Para qué | ¿Se podría quitar? |
|---|---|---|---|
| `tauri` | 2 (features `tray-icon`, `unstable`) | Núcleo del framework: ventana, webview, bandeja | No |
| `tauri-plugin-opener` | 2 | Abrir enlaces externos en el navegador del sistema | No (feature visible) |
| `tauri-plugin-notification` | 2.3.3 | Notificaciones nativas | No (feature visible) |
| `tauri-plugin-autostart` | 2.5.1 | Arranque con el sistema | No (feature visible) |
| `tauri-plugin-global-shortcut` | 2.3.1 | Atajo global para mostrar/ocultar | No (feature visible) |
| `tauri-plugin-deep-link` | 2 | Enlaces `whatsapp-tauri://` | No (feature visible) |
| `tauri-plugin-single-instance` | 2 | Evita dos instancias | No (corrección funcional) |
| `tauri-plugin-dialog` | 2 | Diálogos nativos | No (feature visible) |
| `serde` / `serde_json` | 1 | Persistencia de ajustes (JSON) | No |
| `@tauri-apps/cli` (dev) | ^2 | `tauri dev` / `tauri build` | No |
| `@tauri-apps/api` | — | **Ausente** | — |

No hay dependencias de JavaScript en tiempo de ejecución: no hay bundler ni framework de frontend
(`frontendDist = "icons"`). El `package.json` solo declara la CLI como `devDependency`.

---

## 3. Dependencias transitivas relevantes para el tamaño

Del análisis `cargo bloat` (`perf/bloat-crates.txt`, baseline `12ae4d2`), sobre 8.3 MiB de `.text`:

| Crate | Tamaño | Comentario |
|---|---|---|
| `tauri` | 2.2 MiB (26.1 %) | Inherente al framework |
| `std` | 1.4 MiB | Inherente al lenguaje |
| `whatsapp_tauri` | 1.1 MiB | Código propio (closure `setup` = 1.0 MiB) |
| `tokio` | 790.7 KiB | Runtime de `tauri` |
| `regex_automata` + `regex_syntax` + `aho_corasick` | 739.2 KiB | Transitivas de Tauri (router/patrones de URL) |
| `serde_json` | 251.6 KiB | Persistencia de ajustes |
| `urlpattern` | 172.3 KiB | Transitiva de Tauri (navegación remota) |
| `infer` | 33.6 KiB | **Candidata a desaparecer**: detecta tipos MIME en *drag & drop*, que está deshabilitado (`disable_drag_drop_handler()`). Registrada como B-03 en `BUGS_FOUND.md`. Quitarla cambiaría features ⇒ requiere aprobación explícita |

---

## 4. Si en el futuro se propone una dependencia nueva

Checklist obligatoria antes de aceptarla:

1. **Coste medido**: bytes añadidos al `.exe` release (`cargo bloat` antes/después) y al instalador NSIS.
2. **Alternativa sin dependencia**: ¿se resuelve con `std` o con lo ya presente? Escribir por qué no.
3. **Superficie de riesgo**: nueva superficie de ataque, licencia compatible, mantenimiento activo.
4. **Efecto en KPI**: si toca el camino de arranque, medir `t_window`/`t_cdp` con `perf/measure.ps1`
   (mínimo 5 tomas, mediana) y anotar la fila en `perf-log.md`.
5. **Registro aquí** con la fila correspondiente y el veredicto.

Sin los cinco puntos, la dependencia no entra.

---

## 5. Dependencias de *herramientas* usadas para medir (no del producto)

| Herramienta | Uso | ¿Se distribuye? |
|---|---|---|
| `cargo-bloat` 0.12.1 | Atribución de tamaño por crate/función | No |
| Node (`cdp-probe.mjs`) | Sonda DevTools Protocol para FPS y métricas V8 | No |
| `perf/measure.ps1` | Tomas de arranque, idle, artefactos | No |

Ninguna de estas herramientas forma parte del binario ni del instalador.
