FROM python:3.11-slim

WORKDIR /app

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" tlacuilo && \
    useradd -u "${UID}" -g tlacuilo -m tlacuilo

RUN apt-get update && apt-get install -y git curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

USER tlacuilo
WORKDIR /home/tlacuilo/app

COPY --chown=tlacuilo:tlacuilo requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

ENV PATH="/home/tlacuilo/.local/bin:${PATH}"

# In development, code is mounted via volume
# COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
