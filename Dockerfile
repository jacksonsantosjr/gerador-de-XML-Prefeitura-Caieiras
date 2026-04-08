FROM python:3.12-slim

WORKDIR /code

COPY ./backend/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia tudo da pasta backend
COPY ./backend /code/

# Variáveis globais úteis para contêineres Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expor porta padrão do FastAPI no Hugging Face Spaces / Render
EXPOSE 8000

# Script para iniciar o servidor Uvicorn atrelado à porta 8000
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
