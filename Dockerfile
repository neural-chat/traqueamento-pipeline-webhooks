# 📦 Imagem base
FROM python:3.12-slim

# ✂️ Evita que o pip guarde cache e bytecode desnecessários
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 🔧 Dependências do sistema (caso alguma lib nativa seja requisitada)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# 📂 Diretório de trabalho
WORKDIR /app

# 🔒 Primeiro copiamos apenas o requirements para aproveitar o layer cache
COPY requirements.txt .

# 📦 Instalamos as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# 🗂️ Copiamos o resto da aplicação
COPY src ./src



# 🔥 Porta exposta (ajuste se tiver API/metrics)
# EXPOSE 8000

# 🏁 Comando de inicialização
CMD ["celery", "-A", "src.celery_app", "worker", "--loglevel=info", "-Q", "traqueamento_payloads"]
