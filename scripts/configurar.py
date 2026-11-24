"""Gera um .env privado. Nunca imprime a chave nem substitui um arquivo existente."""
import argparse
import os
from pathlib import Path
import re
import secrets


def identificacao_academica(matricula):
    if not isinstance(matricula, str) or not re.fullmatch(r'[A-Za-z0-9]{3,48}', matricula):
        raise ValueError('Matrícula: use somente letras e números, sem pontos ou traços.')
    if not re.fullmatch(r'[0-9]{3}', matricula[-3:]):
        raise ValueError('A matrícula deve terminar com três dígitos.')
    return 'trab02_2026_2_' + matricula.lower(), 2000 + int(matricula[-3:])


def configurar(caminho, projeto, porta):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{1,62}', projeto):
        raise ValueError('Projeto: use 2 a 63 letras minúsculas, números, hífens ou sublinhados.')
    if not 1024 <= porta <= 65535:
        raise ValueError('Use uma porta entre 1024 e 65535, disponível e autorizada no servidor.')
    texto = (f'COMPOSE_PROJECT_NAME={projeto}\nPORTA_WEB={porta}\nSECRET_KEY={secrets.token_hex(32)}\n'
             'PERMITIR_CADASTRO=true\nCOOKIE_SEGURO=false\nNVD_API_KEY=\n')
    fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as arquivo:
        arquivo.write(texto)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--matricula', help='Servidor acadêmico: calcula o nome obrigatório e a porta.')
    grupo.add_argument('--projeto', help='Nome explícito para teste local ou CI.')
    parser.add_argument('--porta', type=int, help='Porta local; com matrícula deve coincidir com a calculada.')
    args = parser.parse_args()
    try:
        if args.matricula:
            projeto, porta = identificacao_academica(args.matricula)
            if args.porta is not None and args.porta != porta:
                raise ValueError(f'A porta calculada para esta matrícula é {porta}.')
        else:
            projeto, porta = args.projeto, args.porta if args.porta is not None else 2201
        configurar(Path('.env'), projeto, porta)
    except (ValueError, OSError) as erro:
        parser.exit(1, f'Não foi possível configurar: {erro}\n')
    print('.env criado. Guarde-o fora do Git e execute docker compose up -d --build.')


if __name__ == '__main__':
    main()
