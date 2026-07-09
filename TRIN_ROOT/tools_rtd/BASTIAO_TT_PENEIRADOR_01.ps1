param(
  [string]$ArquivoRaw = "",
  [string]$BaseSaida = "TRIN_HISTORICO\00_PROCESSAMENTO_TT\BASTIAO_TT_PENEIRADOR"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Eh-VazioOuTraco($v) {
  if ($null -eq $v) { return $true }
  $s = ([string]$v).Trim()
  return ([string]::IsNullOrWhiteSpace($s) -or $s -eq "-")
}

function Converter-Numero($v) {
  if (Eh-VazioOuTraco $v) { return $null }

  $s = ([string]$v).Trim()

  if ($s.Contains(",")) {
    $s = $s.Replace(".", "").Replace(",", ".")
  }

  $n = 0.0
  $ok = [double]::TryParse(
    $s,
    [System.Globalization.NumberStyles]::Float,
    [System.Globalization.CultureInfo]::InvariantCulture,
    [ref]$n
  )

  if (-not $ok) { return $null }
  return $n
}

function Chave-Bastiao($r) {
  return "$($r.data_pregao)|$($r.contrato)|$($r.hora_tt)|$($r.compradora)|$($r.preco)|$($r.quantidade)|$($r.vendedora)|$($r.agressor)|$($r.agente_agressor)"
}

function Evento-Mercado($agressor) {
  if ($null -eq $agressor) { return "FONTE_INSUFICIENTE" }

  $s = ([string]$agressor).Trim()

  if ($s -match "Leil") { return "EVENTO_LEILAO" }
  if (-not [string]::IsNullOrWhiteSpace($s) -and $s -ne "-") { return "EVENTO_PREGAO" }

  return "FONTE_INSUFICIENTE"
}

function Novo-Registro($r, $status, $classificacao, $evento, $chave, $qtdChave, $motivo) {
  return [pscustomobject][ordered]@{
    data_pregao = $r.data_pregao
    timestamp_captura_pc = $r.timestamp_captura_pc
    contrato = $r.contrato
    row_excel = $r.row_excel
    hora_tt = $r.hora_tt
    compradora = $r.compradora
    preco = $r.preco
    quantidade = $r.quantidade
    vendedora = $r.vendedora
    agressor = $r.agressor
    agente_agressor = $r.agente_agressor
    ocorrencia_snapshot = $r.ocorrencia_snapshot
    hash_evento = $r.hash_evento
    origem = $r.origem
    status_certificacao_origem = $r.status_certificacao
    status_bastiao = $status
    classificacao_bastiao = $classificacao
    evento_mercado = $evento
    chave_bastiao = $chave
    ocorrencias_chave = $qtdChave
    motivo_bastiao = $motivo
  }
}

$TRIN_ROOT = Resolve-Path "."

if ([string]::IsNullOrWhiteSpace($ArquivoRaw)) {
  $ultimo = Get-ChildItem "TRIN_HISTORICO\000_TT_BRUTO" -Recurse -File -ErrorAction Stop |
    Where-Object { $_.FullName -notmatch "_QUARENTENA" -and $_.Name -match "^TT_RAW_.*\.csv$" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if (-not $ultimo) {
    throw "Nenhum TT_RAW encontrado em TRIN_HISTORICO\000_TT_BRUTO."
  }

  $ArquivoRaw = $ultimo.FullName
}

Write-Host "`n===== BASTIAO TT PENEIRADOR 01 =====" -ForegroundColor Cyan
Write-Host "TRIN_ROOT  : $TRIN_ROOT"
Write-Host "Arquivo RAW: $ArquivoRaw"

$dados = Import-Csv $ArquivoRaw -Delimiter ";"

if (-not $dados -or $dados.Count -eq 0) {
  throw "Arquivo RAW vazio ou invalido."
}

$primeiro = $dados | Select-Object -First 1
$contrato = $primeiro.contrato
$dataPregao = $primeiro.data_pregao

if ([string]::IsNullOrWhiteSpace($contrato)) { $contrato = "CONTRATO_DESCONHECIDO" }
if ([string]::IsNullOrWhiteSpace($dataPregao)) { $dataPregao = Get-Date -Format "yyyy-MM-dd" }

$dataArquivo = $dataPregao.Replace("-", "")
$pastaSaida = Join-Path $TRIN_ROOT "$BaseSaida\$contrato\$dataPregao"
New-Item -ItemType Directory -Force $pastaSaida | Out-Null

$arqPeneirado = Join-Path $pastaSaida "TT_PENEIRADO_NAO_CERTIFICADO_${contrato}_${dataArquivo}.csv"
$arqRejeitados = Join-Path $pastaSaida "TT_REJEITADOS_${contrato}_${dataArquivo}.csv"
$arqIncertezas = Join-Path $pastaSaida "TT_INCERTEZAS_${contrato}_${dataArquivo}.csv"
$arqResumo = Join-Path $pastaSaida "RESUMO_BASTIAO_TT_PENEIRADOR_${contrato}_${dataArquivo}.csv"
$arqManifesto = Join-Path $pastaSaida "MANIFESTO_BASTIAO_TT_PENEIRADOR_${contrato}_${dataArquivo}.json"
$arqRelatorio = Join-Path $pastaSaida "RELATORIO_BASTIAO_TT_PENEIRADOR_${contrato}_${dataArquivo}.txt"

$contagemChaves = @{}

foreach ($r in $dados) {
  $horaOk = (-not (Eh-VazioOuTraco $r.hora_tt)) -and (([string]$r.hora_tt) -match "^\d{2}:\d{2}:\d{2}\.\d{3}$")
  $precoNum = Converter-Numero $r.preco
  $qtdNum = Converter-Numero $r.quantidade

  if ($horaOk -and $null -ne $precoNum -and $null -ne $qtdNum -and $precoNum -gt 0 -and $qtdNum -gt 0) {
    $chave = Chave-Bastiao $r
    if (-not $contagemChaves.ContainsKey($chave)) {
      $contagemChaves[$chave] = 0
    }
    $contagemChaves[$chave] += 1
  }
}

$peneirado = New-Object System.Collections.Generic.List[object]
$rejeitados = New-Object System.Collections.Generic.List[object]
$incertezas = New-Object System.Collections.Generic.List[object]

foreach ($r in $dados) {
  $motivos = New-Object System.Collections.Generic.List[string]

  $horaVazia = Eh-VazioOuTraco $r.hora_tt
  $horaOk = (-not $horaVazia) -and (([string]$r.hora_tt) -match "^\d{2}:\d{2}:\d{2}\.\d{3}$")

  $precoNum = Converter-Numero $r.preco
  $qtdNum = Converter-Numero $r.quantidade

  $precoOk = ($null -ne $precoNum -and $precoNum -gt 0)
  $qtdOk = ($null -ne $qtdNum -and $qtdNum -gt 0)

  $evento = Evento-Mercado $r.agressor
  $chave = Chave-Bastiao $r

  $qtdChave = 0
  if ($contagemChaves.ContainsKey($chave)) {
    $qtdChave = $contagemChaves[$chave]
  }

  if (-not $horaOk) { $motivos.Add("TIMESTAMP_INVALIDO") }
  if (-not $precoOk) { $motivos.Add("PRECO_INVALIDO") }
  if (-not $qtdOk) { $motivos.Add("QUANTIDADE_INVALIDA") }

  if ($motivos.Count -gt 0) {
    $classificacao = ($motivos -join "+")
    if ($horaVazia -or $r.hora_tt -eq "-") {
      if (-not $precoOk -and -not $qtdOk) {
        $classificacao = "LINHA_CASCA_EXCEL"
      }
    }

    $rejeitados.Add((Novo-Registro $r "REJEITADO_PELO_BASTIAO" $classificacao $evento $chave $qtdChave ($motivos -join ";")))
    continue
  }

  if ($qtdChave -gt 1) {
    $incertezas.Add((Novo-Registro $r "TT_INCERTO_NAO_CERTIFICADO" "REPETICAO_REAL_POSSIVEL+DUPLICADO_PROVAVEL+INCERTEZA_SEQUENCIAL" $evento $chave $qtdChave "Mesmo conjunto de campos apareceu mais de uma vez; sem ID unico oficial nao e seguro apagar nem aprovar como unico."))
    continue
  }

  $peneirado.Add((Novo-Registro $r "TT_PENEIRADO_NAO_CERTIFICADO" "NEGOCIO_VALIDO_PROVAVEL" $evento $chave $qtdChave "Linha valida em criterios minimos v0."))
}

$peneirado | Export-Csv $arqPeneirado -Delimiter ";" -NoTypeInformation -Encoding UTF8
$rejeitados | Export-Csv $arqRejeitados -Delimiter ";" -NoTypeInformation -Encoding UTF8
$incertezas | Export-Csv $arqIncertezas -Delimiter ";" -NoTypeInformation -Encoding UTF8

$precosPeneirados = @($peneirado | ForEach-Object { Converter-Numero $_.preco } | Where-Object { $null -ne $_ })
$qtdsPeneiradas = @($peneirado | ForEach-Object { Converter-Numero $_.quantidade } | Where-Object { $null -ne $_ })

$resumo = [pscustomobject][ordered]@{
  data_pregao = $dataPregao
  contrato = $contrato
  arquivo_raw = $ArquivoRaw
  total_raw = $dados.Count
  total_peneirado = $peneirado.Count
  total_rejeitados = $rejeitados.Count
  total_incertezas = $incertezas.Count
  eventos_leilao_peneirado = @($peneirado | Where-Object { $_.evento_mercado -eq "EVENTO_LEILAO" }).Count
  eventos_pregao_peneirado = @($peneirado | Where-Object { $_.evento_mercado -eq "EVENTO_PREGAO" }).Count
  preco_min_peneirado = (($precosPeneirados | Measure-Object -Minimum).Minimum)
  preco_max_peneirado = (($precosPeneirados | Measure-Object -Maximum).Maximum)
  qtd_total_peneirada = (($qtdsPeneiradas | Measure-Object -Sum).Sum)
  status_saida = "TT_PENEIRADO_NAO_CERTIFICADO"
  uso_operacional = "DIAGNOSTICO_APENAS"
  candle_oficial = "false"
}

$resumo | Export-Csv $arqResumo -Delimiter ";" -NoTypeInformation -Encoding UTF8

$manifesto = [pscustomobject][ordered]@{
  modulo = "BASTIAO_TT_PENEIRADOR_01"
  status = "EXECUTADO_DIAGNOSTICO"
  data_execucao = (Get-Date -Format "o")
  arquivo_raw = $ArquivoRaw
  arquivo_peneirado = $arqPeneirado
  arquivo_rejeitados = $arqRejeitados
  arquivo_incertezas = $arqIncertezas
  arquivo_resumo = $arqResumo
  total_raw = $dados.Count
  total_peneirado = $peneirado.Count
  total_rejeitados = $rejeitados.Count
  total_incertezas = $incertezas.Count
  status_saida = "TT_PENEIRADO_NAO_CERTIFICADO"
  uso_operacional = "DIAGNOSTICO_APENAS"
  candle_oficial = $false
}

$manifesto | ConvertTo-Json -Depth 5 | Set-Content $arqManifesto -Encoding UTF8

@"
BASTIAO TT PENEIRADOR 01

Arquivo RAW:
$ArquivoRaw

Saidas:
$arqPeneirado
$arqRejeitados
$arqIncertezas
$arqResumo
$arqManifesto

Resumo:
total_raw        : $($dados.Count)
total_peneirado  : $($peneirado.Count)
total_rejeitados : $($rejeitados.Count)
total_incertezas : $($incertezas.Count)

Status:
TT_PENEIRADO_NAO_CERTIFICADO
DIAGNOSTICO_APENAS
CANDLE_OFICIAL=false

Parecer:
O Bastiao peneirou o TT RAW sem alterar o arquivo bruto.
As incertezas foram preservadas, nao apagadas.
"@ | Set-Content $arqRelatorio -Encoding UTF8

Write-Host "`n===== RESULTADO =====" -ForegroundColor Green
Write-Host "Peneirado : $($peneirado.Count)"
Write-Host "Rejeitados: $($rejeitados.Count)"
Write-Host "Incertezas: $($incertezas.Count)"
Write-Host "`nRelatorio: $arqRelatorio"
