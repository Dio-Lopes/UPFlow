# UPFlow

**Smart campus food-space occupancy — SciTeCh'26 | Builders of Things**

O **UPFlow** é uma prova de conceito que monitoriza e apresenta a **ocupação estimada de espaços de alimentação universitários**, ajudando estudantes a comparar alternativas antes de se deslocarem. Foi desenvolvido na Hackathon SciTeCh'26, com **Coreflux** como plataforma central de comunicação e processamento de dados.

> **Prova de conceito:** todas as leituras de ocupação são **simuladas**. O sistema não mede neste momento a ocupação real das cantinas.

## O problema

Um estudante com pouco tempo entre aulas pode chegar a uma cantina sem saber se encontrará lugar ou se outra opção estará menos ocupada. O UPFlow procura transformar leituras dispersas de diferentes espaços em informação fácil de consultar.

## A solução e o que funciona

O fluxo principal do protótipo é:

```text
Sensores virtuais (Python)
        │  MQTT · JSON: occupied, capacity, observed_at
        ▼
Coreflux Cloud Enterprise (broker MQTT)
        │  Action LoT: UPFlowProcessReading
        │  valida e calcula a ocupação
        ▼
Tópicos MQTT processados
        │  occupied · capacity · percentage · status · observed_at
        ▼
Dashboard Coreflux
        └── indicadores de ocupação e visualização dos espaços
```

**Fluxo implementado:**
1. O simulador Python publica leituras MQTT das três cantinas.
2. A Action `UPFlowProcessReading` recebe as leituras, valida-as e calcula a percentagem e o estado.
3. A Coreflux publica os resultados nos tópicos `processed/*`.
4. Os painéis da Coreflux subscrevem os resultados para apresentar os indicadores e gráficos.

Por exemplo, `93` lugares ocupados em `120` resulta em `77,5%` e estado `moderate`.

**Dashboard implementada:** cinco painéis (`UPFlowHome`, `UPFlowFEUP`, `UPFlowBarMinas`, `UPFlowCantinaEngenharia` e `UPFlowGrillEngenharia`), com navegação entre páginas, gauges e gráficos de linhas em tempo real nas páginas de detalhe. O código-fonte está em [`lot/panels/`](lot/panels/) e a exportação em [`notebooks/UPFlow.lotnb`](notebooks/UPFlow.lotnb).

**Favoritos:** existem componentes demonstrativos ligados a tópicos MQTT partilhados; ainda não são preferências personalizadas por utilizador. Os gráficos apresentam leituras em tempo real, não um histórico persistente da semana anterior.

## Tecnologias

- **Python 3.10+**: simulação de leituras de ocupação e publicações MQTT.
- **Paho MQTT**: cliente para comunicação com o broker.
- **Coreflux + LoT (Language of Things)**: receção, validação, processamento e publicação dos dados.
- **Coreflux Dashboard Manager**: apresentação dos indicadores ligados aos tópicos processados.

## Espaços incluídos no protótipo

| Espaço | Capacidade no protótipo | Origem da capacidade |
| --- | ---: | --- |
| Bar de Minas / Cafetaria FEUP | 90 | **Valor fictício provisório**; por confirmar |
| Cantina de Engenharia (SASUP) | 324 | Informação publicada pelos SASUP |
| Grill de Engenharia | 120 | Informação publicada pelos SASUP |

A configuração está em [`config/venues.json`](config/venues.json). Os números de pessoas presentes são sempre simulados.

## Estrutura do repositório

```text
UPFlow/
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── config/
│   └── venues.json
├── upflow/
│   ├── __init__.py
│   ├── settings.py
│   ├── mqtt_client.py
│   ├── publisher.py
│   └── simulator.py
├── lot/
│   ├── actions/
│   │   └── UPFlowProcessReading.lot
│   └── panels/
│       ├── UPFlowHome.lot
│       ├── UPFlowFEUP.lot
│       ├── UPFlowBarMinas.lot
│       ├── UPFlowCantinaEngenharia.lot
│       └── UPFlowGrillEngenharia.lot
├── notebooks/
│   └── UPFlow.lotnb
└── tests/
    └── test_core.py
```

## Executar o projeto

### 1. Preparar Python 

A partir da raiz do repositório:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edita o ficheiro `.env` com as credenciais do **broker MQTT** ao qual tens acesso:

```dotenv
MQTT_HOST=HOST_DO_BROKER
MQTT_PORT=8883
MQTT_TLS=true
MQTT_USERNAME=admin
MQTT_PASSWORD=COLOCAR_LOCALMENTE
```

### 2. Instalar o processamento na Coreflux

