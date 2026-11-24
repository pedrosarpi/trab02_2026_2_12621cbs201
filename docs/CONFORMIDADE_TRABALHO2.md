# Conformidade — Trabalho 02, entrega em 27/11/2026

Esta página descreve o código e as evidências disponíveis. A aprovação acadêmica
e a aceitação das evidências de implantação cabem ao docente.

| Requisito | Implementação e evidência |
| --- | --- |
| Ativos como objetos individuais (20%) | `app/equipamentos.py`: classe abstrata `Equipamento`, cinco subclasses, fábrica `criar`, reconstrução em `from_dict` e composição com vulnerabilidades e dependências. |
| Persistência em array JSON (20%) | `app/dados.py`: `ArmazenamentoJSON`; `app/persistencia.py`: escrita atômica. Um objeto JSON por ativo; vínculos e tipos são recuperados na leitura. |
| Container por pelo menos 24 horas (45%) | `Dockerfile`, `compose.yaml`, `/healthz` e `scripts/monitorar_24h.py`. `docker-logs/` contém 1.440 amostras da instalação de 03–04/11/2026, sem falhas ou reinícios detectados. Uma atualização exige registrar a nova implantação separadamente. |
| Risco efetivo e invertibilidade (15%) | `app/riscos.py`: monta M, v, A e b, verifica posto e condicionamento de I−A, resolve com `numpy.linalg.solve` e confere o resíduo. Testes incluem cenário manual, ciclo invertível e matriz singular. |
| Requisitos herdados do Trabalho 01 | CRUD, busca por ID/nome, cinco tipos em Enum, vulnerabilidades e dicionário de ativos implementados. Branches e merges estão no histórico Git, que um ZIP não transporta. |

## Nomenclatura e dados

Em uma instalação acadêmica nova, `python3 scripts/configurar.py --matricula SUA_MATRICULA`
calcula o identificador `trab02_2026_2_` seguido da matrícula em minúsculas e a porta
`2000 + os três últimos dígitos`. Use a porta atribuída pelo docente.

Diretório e repositório Git devem receber o mesmo identificador. O Compose usa-o
para projeto, container e imagem. A aplicação continua se chamando OrthoCRUD na
interface. O serviço lógico permanece `inventario`, para manter os comandos de
operação e monitoramento.

Há um volume nomeado montado em `/dados`. A ausência de uma pasta versionada
`data/` não significa ausência de persistência: os JSON reais devem permanecer
fora do Git. No uso local, o programa usa `dados/`, com compatibilidade para
arquivos antigos na raiz. Não renomeie esses caminhos sem uma migração explícita.

Para a instalação legada, siga [o procedimento de atualização](ATUALIZACAO_2026_11_23.md).
O volume `orthocrud_dados` pode ser reutilizado como externo: os dados permanecem
isolados e o novo projeto recusa iniciar caso esse volume não exista.

## Organização e decisões que devem ser explicadas

- Domínio: `equipamentos.py` e `modelos.py`.
- Inventário e persistência: `inventario.py`, `dados.py` e `persistencia.py`.
- Transações da web: `servicos.py`, com trava e revisão para impedir perda de atualização.
- Integração e avaliação: `consulta_cve.py`, `seguranca.py` e `riscos.py`.
- Interfaces: `web.py` e templates; `main.py`, `menus.py` e utilidades de terminal.

A separação atual é feita por módulos, ainda sem pacotes por camada, protocolo
de repositório e implementações JSON/memória intercambiáveis. Essas são evoluções
pedidas por cards de estudo do Trello; não se deve afirmar que SOLID está
integralmente atendido.

O risco usa uma coluna por ocorrência de vulnerabilidade. Todas as ocorrências
entram no cálculo, inclusive as corrigidas, conforme a decisão documentada do
modelo literal. O resultado pode ultrapassar 10; não é uma nota CVSS nem uma
probabilidade. O cadastro de dependências limita a soma de cada linha a menos de 1;
dados importados fora dessa condição são diagnosticados pelo cálculo.

## Demonstração de cinco minutos

1. 0:00–0:45: objetivo, login e cadastro de ativo; mostrar a subclasse e a fábrica.
2. 0:45–1:45: cadastrar vulnerabilidade, consultar CVE e calcular um vetor CVSS.
3. 1:45–3:00: apresentar três ativos e dependências, risco próprio e efetivo;
   localizar a verificação de invertibilidade e o `solve`.
4. 3:00–4:00: mostrar o JSON como array e os testes de gravação/recarga e singularidade.
5. 4:00–5:00: `docker compose ps`, volume, `/healthz` e evidências reais de 24 horas.

Tenha um exemplo salvo para a demonstração; a consulta externa pode ficar
indisponível. Não reinicie o container durante uma coleta de disponibilidade.
