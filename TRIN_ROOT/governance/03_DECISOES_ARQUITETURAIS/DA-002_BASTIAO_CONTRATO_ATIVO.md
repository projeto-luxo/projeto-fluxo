# DA-002 - Bastiao como Validador Oficial do Contrato Ativo

## Status
PROPOSTA PARA ORGANIZACAO

## Problema identificado
O Excel RTD estava preso em contrato fixo, exemplo:

WINM26_F_0

Mesmo com o Profit exibindo WINQ26, o Excel continuava lendo WINM26 porque as formulas RTD continham o contrato hardcoded.

## Decisao arquitetural
O contrato ativo nao deve ser decidido manualmente dentro das formulas do Excel.

O TRIN deve ter uma cadeia oficial:

Calendario B3 Oficial
-> ContratoAtivoResolver
-> Bastiao valida e certifica
-> Atualizador Excel aplica
-> Leitor RTD le
-> Backend e Painel exibem

## Responsabilidade do Bastiao
O Bastiao deve validar:

1. Se o contrato escolhido esta correto para a data atual.
2. Se a rolagem respeita o calendario oficial da B3.
3. Se ha divergencia entre Excel, Profit e backend.
4. Se a leitura operacional pode ser liberada.
5. Se deve haver bloqueio por contrato invalido.

## O que o Bastiao NAO deve fazer
- Nao deve ler RTD diretamente.
- Nao deve alterar formulas do Excel diretamente.
- Nao deve substituir o leitor institucional.
- Nao deve decidir com base em chute ou contrato manual.
- Nao deve ignorar calendario B3 oficial.

## Modulos envolvidos

### Calendario B3
Fonte de datas oficiais, feriados, UDN, LF e vencimentos.

### ContratoAtivoResolver
Resolve qual contrato deveria estar ativo hoje.

### Bastiao
Certifica se o contrato resolvido pode ser usado.

### Atualizador Excel
Aplica no Excel o contrato aprovado pelo Bastiao.

### Leitor RTD
Le apenas os dados que o Excel entregar.

## Regra de ouro
Nenhum Excel, backend ou painel pode decidir contrato sozinho.
Contrato ativo vem de fonte oficial e passa pelo Bastiao.
