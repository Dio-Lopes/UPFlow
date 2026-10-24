# UPFlow — Versão CachyOS + Coreflux Dashboard (SciTeCh)

Projeto preparado para 3 pessoas: (A) código LoT + simulador Python em CachyOS; (B) painel Coreflux diretamente no browser em CachyOS; (C) PowerPoint em Windows.

**Não é necessária instalação local de Coreflux nem Docker** quando todos usam o broker Enterprise da equipa na cloud.

**Dados inteiramente simulados.** Capacidades no `config/venues.json` são exemplos, não números oficiais. Ocupação de lugares sentados != comprimento da fila ou tempo de espera. Não usar os números como informação ao público sem validação.

## Primeira utilização após mudança do nome

- **Usar esta pasta e este ZIP como a única versão de referência.** Se já criaram `.venv` na pasta antiga, criem um novo na pasta atual com os comandos abaixo. Não mover a pasta `.venv` entre projetos.
- Em Python, todos os comandos usam `python -m upflow.*`; em MQTT, todos os tópicos começam por `upflow/v1/`.
- No broker da cloud, criar/instalar a Action `UPFlowProcessReading` e o painel `UPFlowDashboard` deste pacote. O que estiver publicado com nomes ou tópicos antigos **não muda automaticamente**: após confirmar a versão nova, desativar/remover apenas os recursos antigos da equipa para evitar duplicação/confusão.
- Avisar os três membros para não misturarem prefixos MQTT. Não incluir o ficheiro `.env` na partilha nem no GitHub.

## Trabalho comum — tópicos MQTT

- Entrada: `upflow/v1/{campus}/{espaco}/raw/reading`
- Payload JSON: `{"occupied":45,"capacity":90,"observed_at":"2026-10-24T09:30:00Z","source":"demo_simulator"}`
- Saídas: `upflow/v1/{campus}/{espaco}/processed/percentage`, `.../processed/status`, `.../processed/occupied`, `.../processed/capacity`, `.../processed/observed_at`
- `status`: `quiet` (<50%), `moderate` (50%-<80%), `busy` (>=80%); `invalid` indica valor inválido.

## Pessoa A — Programação Coreflux e Python, CachyOS

### Dependências

Se já há `python`, `git` e `unzip`, **não reinstalar**. Verificar: `python --version && git --version && unzip -v | head -1`.

Se faltar alguma ferramenta: `sudo pacman -Syu --needed python python-pip git unzip` (pode atualizar o sistema; evitar desnecessariamente durante a hackathon).

No terminal na pasta `UPFlow_CachyOS_Coreflux`:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Este método chama diretamente o Python do venv e não requer ativá-lo: funciona com **Fish**, Bash ou Zsh. Se quiser ativar: Fish `source .venv/bin/activate.fish`; Bash/Zsh `source .venv/bin/activate`.

Editar `.env` com host, password e outros parâmetros do broker MQTT da equipa. `MQTT_HOST` é o **hostname do broker**, não a URL do Hub `hub.eu1.coreflux.cloud`. Nunca fazer commit de `.env` ou partilhar passwords. A configuração de teste usa `mqtts://`, porta `8883`, `admin` e a password da equipa.

### Action LoT

1. Abrir `https://hub.eu1.coreflux.cloud`, entrar e ligar ao broker da equipa.
2. Abrir **LoT Editor** e criar notebook UPFlow.
3. Abrir `lot/01-upflow-process-reading.lot` e copiar o código desde `DEFINE ACTION` até ao fim.
4. Executar a célula LoT, ler as mensagens de sucesso/erro.
5. **Não confiar que compila sem testes**: ainda não foi validado neste broker de competição.

### Testar o simulador

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m upflow.simulator --once
# Depois de ver mensagens num Data Viewer, testar continuamente:
.venv/bin/python -m upflow.simulator
```

O simulador publica de 5 em 5 segundos em `.../raw/reading`. Deverão aparecer as saídas `.../processed/percentage` na Coreflux caso a Action funcione.

Publicação manual de um valor:

```sh
.venv/bin/python -m upflow.publisher --venue bar_minas --occupied 80
```

Só uma pessoa deve executar o simulador de cada vez. Para interromper, `Ctrl+C`.

## Pessoa B — Dashboard Coreflux, CachyOS

**Não é necessário Python, pip, Docker, Node.js ou VS Code**: apenas browser moderno e credenciais válidas da Coreflux Hub/cloud.

1. No Hub, ligar-se ao **mesmo broker** da Pessoa A.
2. Abrir **Dashboards → Create new panel**.
3. Abrir `panels/01-upflow-dashboard.lot` e copiar a definição `DEFINE PANEL` para o editor do painel.
4. Guardar; verificar se aparecem gauges de 0 a 100% e um gráfico `realtime-chart`.
5. Para testar sem aguardar o simulador, publicar `35`, `65`, `90` nos respetivos tópicos `.../processed/percentage` através do Data Viewer. São apenas mensagens de teste: parar estes publishers quando a Pessoa A começar.
6. A seguir, apontar exclusivamente para os tópicos `processed/*` da Action real.
7. Adicionar opcionalmente indicadores `occupied` / `capacity`, timestamps e outros gráficos, verificando a sintaxe na documentação.

Atenção: os gauges podem continuar a mostrar o último valor após parar a emissão. **Não chamar a um valor antigo "ao vivo"**: prever um estado sem dados recentes antes de qualquer piloto real. O modo `PUBLIC` e a função Broadcast podem divulgar informação; verificar permissões antes de partilhar links.

Docs: https://docs.coreflux.org/latest/quick-start/building-dashboards

## Pessoa C — PowerPoint, Windows

Precisa apenas de **PowerPoint ou ferramenta compatível**, acesso à documentação e capturas de ecrã fornecidas pelos colegas. **Sem Docker, Python, MQTT ou Coreflux local**.

Seis slides (objetivo aproximado: 5 min, confirmar limite oficial):
1. Problema: não se sabe a ocupação das cantinas antes de lá chegar.
2. Solução: UPFlow, várias cantinas num painel.
3. Como funciona: Python/sensores futuros → MQTT → Coreflux LoT → Dashboard.
4. Demonstração com **dados simulados** (capturas + vídeo de reserva se houver tempo).
5. Futuro: integração possível com app UNI/SASUP, outras faculdades, sensores reais; não afirmar que existe já integração.
6. Impacto, limitações e roadmap: validar lotação real, medir filas, API, segurança, persistência.

## Diagnóstico rápido

- Action com erro: guardar erro exato do LoT Editor para corrigir sintaxe.
- Python não liga: conferir `MQTT_HOST` (broker, não Hub), TLS/8883, username e password. Não publicar credenciais.
- Dashboard sem valor: confirmar no Data Viewer se `.../processed/percentage` recebe um **número**. Se só `raw/reading` recebe JSON, a Action de processamento não está a publicar.
- Chart vazio no início: aguardar várias mensagens novas; histórico do gráfico não substitui base de dados persistente.
- `python -m venv` com falha: conferir Python >= 3.10 e espaço em disco.

## Garantias de teste

O código Python pode ser validado localmente com os testes unitários. A Action LoT e o painel foram adaptados da sintaxe oficial da documentação, mas **não foram executados no vosso broker**. Testá-los antes da apresentação.
