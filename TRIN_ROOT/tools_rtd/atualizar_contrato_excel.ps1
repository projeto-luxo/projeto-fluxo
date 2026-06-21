$Calendario = "C:\Users\User\projeto_fluxo\TRIN_ROOT\config\contratos_ativos_trin.csv"
$WorkbookPath = "C:\Users\User\projeto_fluxo\MARCO_ZERO_INSTITUCIONAL.xlsx"

if (!(Test-Path $Calendario)) {
    throw "Calendario de contratos nao encontrado: $Calendario"
}

$contratos = Import-Csv $Calendario -Delimiter ";"
$ativo = $contratos | Where-Object { $_.ativo_base -eq "WIN" -and $_.status -eq "ATIVO" } | Select-Object -First 1

if ($null -eq $ativo) {
    throw "Nenhum contrato WIN com status ATIVO encontrado no calendario."
}

$ContratoRTD = $ativo.contrato_rtd
$ContratoVisual = $ativo.contrato_visual

Write-Host "Contrato oficial TRIN:"
Write-Host "Visual: $ContratoVisual"
Write-Host "RTD:    $ContratoRTD"

try {
    $excel = [Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application")
} catch {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $true
}

$wb = $null

foreach ($book in $excel.Workbooks) {
    if ($book.FullName -eq $WorkbookPath) {
        $wb = $book
        break
    }
}

if ($null -eq $wb) {
    if (!(Test-Path $WorkbookPath)) {
        throw "Planilha nao encontrada: $WorkbookPath"
    }
    $wb = $excel.Workbooks.Open($WorkbookPath)
}

$totalAlteradas = 0

foreach ($ws in $wb.Worksheets) {
    $used = $ws.UsedRange

    for ($r = 1; $r -le $used.Rows.Count; $r++) {
        for ($c = 1; $c -le $used.Columns.Count; $c++) {
            $cell = $used.Cells.Item($r, $c)

            if ($cell.HasFormula) {
                $formula = [string]$cell.FormulaLocal

                if ($formula -match 'WIN[A-Z][0-9]{2}_F_0') {
                    $nova = $formula -replace 'WIN[A-Z][0-9]{2}_F_0', $ContratoRTD

                    if ($nova -ne $formula) {
                        $cell.FormulaLocal = $nova
                        $totalAlteradas++
                    }
                }
            } else {
                $valor = [string]$cell.Text

                if ($valor -match '^WIN[A-Z][0-9]{2}$') {
                    $cell.Value2 = $ContratoVisual
                    $totalAlteradas++
                }
            }
        }
    }
}

$wb.Save()

Write-Host "Atualizacao concluida."
Write-Host "Celulas/formulas alteradas: $totalAlteradas"
Write-Host "Contrato aplicado: $ContratoRTD"
