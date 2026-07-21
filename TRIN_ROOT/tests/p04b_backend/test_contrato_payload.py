from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from backend.confluencia_replay_backend import anexar_confluencia_replay_backend, campo_seguro
from tests.p04b_backend.helpers import RepositorioFake, env_config, payload_fiscal_aprovado, saida_p04a_valida


def test_campo_seguro_tem_constantes():
    campo = campo_seguro('INDISPONIVEL','X','motivo')
    assert campo['contrato']=='ConfluenciaReplayBackendV1'
    assert campo['versao']=='1.0.0'
    assert campo['modo']=='SOMBRA'
    assert campo['peso']==0 and campo['impacto_operacional']==0
    assert campo['operacional'] is False
    assert campo['gate_fiscal']['bloqueio_operacional'] is True


def test_schema_backend_aceita_seguro():
    root=Path(__file__).resolve().parents[2]
    schema=json.loads((root/'governance/08_CONTRATOS/CONFLUENCIA_REPLAY_BACKEND_V1.schema.json').read_text(encoding='utf-8'))
    assert not list(Draft202012Validator(schema).iter_errors(campo_seguro('INDISPONIVEL','X','m')))

@pytest.mark.parametrize('chave', ['entrada','stop','parcial','alvo','ordem','direcao_operacional'])
def test_schema_rejeita_campo_operacional(chave):
    root=Path(__file__).resolve().parents[2]
    schema=json.loads((root/'governance/08_CONTRATOS/CONFLUENCIA_REPLAY_BACKEND_V1.schema.json').read_text(encoding='utf-8'))
    doc=campo_seguro('INDISPONIVEL','X','m'); doc[chave]=1
    assert list(Draft202012Validator(schema).iter_errors(doc))


def test_payload_aditivo_preserva_chaves_e_tipos(tmp_path):
    original={'historico':[],'confluencia':{'score':7},'entrada':None,'numero':3}
    snapshot=copy.deepcopy(original)
    result=anexar_confluencia_replay_backend(original,replay_ativo=False)
    assert original==snapshot
    assert {k:type(v) for k,v in original.items()}=={k:type(result[k]) for k,v in original.items()}
    assert result['confluencia']==original['confluencia']
    assert result['confluencia_replay']['operacional'] is False


def test_saida_p04a_valida_projetada(tmp_path):
    p04a=saida_p04a_valida()
    result=anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(), replay_ativo=True,
        replay_status={'data_pregao':'2026-01-21'}, environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]), avaliador=lambda _c,_r:p04a,
    )
    campo=result['confluencia_replay']
    assert campo['status']==p04a['status']
    assert campo['id_confluencia']==p04a['id_confluencia']
    assert campo['hash_resultado']==p04a['hash_resultado']
    assert campo['quantidade_experiencias']==2
    assert campo['peso']==0 and campo['impacto_operacional']==0 and campo['operacional'] is False
    assert campo['gate_fiscal']['fonte']=='FISCAL_TEMPORAL_LAUDO_OFICIAL'
    assert campo['gate_fiscal']['aprovado_operacional'] is True
