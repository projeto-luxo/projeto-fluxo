# ATA DE DECISÃO — EIXO COCKPIT, CHECKLIST E INTELIGÊNCIA TRIN

**Data:** 2026-07-11
**Status:** APROVADA
**Projeto:** TRIN
**Natureza:** decisão metodológica, arquitetural e de produto

---

## 1. Objetivo desta ata

Consolidar as decisões tomadas sobre:

- o papel do checklist-eixo;
- a construção das cascas do cockpit;
- a separação entre cockpit operacional, diagnóstico e governança;
- a finalidade imediata da inteligência do TRIN;
- a visão futura de reutilização dessa inteligência;
- o adiamento do Modo Explicação para uma fase posterior.

## 2. Eixo oficial de trabalho

O trabalho passa a ser conduzido pelo conjunto:

**CHECKLIST-EIXO + COCKPIT + GIT/GOVERNANÇA**

- **Checklist-eixo:** seleciona e governa o módulo em trabalho.
- **Cockpit:** apresenta a síntese operacional dos módulos homologados.
- **Git/Governança:** prova, registra e preserva auditorias, contratos, decisões, homologações e checkpoints.

O cockpit não substitui o checklist. O checklist não substitui as evidências. O Git não define sozinho a finalidade operacional do módulo.

## 3. Ordem oficial para cada módulo

1. Localizar e analisar o módulo no checklist.
2. Identificar missão, estado atual, evidências e pendências.
3. Decidir exatamente o que desse módulo deverá aparecer no cockpit.
4. Definir o que ficará fora do cockpit operacional.
5. Criar a casca visual correspondente, sem inventar dados.
6. Retornar ao módulo no checklist.
7. Auditar, corrigir ou construir sua base.
8. Definir entradas, saídas, contratos, riscos e consumidores.
9. Integrar a base homologável à casca.
10. Testar tecnicamente e com dados reais.
11. Homologar o módulo.
12. Atualizar checklist, governança, Git e cockpit.

A casca não é o ponto de partida isolado. Ela é o destino visual antecipado do módulo escolhido no checklist.

## 4. Classificação visual dos módulos

- **[OP] Cockpit operacional:** resultado necessário durante a operação.
- **[DG] Diagnóstico técnico:** fonte, contrato, latência, integridade e explicações técnicas.
- **[GV] Governança:** auditorias, decisões, homologações, hashes, laudos e evidências.
- **[NA] Não aplicável à interface:** utilitários e componentes internos sem necessidade visual.

Nem todo módulo precisa de uma área própria no cockpit.

## 5. Diretriz definitiva do cockpit operacional

O cockpit final não deverá explicar a análise.

Ele deverá entregar apenas resultados objetivos, claros e acionáveis, como:

- possível região de reversão;
- região de milhar;
- provável região de parada;
- região de continuação;
- direção;
- entrada;
- saída;
- stop;
- parcial;
- alvo;
- invalidação;
- aguardar;
- sem operação;
- bloqueio essencial.

Detalhes como fontes RTD, contratos semânticos, nomes de tópicos, proveniência, correlação entre campos, estado de replay e explicações longas não permanecerão na tela operacional principal.

## 6. Destino dos elementos atualmente visíveis

Blocos usados durante a construção poderão permanecer temporariamente no cockpit para auditoria e depuração.

No produto final:

- **Status operacional:** permanece de forma resumida.
- **Fonte operacional detalhada:** migra para diagnóstico.
- **Contrato Delta/Saldo:** migra para diagnóstico.
- **Replay diagnóstico:** migra para ambiente próprio de laboratório/replay.
- **Textos explicativos:** saem da tela operacional.
- **Resultado operacional:** permanece.

A tela atual funciona como painel de mecânico com o capô aberto. A tela final deverá funcionar como painel do operador.

## 7. Referência do painel ASG

A imagem do painel ASG é referência funcional e conceitual, não exigência de cópia visual.

Ela representa:

