# verify.ps1 — evidencia ejecutable del cierre (runbook de optimizacion Tauri).
# Sale 0 solo si los entregables existen y la mejora principal se sostiene en disco.
$ErrorActionPreference = 'Stop'
$repo = 'D:\dev\whatsapp-tauri'
$fail = @()

# 1) Entregables del runbook (§8)
foreach ($f in @('OPTIMIZATION_REPORT.md','perf-log.md','bottleneck-analysis.md','BUGS_FOUND.md','DEPENDENCIES_JUSTIFICATION.md','PERF-PLAN.md')) {
  if (-not (Test-Path (Join-Path $repo $f))) { $fail += "falta $f" }
}

# 2) Evidencia cruda de las mediciones
foreach ($f in @('baseline-01.json','iter1-release-profile.json','iter1b-opt3.json','iter1b-startup10.json','iter1b-idle2.json')) {
  if (-not (Test-Path (Join-Path $repo "perf\out\$f"))) { $fail += "falta perf/out/$f" }
}

# 3) Perfil de release aplicado
$cargo = Get-Content (Join-Path $repo 'whatsapp-lite\src-tauri\Cargo.toml') -Raw
if ($cargo -notmatch '\[profile\.release\]') { $fail += 'Cargo.toml sin [profile.release]' }
if ($cargo -notmatch 'lto\s*=\s*"fat"') { $fail += 'Cargo.toml sin lto="fat"' }
if ($cargo -notmatch 'strip\s*=\s*"symbols"') { $fail += 'Cargo.toml sin strip="symbols"' }

# 4) El binario en disco refleja la mejora (baseline 12 729 344 B -> umbral 8 000 000 B)
$exe = Join-Path $repo 'whatsapp-lite\src-tauri\target\release\whatsapp-tauri.exe'
if (Test-Path $exe) {
  $size = (Get-Item $exe).Length
  if ($size -ge 8000000) { $fail += "exe sin reducir: $size B" }
  else { "exe = $size B (baseline 12729344 B, -{0:N1}%)" -f (100.0 * (12729344 - $size) / 12729344) }
} else { $fail += 'no existe el .exe release' }

if ($fail.Count -gt 0) { $fail | ForEach-Object { "FALLO: $_" }; exit 1 }
"OK: entregables, evidencia y perfil de release verificados"
exit 0
