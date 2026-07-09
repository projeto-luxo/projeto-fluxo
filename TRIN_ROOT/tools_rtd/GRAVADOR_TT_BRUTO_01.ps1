param(
  [int]$IntervaloMs = 500,
  [int]$DuracaoMinutos = 30,
  [string]$DataPregao = "",
  [string]$WorkbookFiltro = "*MARCO_ZERO_INSTITUCIONAL*"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Escape-CsvCampo($v) {
  if ($null -eq $v) { return "" }

  $s = [string]$v
  $s = $s.Replace('"', '""')

  if ($s.Contains(";") -or $s.Contains('"') -or $s.Contains("`n") -or $s.Contains("`r")) {
    return '"' + $s + '"'
  }

  return $s
}

function Hash-Texto($texto) {
  $sha = [System.Security.Cryptography.SHA256]::Create()
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($texto)
  $hash = $sha.ComputeHash($bytes)
  return ([System.BitConverter]::ToString($hash)).Replace("-", "").ToLower()
}

function Get-ExcelText($ws, [int]$linha, [int]$coluna, [int]$tentativas = 10) {
  for ($i = 1; $i -le $tentativas; $i++) {
    try {
      return $ws.Cells.Item($linha, $coluna).Text
    } catch {
      if ($i -eq $tentativas) {
        throw
      }

      Start-Sleep -Milliseconds (100 + ($i * 100))
    }
  }
}

function Get-ExcelUsedRows($ws, [int]$tentativas = 10) {
  for ($i = 1; $i -le $tentativas; $i++) {
    try {
      return $ws.UsedRange.Rows.Count
    } catch {
      if ($i -eq $tentativas) {
        throw
      }

      Start-Sleep -Milliseconds (100 + ($i * 100))
    }
  }
}

if ([string]::IsNullOrWhiteSpace($DataPregao)) {
  $DataPregao = Get-Date -Format "yyyy-MM-dd"
}

$TRIN_ROOT = Resolve-Path "."
$dataArquivo = $DataPregao.Replace("-", "")

Write-Host "`n===== GRAVADOR TT BRUTO 01 =====" -ForegroundColor Cyan
Write-Host "TRIN_ROOT    : $TRIN_ROOT"
Write-Host "Data pregão  : $DataPregao"
Write-Host "Intervalo ms : $IntervaloMs"
Write-Host "Duração min  : $DuracaoMinutos"

$excel = [Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application")

$wb = $excel.Workbooks | Where-Object {
  $_.Name -like $WorkbookFiltro
} | Select-Object -First 1

if (-not $wb) {
  throw "Workbook não encontrado: $WorkbookFiltro"
}

$ws = $wb.Worksheets | Where-Object {
  $_.Name -like "*TT*" -or $_.Name -like "*Plan2*"
} | Select-Object -First 1

if (-not $ws) {
  throw "Aba TT não encontrada."
}

$contrato = Get-ExcelText $ws 1 1
if ([string]::IsNullOrWhiteSpace($contrato)) {
  $contrato = "WIN_TT"
}

$pastaSaida = Join-Path $TRIN_ROOT "TRIN_HISTORICO\000_TT_BRUTO\$contrato\$DataPregao"
New-Item -ItemType Directory -Force $pastaSaida | Out-Null

$arquivoSaida = Join-Path $pastaSaida "TT_RAW_${contrato}_${dataArquivo}.csv"

Write-Host "Workbook     : $($wb.Name)" -ForegroundColor Green
Write-Host "Aba TT       : $($ws.Name)" -ForegroundColor Green
Write-Host "Contrato     : $contrato" -ForegroundColor Green
Write-Host "Arquivo      : $arquivoSaida" -ForegroundColor Green

$header = @(
  "data_pregao",
  "timestamp_captura_pc",
  "contrato",
  "row_excel",
  "hora_tt",
  "compradora",
  "preco",
  "quantidade",
  "vendedora",
  "agressor",
  "agente_agressor",
  "ocorrencia_snapshot",
  "hash_evento",
  "origem",
  "status_certificacao"
) -join ";"

if (-not (Test-Path $arquivoSaida)) {
  Set-Content -Path $arquivoSaida -Value $header -Encoding UTF8
}

$vistos = @{}

try {
  Import-Csv $arquivoSaida -Delimiter ";" | ForEach-Object {
    if ($_.hash_evento) {
      $vistos[$_.hash_evento] = $true
    }
  }
} catch {}

$fim = (Get-Date).AddMinutes($DuracaoMinutos)
$totalNovos = 0
$ciclo = 0

Write-Host "`nGravando T.T. bruto. Para parar: Ctrl+C`n" -ForegroundColor Yellow

while ((Get-Date) -lt $fim) {
  $ciclo += 1
  $timestampPc = Get-Date -Format "o"

  $lastRow = Get-ExcelUsedRows $ws

  $contagemBaseSnapshot = @{}
  $linhasNovas = New-Object System.Collections.Generic.List[string]

  for ($r = 3; $r -le $lastRow; $r++) {
    $horaTt = Get-ExcelText $ws $r 1
    $compradora = Get-ExcelText $ws $r 2
    $preco = Get-ExcelText $ws $r 3
    $quantidade = Get-ExcelText $ws $r 4
    $vendedora = Get-ExcelText $ws $r 5
    $agressor = Get-ExcelText $ws $r 6
    $agenteAgressor = Get-ExcelText $ws $r 7

    if ([string]::IsNullOrWhiteSpace($horaTt) -or [string]::IsNullOrWhiteSpace($preco)) {
      continue
    }

    $base = "$DataPregao|$contrato|$horaTt|$compradora|$preco|$quantidade|$vendedora|$agressor|$agenteAgressor"

    if (-not $contagemBaseSnapshot.ContainsKey($base)) {
      $contagemBaseSnapshot[$base] = 0
    }

    $contagemBaseSnapshot[$base] += 1
    $ocorrencia = $contagemBaseSnapshot[$base]

    $hash = Hash-Texto "$base|$ocorrencia"

    if ($vistos.ContainsKey($hash)) {
      continue
    }

    $vistos[$hash] = $true

    $campos = @(
      $DataPregao,
      $timestampPc,
      $contrato,
      $r,
      $horaTt,
      $compradora,
      $preco,
      $quantidade,
      $vendedora,
      $agressor,
      $agenteAgressor,
      $ocorrencia,
      $hash,
      "EXCEL_TT_RTD",
      "RAW_NAO_CERTIFICADO"
    ) | ForEach-Object { Escape-CsvCampo $_ }

    $linhasNovas.Add(($campos -join ";"))
  }

  if ($linhasNovas.Count -gt 0) {
    Add-Content -Path $arquivoSaida -Value $linhasNovas -Encoding UTF8
    $totalNovos += $linhasNovas.Count
  }

  Write-Host ("{0} ciclo={1} novos={2} total_novos={3} linhas_excel={4}" -f (Get-Date -Format "HH:mm:ss"), $ciclo, $linhasNovas.Count, $totalNovos, $lastRow)

  Start-Sleep -Milliseconds $IntervaloMs
}

Write-Host "`n===== GRAVAÇÃO FINALIZADA =====" -ForegroundColor Green
Write-Host "Arquivo: $arquivoSaida"
Write-Host "Total novos: $totalNovos"
