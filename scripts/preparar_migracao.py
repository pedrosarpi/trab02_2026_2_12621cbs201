"""Copia a configuração privada para uma nova pasta e reutiliza o volume existente.

Não executa Docker, não altera dados e não imprime segredos. Execute a partir
da nova pasta do projeto, antes de construir a imagem e parar a versão antiga.
"""
import argparse
import os
from pathlib import Path
import re

try:
    from scripts.configurar import identificacao_academica
except ModuleNotFoundError:
    from configurar import identificacao_academica


def preparar(origem, destino, matricula, volume):
    projeto, porta = identificacao_academica(matricula)
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*', volume):
        raise ValueError('Nome de volume inválido.')
    origem, destino = Path(origem), Path(destino)
    if origem.resolve() == destino.resolve():
        raise ValueError('Origem e destino devem ser arquivos diferentes.')
    texto = origem.read_text(encoding='utf-8')
    # O .env gerado por configurar.py usa atribuições simples, uma por linha.
    def valor(chave):
        encontrados = re.findall(r'^' + re.escape(chave) + r'=(.*)$', texto, re.MULTILINE)
        if len(encontrados) != 1:
            raise ValueError(f'A configuração de origem deve conter exatamente uma linha {chave}=...')
        return encontrados[0].strip().strip('\"\'')
    chave = valor('SECRET_KEY')
    if len(chave) < 32 or '$' in chave:
        raise ValueError('A SECRET_KEY da origem precisa ser literal e ter pelo menos 32 caracteres.')
    if valor('PORTA_WEB') != str(porta):
        raise ValueError('A porta existente difere da calculada. Confirme a atribuição antes de migrar.')
    atualizacoes = dict(COMPOSE_PROJECT_NAME=projeto, PORTA_WEB=str(porta),
                       COMPOSE_FILE='compose.yaml:compose.volume-existente.yaml',
                       VOLUME_DADOS_EXISTENTE=volume)
    linhas = []
    for linha in texto.splitlines():
        nome = linha.split('=', 1)[0].strip()
        if nome not in atualizacoes:
            linhas.append(linha)
    linhas.extend(f'{nome}={valor}' for nome, valor in atualizacoes.items())
    fd = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as arquivo:
        arquivo.write('\n'.join(linhas) + '\n')
    return projeto, porta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origem', required=True, type=Path)
    parser.add_argument('--matricula', required=True)
    parser.add_argument('--volume', required=True)
    args = parser.parse_args()
    try:
        projeto, porta = preparar(args.origem, Path('.env'), args.matricula, args.volume)
    except (OSError, ValueError) as erro:
        parser.exit(1, f'Configuração não criada: {erro}\n')
    print(f'Configuração criada: projeto {projeto}, porta {porta}.')
    print('O volume existente será exigido; a aplicação antiga ainda não foi alterada.')


if __name__ == '__main__':
    main()