- pouca informação por vez;
- leitura imediata;
- ausência de explicações extensas;
- entrega direta de regiões e decisões;
- redução da sobrecarga cognitiva do operador.

O TRIN deverá manter identidade própria e arquitetura própria.

## 8. Inteligência além do fluxo

A inteligência do TRIN não será limitada ao fluxo.

Ela deverá poder combinar, progressivamente:

- preço;
- volume;
- fluxo;
- tempo;
- VWAP;
- agressão;
- microestrutura;
- fractais;
- regiões;
- contexto;
- memória;
- comportamento histórico;
- certificação temporal.

O cockpit será apenas um consumidor dessa inteligência.

Consumidores futuros poderão incluir robô de execução, alertas, replay, simulador, estudos estatísticos, leitura ampla de mercado e outras aplicações.

Os módulos deverão produzir conhecimento estruturado e reutilizável, não apenas textos presos à interface.

## 9. Prioridade operacional imediata

A prioridade atual é construir uma inteligência mínima para o WIN que:

1. receba dados de mercado ao vivo;
2. valide atualidade, contrato, integridade e coerência;
3. rejeite dados ruins ou estagnados;
4. combine somente evidências autorizadas;
5. evite dupla contagem;
6. produza análise reproduzível;
7. entregue regiões e condições de entrada e saída;
8. permaneça bloqueada quando não houver evidência suficiente.

Saídas prioritárias:

- AGUARDAR;
- SEM OPERAÇÃO;
- POSSÍVEL COMPRA;
- POSSÍVEL VENDA;
- MANTER;
- REDUZIR;
- SAIR;
- região de entrada;
- invalidação;
- stop;
- parcial;
- alvo;
- validade da leitura.

“Minimamente confiável” não significa garantia de lucro. Significa dado verdadeiro, lógica consistente, decisão reproduzível, bloqueio seguro e validação mensurável.

## 10. Escopo atual

- Ativo prioritário: **WIN**.
- WDO: adiado até a conclusão do eixo atual e realização de coleta e auditoria próprias.
- Candle 5S: diagnóstico não certificado até validação de amostra, continuidade e fidelidade.
- Livro de Ofertas: etapa posterior ao avanço do eixo 5S e ao mapeamento RTD.
- Robô executor: fora do escopo imediato.
- Interface conversacional completa: fora do escopo imediato.

## 11. Modo Explicação

O **Modo Explicação** será tratado como projeto ou fase posterior.

Sua função futura será fornecer, sob demanda:

- fundamento técnico;
- módulos participantes;
- dados utilizados;
- rastreabilidade;
- motivos da conclusão;
- limites e incertezas.

O Modo Explicação não deverá ocupar permanentemente o cockpit operacional.

Ordem aprovada:

1. Primeiro: inteligência ao vivo e resultado operacional.
2. Depois: explicação técnica e rastreabilidade sob demanda.

## 12. Autoridade humana

O TRIN deverá executar o trabalho pesado de leitura, validação, cruzamento, síntese, organização e apresentação.

A decisão final permanece com o operador.

O sistema poderá propor, bloquear, alertar e justificar. Não deverá substituir silenciosamente a autorização humana.

## 13. Regra de encerramento por módulo

Um módulo somente será considerado encerrado quando houver, conforme aplicável:

- necessidade arquitetural registrada;
- auditoria;
- decisão;
- contrato;
- implementação controlada;
- teste automatizado;
- teste com dado real;
- laudo;
- homologação;
- atualização do checklist;
- commit;
- push;
- evidência preservada.

Sem evidência suficiente, o estado deverá permanecer pendente, diagnóstico, não certificado ou bloqueado.

## 14. Síntese oficial

**O checklist escolhe e governa o módulo.
O módulo define o que precisa aparecer no cockpit.
A casca antecipa o destino visual.
A auditoria e a construção consolidam a base.
A homologação fecha módulo e apresentação.
O cockpit final entrega somente resultados.
O diagnóstico explica.
A governança prova.
O operador decide.**
