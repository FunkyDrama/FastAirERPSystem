FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app \
    IPYTHONDIR=/root/.ipython

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock /app/
RUN pip install --no-cache-dir poetry \
 && poetry install --no-interaction --no-root

COPY services/users_service /app/services/users_service
COPY scripts /app/scripts

RUN ipython profile create --profile=async && \
    mkdir -p /root/.ipython/profile_async/startup && \
    printf "c = get_config()\n" \
           "c.TerminalInteractiveShell.autoawait = True\n" \
           "c.TerminalInteractiveShell.loop_runner = 'asyncio'\n" \
           "c.InteractiveShellApp.exec_lines = [\n" \
           "    'import asyncio',\n" \
           "    'print(\\\"[ipython] autoawait on\\\")',\n" \
           "    'try:\\n import uvloop; asyncio.set_event_loop_policy(uvloop.EventLoopPolicy()); print(\\\"[ipython] uvloop policy set\\\")\\nexcept Exception as e:\\n print(\\\"[ipython] uvloop disabled:\\\", e)'\n" \
           "]\n" \
      >> /root/.ipython/profile_async/ipython_config.py

EXPOSE 8000

CMD ["python", "-m", "services.users_service.app.main"]
