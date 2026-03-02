# 🧠 Traqueamento de Webhooks

1. **Worker Celery**: processa tasks `save_webhook_event` e persiste os dados da mesma forma.


## 📁 Estrutura do Projeto

```bash

src/
├── db/                # MongoDB connection + TTL index
├── models/            # (reserva para schemas futuros)
├── mq/
│   └── rabbit.py      # Configurações e conexão RabbitMQ
├── pipe/              # (para futuras transformações em pipeline)
├── utils/
│   └── utils\_logs.py  # Logging visual dos payloads
├── workers/
│   └── celery\_app.py  # Worker Celery + Task principal
├── config.py          # Variáveis de ambiente
main.py                # Entrypoint do consumidor
Dockerfile             # Containerização
requirements.txt       # Dependências
.env                   # Configurações locais
README.md              # Este arquivo

```


```bash

## ⚙️ Tecnologias Usadas

- Python 3.11+
- [Celery](https://docs.celeryq.dev)
- [aio-pika](https://aio-pika.readthedocs.io/)
- MongoDB + TTL Index
- RabbitMQ (TOPIC exchange)
- Pytz + datetime
- pyfiglet (diversão nos logs!)

```

---

## 🧪 Exemplo de Payload

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "9876543210",
      "changes": [...]
    }
  ]
}
```

O campo `createdAt` é automaticamente adicionado pelo sistema no formato:

```json
"createdAt": "2025-07-02T10:45:00-03:00"
```

---

## 🚀 Rodando Localmente

### 1. Requisitos

* RabbitMQ com exchange `amq.topic`
* MongoDB rodando
* Python 3.11+
* Redis (se quiser rodar Celery com backend de resultados)

### 2. Instalação

```bash
pip install -r requirements.txt
```

### 3. Variáveis no `.env`

```env
RABBIT_URL=amqp://guest:guest@localhost/
MONGO_URI=mongodb://localhost:27017/
QUEUE_NAME=
TOPIC_KEY=
```


## 📦 Modo 2 – Celery Worker (`src/celery_app.py`)

Processa tasks enviadas pelo backend, gateway.

```bash
celery -A src.celery_app worker --loglevel=info -Q traqueamento_payloads
```

Isso:

* Garante a criação do índice TTL no startup.
* Usa o nome da task `"save_webhook_event"`.
* Persistente ao falhar (`autoretry_for`, `retry_backoff`).
* Imprime uma arte com `pyfiglet` como banner no log:


---

## 🧼 Sobre o TTL

O campo `createdAt` recebe um índice TTL com expiração de 36h:

```python
db.meta_payloads.createIndex(
  { "createdAt": 1 },
  { expireAfterSeconds: 129600 }  # 36 horas
)
```

---

## 📈 Logs Exemplo

```bash
📦  Novo webhook recebido
┌──────────────────────────────┐
│ object: whatsapp_business... │
│ id: 9876543210               │
└──────────────────────────────┘

✅ Doc 66f22b... salvo (expires ~36 h): 02/07 10:45
```

---

## 🧠 Casos de Uso

* Armazenar temporariamente eventos da API da Meta
* Acoplamento com pipelines ETL
* Histórico curto para debug de integrações
* Rastreamento de eventos em tempo real
* Pré-processamento para sistemas de automação

---

## 📌 Futuras Melhorias

* Adicionar validação com Pydantic
* Exportar para data lake (S3, BigQuery etc)
* Configuração de múltiplas exchanges
* Web interface para visualização dos eventos

---



## 🔗 Nome dos Fluxos do N8N

### 📋 Webhooks Configurados

* 🔴 **URL Principal** → `[Pipeline] Erros de resposta`
  * Usado para eventos de status `failed` e outros eventos padrão
  
* 🟢 **URL de Eventos Especiais** → `[Neural Chat] Eventos | Meta Ads`
  * Usado para eventos automáticos (`automatic_events`) para rastreamento de leads


Nome da Imagem : agencianeuron/traqueamentos-webhooks:0.0.2
