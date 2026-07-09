param(
  [string]$ArquivoPeneirado = "",
  [string]$BaseSaida = "TRIN_HISTORICO\00_PROCESSAMENTO_TT\CANDLE_5S_DIAGNOSTICO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Num($v) {
  if ($null -eq $v) { return $null }
  $s = ([string]$v).Trim()
  if ($s -eq "" -or $s -eq "-") { return $null }
  if ($s.Contains(",")) { $s = $s.Replace(".", "").Replace(",", ".") }

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

function Bucket5s($dataPregao, $horaTt) {
  $dt = [datetime]::ParseExact(
    "$dataPregao $horaTt",
    "yyyy-MM-dd HH:mm:ss.fff",
    [System.Globalization.CultureInfo]::InvariantCulture
  )

  $segBucket = [math]::Floor($dt.Second / 5) * 5

  return Get-Date -Date ([datetime]::new($dt.Year, $dt.Month, $dt.Day, $dt.Hour, $dt.Minute, $segBucket)) -Format "yyyy-MM-dd HH:mm:ss"
}

$TRIN_ROOT = Resolve-Path "."

if ([string]::IsNullOrWhiteSpace($ArquivoPeneirado)) {
  $ultimo = Get-ChildItem "TRIN_HISTORICO\00_PROCESSAMENTO_TT\BASTIAO_TT_PENEIRADOR" -Recurse -File |
    Where-Object { $_.Name -like "TT_PENEIRADO_NAO_CERTIFICADO_*.csv" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if (-not $ultimo) {
    throw "Nenhum TT_PENEIRADO_NAO_CERTIFICADO encontrado."
  }

  $ArquivoPeneirado = $ultimo.FullName
}

Write-Host "`n===== CANDLE 5S DIAGNOSTICO 01 =====" -ForegroundColor Cyan
Write-Host "Arquivo peneirado: $ArquivoPeneirado"

$dados = Import-Csv $ArquivoPeneirado -Delimiter ";"

$validos = @(
  $dados | Where-Object {
    $_.status_bastiao -eq "TT_PENEIRADO_NAO_CERTIFICADO" -and
    $_.classificacao_bastiao -eq "NEGOCIO_VALIDO_PROVAVEL"
  }
)

if ($validos.Count -eq 0) {
  throw "Nenhum NEGOCIO_VALIDO_PROVAVEL encontrado no TT peneirado."
}

$primeiro = $validos | Select-Object -First 1
$dataPregao = $primeiro.data_pregao
$contrato = $primeiro.contrato
$dataArquivo = $dataPregao.Replace("-", "")

$pastaSaida = Join-Path $TRIN_ROOT "$BaseSaida\$contrato\$dataPregao"
New-Item -ItemType Directory -Force $pastaSaida | Out-Null

$arqCandles = Join-Path $pastaSaida "CANDLE_5S_DIAGNOSTICO_${contrato}_${dataArquivo}.csv"
$arqResumo = Join-Path $pastaSaida "RESUMO_CANDLE_5S_DIAGNOSTICO_${contrato}_${dataArquivo}.csv"
$arqRelatorio = Join-Path $pastaSaida "RELATORIO_CANDLE_5S_DIAGNOSTICO_${contrato}_${dataArquivo}.txt"

$linhas = foreach ($r in $validos) {
  $preco = Num $r.preco
  $qtd = Num $r.quantidade

  if ($null -eq $preco -or $null -eq $qtd -or $preco -le 0 -or $qtd -le 0) {
    continue
  }

  [pscustomobject]@{
    bucket = Bucket5s $r.data_pregao $r.hora_tt
    data_pregao = $r.data_pregao
    contrato = $r.contrato
    hora_tt = $r.hora_tt
    preco = $preco
    quantidade = $qtd
    evento_mercado = $r.evento_mercado
    hash_evento = $r.hash_evento
  }
}

$candles = foreach ($g in ($linhas | Sort-Object bucket,hora_tt | Group-Object bucket)) {
  $regs = @($g.Group | Sort-Object hora_tt)

  $abertura = ($regs | Select-Object -First 1).preco
  $fechamento = ($regs | Select-Object -Last 1).preco
  $maximo = ($regs | Measure-Object preco -Maximum).Maximum
  $minimo = ($regs | Measure-Object preco -Minimum).Minimum
  $volume = ($regs | Measure-Object quantidade -Sum).Sum

  [pscustomobject][ordered]@{
    data_pregao = $dataPregao
    contrato = $contrato
    timeframe = "5S"
    bucket_inicio = $g.Name
    bucket_fim = (Get-Date ([datetime]::ParseExact($g.Name, "yyyy-MM-dd HH:mm:ss", $null)).AddSeconds(5) -Format "yyyy-MM-dd HH:mm:ss")
    abertura = $abertura
    maximo = $maximo
    minimo = $minimo
    fechamento = $fechamento
    volume_quantidade = $volume
    qtd_negocios = $regs.Count
    eventos_pregao = @($regs | Where-Object { $_.evento_mercado -eq "EVENTO_PREGAO" }).Count
    eventos_leilao = @($regs | Where-Object { $_.evento_mercado -eq "EVENTO_LEILAO" }).Count
    fonte = "TT_PENEIRADO_NAO_CERTIFICADO"
    status_candle = "CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO"
    uso_operacional = "DIAGNOSTICO_APENAS"
    candle_oficial = "false"
  }
}

$candles | Export-Csv $arqCandles -Delimiter ";" -NoTypeInformation -Encoding UTF8

$resumo = [pscustomobject][ordered]@{
  data_pregao = $dataPregao
  contrato = $contrato
  arquivo_peneirado = $ArquivoPeneirado
  arquivo_candles = $arqCandles
  total_negocios_validos = $validos.Count
  total_candles_5s = @($candles).Count
  status_candle = "CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO"
  uso_operacional = "DIAGNOSTICO_APENAS"
  candle_oficial = "false"
}

$resumo | Export-Csv $arqResumo -Delimiter ";" -NoTypeInformation -Encoding UTF8

@"
CANDLE 5S DIAGNOSTICO 01

Entrada:
$ArquivoPeneirado

Saida:
$arqCandles

Resumo:
total_negocios_validos: $($validos.Count)
total_candles_5s: $(@($candles).Count)

Status:
CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO
DIAGNOSTICO_APENAS
CANDLE_OFICIAL=false

Parecer:
Geracao diagnostica de candles de 5 segundos a partir de TT_PENEIRADO_NAO_CERTIFICADO.
Nao alimentar decisao operacional.
"@ | Set-Content $arqRelatorio -Encoding UTF8

Write-Host "`n===== RESULTADO =====" -ForegroundColor Green
Write-Host "Candles 5s gerados:" @($candles).Count
Write-Host "Arquivo:" $arqCandles