1. Abre o [Coreflux Hub](https://hub.eu1.coreflux.cloud/) e liga-te ao teu broker.
2. No **LoT Editor**, abre/cria um notebook e adiciona uma célula LoT.
3. Copia a definição do ficheiro [`lot/actions/UPFlowProcessReading.lot`](lot/actions/UPFlowProcessReading.lot).
4. Faz **Deploy** da Action `UPFlowProcessReading` e confirma que aparece em **Broker Runtime → Actions**.
5. No **Data Viewer** ou **Action Console**, verifica as mensagens e as execuções.

**Importante:** alterações feitas diretamente no Hub não são guardadas automaticamente no ficheiro `.lot` do GitHub. Antes da entrega, compara o código no broker com o código no repositório.

### 3. Executar os sensores virtuais

Uma leitura por cantina:

```bash
.venv/bin/python -m upflow.simulator --once
```

Simulação contínua, com atualizações a cada 5 segundos:

```bash
.venv/bin/python -m upflow.simulator --interval 5
```

Publicação manual de um cenário controlado:

```bash
.venv/bin/python -m upflow.publisher --venue cantina_engenharia --occupied 300
```

### 4. Abrir a dashboard Coreflux

1. No [Coreflux Hub](https://hub.eu1.coreflux.cloud/), ligar ao broker da equipa.
2. No **LoT Editor**, abrir ou importar [`notebooks/UPFlow.lotnb`](notebooks/UPFlow.lotnb), que contém a Action e os cinco painéis. Alternativamente, consultar as definições individuais em [`lot/panels/`](lot/panels/).
3. Confirmar que a Action e os cinco painéis estão presentes em **Broker Runtime**, sem redeploy desnecessário num broker já configurado.
4. Abrir a dashboard `UPFlowHome`, navegar para `UPFlowFEUP` e depois para as páginas das cantinas.
5. Publicar uma nova leitura e confirmar a atualização dos gauges e gráficos em tempo real.

## Contrato MQTT

O UPFlow utiliza a convenção:

```text
upflow/v1/{campus}/{espaco}/raw/reading
upflow/v1/{campus}/{espaco}/processed/occupied
upflow/v1/{campus}/{espaco}/processed/capacity
upflow/v1/{campus}/{espaco}/processed/percentage
upflow/v1/{campus}/{espaco}/processed/status
upflow/v1/{campus}/{espaco}/processed/observed_at
```

Exemplo de publicação de entrada:

```json
{
  "occupied": 162,
  "capacity": 324,
  "observed_at": "2026-10-24T11:00:00Z",
  "source": "demo_simulator"
}
```

A Action LoT valida `capacity > 0` e `0 <= occupied <= capacity`, calcula `occupied / capacity * 100` e classifica a ocupação:

| Percentagem | `status` |
| --- | --- |
| Menos de 50% | `quiet` |
| De 50% a menos de 80% | `moderate` |
| 80% ou mais | `busy` |
| Leitura inválida | `invalid` |

A Action utiliza o wildcard MQTT `upflow/v1/+/+/raw/reading`, pelo que o mesmo processamento se aplica a diferentes campus e espaços que respeitem o contrato.

## Testes e demonstração

Executar os testes unitários Python:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

**Demonstração sugerida:**

1. Abrir a dashboard e o Data Viewer no broker da equipa.
2. Parar temporariamente o simulador para um teste controlado.
3. Publicar uma leitura de `300` ocupados na Cantina de Engenharia.
4. Confirmar `92,59%` e `busy` nos tópicos processados e na dashboard.
5. Publicar outra leitura com `80` ocupados; confirmar `24,69%` e `quiet`.
6. Voltar a iniciar o simulador e observar atualizações em tempo real.

O teste de integração com a dashboard deve ser repetido após alterações à definição do painel. Guardar capturas ou gravação curta da demonstração é útil como alternativa à execução ao vivo.

## Limitações e próximos passos

### Limitações da prova de conceito

- As ocupações são **simuladas**; não há sensores reais instalados nas cantinas.
- A **ocupação** não equivale ao **comprimento da fila** nem ao **tempo de espera**.
- Os gráficos de linhas mostram dados em tempo real; não existe armazenamento histórico persistente da semana anterior.
- A ausência de novas leituras deve ser tratada como dados possivelmente desatualizados, não como ocupação zero.
- Os toggles de favoritos da demonstração usam tópicos MQTT partilhados; não guardam preferências individuais.
- A funcionalidade de cantinas favoritas não funciona atualmente, mas, de acordo com profissionais da Coreflux, pode ser mesmo um bug da plataforma!

### Visão futura (não implementada neste MVP)

- Contagem com sensores físicos, com testes de precisão e privacidade.
- Fotografias, ementas e horários atualizados em cada página de detalhe.
- Favoritos personalizados e persistentes por utilizador (até três), recomendações por faculdade, orçamento e alimentação.
- Histórico persistente, tendências por dia/semana e estimativa de filas baseada em medições adequadas.
- Integração, mediante acordo, com a app UNI e fontes de informação dos SASUP.
- Expansão outras faculdades da Universidade do Porto e, possívelmente, outras instituições.

## Documentação e fontes

- [Documentação da Coreflux](https://docs.coreflux.org/latest)
- [SASUP — Cantinas](https://www.up.pt/portal/pt/sasup/alimentacao/cantinas/)

---

**UPFlow · SciTeCh'26 — Builders of Things**  
*Conceito demonstrado com dados simulados; o projeto não é um serviço oficial da Universidade do Porto, FEUP, FCUP ou SASUP.*
