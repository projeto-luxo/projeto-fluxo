# CONTRATO OFICIAL — MOTOR DE REGIÕES V1.1

**Status:** PLANEJADO / NÃO IMPLEMENTADO
**Uso operacional:** BLOQUEADO
**Substitui conceitualmente:** V1 após homologação

## 1. Missão

Localizar, registrar, manter e invalidar referências de mercado rastreáveis.

A primeira versão não prevê comportamento e não produz plano operacional.

## 2. Entradas

Cada fornecedor deve declarar:

- ativo;
- contrato;
- timestamp_fonte;
- timestamp_processamento;
- timeframe;
- valor ou faixa;
- fornecedor;
- campo_origem;
- modo_dados;
- qualidade;
- certificação;
- versão.

## 3. Saída canônica

```json
{
  "chave_referencia": "REF-DETERMINISTICA",
  "id_evento": "RGE-YYYYMMDD-000001",
  "ativo": "WIN",
  "contrato": "WINQ26",
  "natureza": "NIVEL_REFERENCIA|FAIXA_REFERENCIA",
  "origem_tipo": "MILHAR|VWAP_OFICIAL|ABERTURA_SESSAO|MAXIMA_SESSAO|MINIMA_SESSAO|FRACTAL|OUTRA_FONTE_HOMOLOGADA",
  "funcao_provavel": "INDETERMINADA|EQUILIBRIO|PARADA|REVERSAO|CONTINUACAO|DEFESA",
  "status_funcao": "NAO_AVALIADA|HIPOTESE|EVIDENCIADA|CONFIRMADA",
  "limite_inferior": 0.0,
  "limite_superior": 0.0,
  "fornecedor": "",
  "campo_origem": "",
  "timeframe_origem": "",
  "modo_dados": "AO_VIVO|REPLAY|HISTORICO|TESTE_SINTETICO",
  "origens": [],
  "timestamp_fonte": "",
  "timestamp_processamento": "",
  "inicio_validade": "",
  "fim_validade": "",
  "condicao_invalidacao": "",
  "status": "CANDIDATA|ATIVA|ENFRAQUECIDA|INVALIDADA|EXPIRADA|BLOQUEADA",
  "motivo_status": "",
  "qualidade_dados": "",
  "status_certificacao": "",
  "uso_operacional": "BLOQUEADO",
  "versao_regra": "1.1"
}
```

## 4. Regras da versão 1.1

- `origem_tipo` declara de onde nasceu a referência.
- `funcao_provavel` declara interpretação posterior.
- A primeira implementação usa `funcao_provavel = INDETERMINADA`.
- A primeira implementação usa `status_funcao = NAO_AVALIADA`.
- `CONFIRMADA` descreve maturidade da interpretação; não significa homologação documental, certificação, autorização ou liberação operacional.
- A primeira implementação não produz direção, força ou confiança.
- Referência inválida permanece no histórico com novo estado.
- A composição definitiva de `chave_referencia` será homologada antes da implementação.
- A composição deverá considerar, no mínimo: ativo, contrato, sessão ou data de referência, `origem_tipo`, fornecedor, `campo_origem`, `timeframe_origem`, valor ou faixa normalizada e versão da regra.
- Não é necessário definir algoritmo ou hash na RG-02A.
- Mesmas entradas semânticas produzem a mesma `chave_referencia`.
- `id_evento` registra criação, atualização ou transição de estado.
- `timestamp_processamento` e `id_evento` não participam da identidade determinística da referência.
- Nenhuma região existe sem origem, fornecedor, campo de origem e versão.
- Na RG-02A, `fornecedor` e `campo_origem` representam a origem direta.
- Na RG-02A, `origens` permanece reservado e vazio; não é lista livre de textos ou fornecedores.
- No RG-02B futuro, `origens` poderá conter uma coleção estruturada das referências preservadas de uma região composta.
- Referências sobrepostas preservam identidade e proveniência próprias.

## 5. Fornecedores iniciais

### MILHAR

Fonte:

```text
PRECO_ATUAL
```

Estado:

```text
DISPONÍVEL PARA TESTE SINTÉTICO
```

### VWAP_OFICIAL

Fonte:

```text
VWAP OFICIAL DO PAYLOAD CANÔNICO
```

Estado:

```text
DISPONÍVEL COM PROVENIÊNCIA
```

### ABERTURA, MÁXIMA E MÍNIMA DA SESSÃO

Estado:

```text
BLOQUEADAS ATÉ PRESERVAÇÃO DOS CAMPOS ORIGINAIS
```

## 6. Proibições

O Motor de Regiões nunca deve:

- executar ordem;
- gerar entrada;
- calcular stop;
- calcular parcial;
- calcular alvo;
- definir quantidade de contratos;
- substituir Confluência;
- substituir Fiscal;
- substituir Gestão de Risco;
- inventar dado ausente;
- usar diagnóstico como certificado;
- classificar automaticamente MILHAR como REVERSÃO;
- classificar automaticamente VWAP como PARADA;
- produzir direção, força ou confiança na RG-02A.
