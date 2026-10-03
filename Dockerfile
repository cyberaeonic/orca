FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN npm install -g opencode-ai
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY bot.py opencode_bridge.py ./
ENV PATH="/opt/venv/bin:${PATH}" PYTHONUNBUFFERED=1 OPENCODE_WORKDIR=/workspace
RUN useradd --create-home bot && mkdir /workspace && chown bot:bot /workspace
USER bot
CMD ["python", "bot.py"]
