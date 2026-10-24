#requires -Version 5.1
# Verifica que el repo standalone y su release son coherentes con lo medido y publicado.
# Uso: powershell -ExecutionPolicy Bypass -File perf\verify-publish.ps1
$ErrorActionPreference = 'Stop'
$repoDir = 'D:\dev\whatsapp-tauri'
if (-not (Test-Path $repoDir)) { Write-Host ('FAIL  no existe ' + $repoDir); exit 1 }
Set-Location $repoDir
$repo = 'barraco002/whatsapp-tauri-lite'
$tag = 'v0.3.3'
$assetName = 'Whatsapp.Tauri_0.3.3_x64-setup.exe'
$assetSize = 2096259
$fails = New-Object System.Collections.ArrayList
function Check([string]$name, [scriptblock]$test) {
  try {
    $r = & $test
    if ($r) { Write-Host ('PASS  ' + $name) } else { Write-Host ('FAIL  ' + $name); [void]$fails.Add($name) }
  } catch {
    Write-Host ('FAIL  ' + $name + '  (' + $_.Exception.Message + ')'); [void]$fails.Add($name)
  }
}

Check 'repo publico y rama main' {
  $j = gh api ('repos/' + $repo) | ConvertFrom-Json
  (-not $j.private) -and ($j.default_branch -eq 'main')
}
Check 'topics >= 7' {
  $j = gh api ('repos/' + $repo + '/topics') -H 'Accept: application/vnd.github+json' | ConvertFrom-Json
  $j.names.Count -ge 7
}
Check 'release publicado (no draft, no prerelease)' {
  $r = gh release view $tag --repo $repo --json isDraft,isPrerelease | ConvertFrom-Json
  (-not $r.isDraft) -and (-not $r.isPrerelease)
}
Check ('asset ' + $assetName + ' con ' + $assetSize + ' B') {
  $r = gh release view $tag --repo $repo --json assets | ConvertFrom-Json
  $a = $r.assets | Where-Object { $_.name -eq $assetName }
  ($null -ne $a) -and ([int64]$a.size -eq $assetSize)
}
Check 'main remoto == HEAD local' {
  $remote = (git -C $repoDir ls-remote lite refs/heads/main) -split "`t" | Select-Object -First 1
  $head = git -C $repoDir rev-parse HEAD
  $remote.Trim() -eq $head.Trim()
}
Check 'README remoto tiene el H1 de producto' {
  $b64 = gh api ('repos/' + $repo + '/readme') --jq .content
  $txt = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(($b64 -join '')))
  $txt.Contains('# WhatsApp Tauri Lite')
}
Check 'los 8 documentos del runbook estan en el remoto' {
  $tree = gh api ('repos/' + $repo + '/git/trees/main?recursive=0') --jq '.tree[].path'
  $need = @('OPTIMIZATION_REPORT.md','perf-log.md','bottleneck-analysis.md','BENCHMARKS.md','BUGS_FOUND.md','DEPENDENCIES_JUSTIFICATION.md','PERF-PLAN.md','LICENSE')
  ($need | Where-Object { $tree -notcontains $_ }).Count -eq 0
}

Check 'imagenes referenciadas por el README presentes' {
  $tree = git -C $repoDir ls-tree -r --name-only lite/main
  ($tree -contains 'assets/whatsapp-tauri.svg') -and ($tree -contains 'assets/social-preview.png')
}
Check 'topics incluyen tauri y rust' {
  $j = gh api ('repos/' + $repo + '/topics') -H 'Accept: application/vnd.github+json' | ConvertFrom-Json
  ($j.names -contains 'tauri') -and ($j.names -contains 'rust')
}

Check 'documentacion de comunidad presente' {
  $tree = git -C $repoDir ls-tree -r --name-only lite/main
  $need = @('SECURITY.md','CONTRIBUTING.md','CODE_OF_CONDUCT.md','.github/PULL_REQUEST_TEMPLATE.md','.github/ISSUE_TEMPLATE/bug.yml','.github/ISSUE_TEMPLATE/feature.yml','.github/ISSUE_TEMPLATE/config.yml')
  ($need | Where-Object { $tree -notcontains $_ }).Count -eq 0
}
Check 'community health = 100' {
  $h = gh api ('repos/' + $repo + '/community/profile') | ConvertFrom-Json
  [int]$h.health_percentage -eq 100
}
Check 'discussions habilitadas' {
  $j = gh api ('repos/' + $repo) | ConvertFrom-Json
  [bool]$j.has_discussions
}

if ($fails.Count -gt 0) {
  Write-Host ''
  Write-Host ('FALLOS: ' + ($fails -join ', '))
  exit 1
}
Write-Host ''
Write-Host 'OK: publicacion verificada'
exit 0