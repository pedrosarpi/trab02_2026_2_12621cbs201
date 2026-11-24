# Atualização da instalação existente

Procedimento preparado com a saída do servidor fornecida em 23/11/2026:

| Item | Valor confirmado |
| --- | --- |
| Diretório atual | `~/trabalho2` |
| Projeto Compose | `orthocrud` |
| Container / imagem | `orthocrud-inventario-1` / `orthocrud-inventario` |
| Volume persistente | `orthocrud_dados`, montado em `/dados` |
| Porta | `127.0.0.1:2201` → `8000` no container |
| Início do container | `2026-11-09T22:36:07Z`, sem reinícios registrados |
| Compose | `2.40.3+ds1-0ubuntu1` |
| Identificador de destino | `trab02_2026_2_12621cbs201` |

Cada bloco Bash usa um subshell com interrupção no primeiro erro. Leia o resultado de uma etapa antes de executar a próxima.

As etapas abaixo ainda não foram executadas no servidor. A atualização tem uma
interrupção curta entre parar a versão antiga e iniciar a nova. Não use `down -v`,
`volume rm`, `system prune` ou comandos globais de limpeza.

## 1. Publicar o código revisado

No computador de desenvolvimento, confira `git status --short --branch`. Aplique
o patch entregue somente depois de preservar alterações locais. `git apply --check`
deve passar antes de `git apply`; uma divergência deve ser analisada, sem forçar
a aplicação. O patch foi preparado sobre o commit `9058a80`.

Execute `python -m pytest -q`, revise `git diff`, faça um commit e publique pelo
fluxo de branches/merge já adotado. Para atender ao card S5_20, renomeie o
repositório no GitHub para `trab02_2026_2_12621cbs201`, mantendo o histórico.
O nome comercial OrthoCRUD pode permanecer no README e na interface.

Continue somente quando o código revisado estiver na branch principal remota.
O ZIP/patch de revisão não atualiza o GitHub automaticamente.

## 2. Preparar uma pasta nova no servidor

Entre por SSH. Não substitua o diretório antigo; ele será o caminho de retorno.

```bash
(
set -eu
cd ~
git clone https://github.com/pedrosarpi/trab02_2026_2_12621cbs201.git trab02_2026_2_12621cbs201
cd ~/trab02_2026_2_12621cbs201
git log -1 --oneline
test -f scripts/preparar_migracao.py
python3 scripts/preparar_migracao.py --origem ~/trabalho2/.env --matricula 12621CBS201 --volume orthocrud_dados
sudo docker volume inspect orthocrud_dados --format '{{.Name}}'
sudo docker compose config --quiet
sudo docker compose build
)
```

Se qualquer comando falhar, pare nessa etapa: a instalação antiga permanece
rodando. Se a pasta de destino já existir, confira o conteúdo antes de usá-la;
não a apague automaticamente.

O preparador copia a configuração privada, preservando chave de sessão,
preferência de cadastro, cookies e chave NVD. Exige a porta calculada, cria o
novo `.env` com permissão 600 e recusa sobrescrever um arquivo existente.
Define `COMPOSE_FILE=compose.yaml:compose.volume-existente.yaml`; assim os comandos
normais de Compose usam o volume antigo como externo. Não publique esse `.env`.

O volume não é renomeado nem copiado para uma base vazia. O padrão obrigatório é
aplicado ao diretório, repositório, projeto, container e imagem; o nome do volume
legado fica documentado para preservar os dados.

## 3. Fazer backup consistente antes da troca

Confirme que a imagem nova foi construída. No servidor:

```bash
(
set -eu
cd ~/trabalho2
sudo docker compose stop inventario
umask 077
PASTA_BACKUP="$HOME/backup_orthocrud_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$PASTA_BACKUP"
sudo docker compose cp inventario:/dados/. "$PASTA_BACKUP/"
cp .env "$PASTA_BACKUP/env-legado"
sudo chown -R "$(id -u):$(id -g)" "$PASTA_BACKUP"
python3 - "$PASTA_BACKUP" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
ativos = json.loads((p / 'vulnerabilidades.json').read_text())
contas = json.loads((p / 'usuarios.json').read_text())
if not isinstance(ativos, list) or not isinstance(contas, dict):
    raise SystemExit('Formato de backup inesperado; não avance.')
print('Backup validado:', len(ativos), 'ativos e', len(contas), 'contas.')
print('Pasta:', p)
PY
)
```

Anote o caminho e as contagens. Se o backup falhar, não inicie a versão nova:
execute `sudo docker compose start inventario` nesta pasta antiga e investigue.
Esse backup contém hashes de senha e configuração privada; mantenha-o restrito.

## 4. Iniciar a versão padronizada

```bash
(
set -eu
cd ~/trab02_2026_2_12621cbs201
sudo docker compose up -d --wait --wait-timeout 220
sudo docker compose ps
curl --fail http://127.0.0.1:2201/healthz
sudo docker compose ps -q inventario | xargs -r sudo docker inspect --format '{{.Name}} | imagem={{.Config.Image}} | volumes={{json .Mounts}}'
sudo docker compose exec -T inventario python - <<'PY'
import json, os, importlib.metadata
with open(os.environ['INVENTARIO_ARQUIVO']) as f:
    ativos = json.load(f)
with open(os.environ['USUARIOS_ARQUIVO']) as f:
    contas = json.load(f)
print(len(ativos), 'ativos e', len(contas), 'contas.')
print('filelock:', importlib.metadata.version('filelock'))
PY
)
```

Compare as contagens com o backup. O nome do container deve ser
`trab02_2026_2_12621cbs201`, a imagem deve ter esse nome com a tag
`revisao-20261123`, e o volume deve continuar sendo `orthocrud_dados`.
Teste o login, um ativo existente e o cálculo de risco. O túnel permanece
`18080:127.0.0.1:2201`; não altere 2201 para 8000.

Após confirmar que há uma conta funcional, se o uso for restrito, configure
`PERMITIR_CADASTRO=false` no novo `.env` e aplique com `sudo docker compose up -d`.
O inventário é compartilhado entre contas; deixar cadastro aberto permite que
qualquer pessoa com acesso ao serviço crie uma conta e altere os registros.
Finalize esse ajuste antes de iniciar uma nova coleta de 24 horas.

## 5. Retornar à versão anterior em caso de falha

```bash
(
set -eu
cd ~/trab02_2026_2_12621cbs201
sudo docker compose stop inventario
cd ~/trabalho2
sudo docker compose start inventario
sudo docker compose ps
curl --fail http://127.0.0.1:2201/healthz
)
```

Não inicie as duas versões simultaneamente. As correções não alteram o formato
dos JSON; a versão anterior pode voltar a usar o mesmo volume. Dados novos
gravados pela nova versão permanecem no volume. Não restaure o backup por cima
de alterações novas sem decidir explicitamente qual estado deseja recuperar.

## 6. Registrar a implantação nova

Preserve os registros históricos de 03–04/11 e capture o estado do container
atual antes da troca. Após validar a versão nova, execute o procedimento de
monitoramento do [guia operacional](SERVIDOR.md), agora dentro de
`~/trab02_2026_2_12621cbs201`, usando uma pasta de evidências nova.

O script `monitorar_24h.py`, a porta 2201 e o serviço `inventario` continuam
iguais. O nome e a identidade do container mudam; uma coleta nova documenta a
versão efetivamente entregue. Não reconstrua, pare ou reinicie durante essa coleta.
