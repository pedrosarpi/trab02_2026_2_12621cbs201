"""Regressões de responsabilidade compartilhada entre web e terminal."""
from unittest.mock import patch

from app.menus import MenuPrincipal
from tests.test_web import app, client, ativo, post


def test_renomear_conta_atualiza_responsavel_nas_listagens(client, app):
    conta = app.extensions['usuarios'].listar()[0]
    ativo(client, app, responsavel_id=conta['id'])
    resposta = post(client, '/usuarios', dict(
        acao='renomear', senha_atual='senha-teste', novo_login='ana-renomeada'))
    assert resposta.status_code == 302
    for rota in ('/', '/ativos'):
        html = client.get(rota).get_data(as_text=True)
        assert '<td>ana-renomeada</td>' in html
        assert '<td>ana</td>' not in html


def test_responsavel_manual_no_terminal_remove_vinculo_anterior(client, app):
    usuarios = app.extensions['usuarios']
    conta = usuarios.listar()[0]
    ativo(client, app, responsavel_id=conta['id'])
    inventario, _ = app.extensions['inventario'].ler()
    with patch('app.menus.repositorio', return_value=usuarios):
        menu = MenuPrincipal(inventario, 'ana')
    with patch('builtins.input', side_effect=['1', '', 'Equipe nova', '', '', 'n', 'n']):
        menu.atualizar_ativo()
    recarregado, _ = app.extensions['inventario'].ler()
    equipamento = recarregado.obter(1)
    assert equipamento.responsavel == 'Equipe nova'
    assert equipamento.responsavel_id == ''
    html = client.get('/ativos/1').get_data(as_text=True)
    assert 'Equipe nova' in html
