"""Proteções da preparação de configuração; não acessa o Docker."""
from pathlib import Path
import stat

import pytest

from scripts.configurar import configurar, identificacao_academica
from scripts.preparar_migracao import preparar


def test_identificador_e_porta_da_matricula():
    assert identificacao_academica('12621CBS201') == ('trab02_2026_2_12621cbs201', 2201)
    assert identificacao_academica('123456') == ('trab02_2026_2_123456', 2456)


@pytest.mark.parametrize('matricula', ['12621-CBS201', 'matrícula201', '123ABC', '', '../201'])
def test_matricula_invalida(matricula):
    with pytest.raises(ValueError):
        identificacao_academica(matricula)


def test_migracao_preserva_segredo_origem_e_opcoes(tmp_path):
    origem = tmp_path / 'origem.env'
    destino = tmp_path / '.env'
    configurar(origem, 'orthocrud', 2201)
    origem.write_text(origem.read_text().replace('PERMITIR_CADASTRO=true', 'PERMITIR_CADASTRO=false'))
    antes = origem.read_bytes()
    preparar(origem, destino, '12621CBS201', 'orthocrud_dados')
    depois = destino.read_text()
    segredo = next(l for l in origem.read_text().splitlines() if l.startswith('SECRET_KEY='))
    assert segredo in depois
    assert 'PERMITIR_CADASTRO=false' in depois
    assert 'COMPOSE_PROJECT_NAME=trab02_2026_2_12621cbs201' in depois
    assert 'COMPOSE_FILE=compose.yaml:compose.volume-existente.yaml' in depois
    assert 'VOLUME_DADOS_EXISTENTE=orthocrud_dados' in depois
    assert origem.read_bytes() == antes
    assert stat.S_IMODE(destino.stat().st_mode) == 0o600
    with pytest.raises(FileExistsError):
        preparar(origem, destino, '12621CBS201', 'orthocrud_dados')
    assert destino.read_text() == depois


def test_porta_divergente_nao_cria_destino(tmp_path):
    origem = tmp_path / 'origem.env'
    configurar(origem, 'orthocrud', 2202)
    with pytest.raises(ValueError, match='porta'):
        preparar(origem, tmp_path / '.env', '12621CBS201', 'orthocrud_dados')
    assert not (tmp_path / '.env').exists()


@pytest.mark.parametrize('volume', ['', '../dados', 'volume com espaço'])
def test_volume_invalido_nao_cria_destino(tmp_path, volume):
    with pytest.raises(ValueError, match='volume'):
        preparar(tmp_path / 'origem.env', tmp_path / '.env', '12621CBS201', volume)
    assert not (tmp_path / '.env').exists()


def test_segredo_ausente_nao_cria_destino(tmp_path):
    origem = tmp_path / 'origem.env'
    origem.write_text('PORTA_WEB=2201\n')
    with pytest.raises(ValueError, match='SECRET_KEY'):
        preparar(origem, tmp_path / '.env', '12621CBS201', 'orthocrud_dados')
    assert not (tmp_path / '.env').exists()


def test_origem_igual_destino_e_recusada(tmp_path):
    origem = Path(tmp_path / '.env')
    configurar(origem, 'orthocrud', 2201)
    antes = origem.read_bytes()
    with pytest.raises(ValueError, match='diferentes'):
        preparar(origem, origem, '12621CBS201', 'orthocrud_dados')
    assert origem.read_bytes() == antes
