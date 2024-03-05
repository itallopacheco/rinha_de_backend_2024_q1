FROM python:3.11-slim-bookworm
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR app/
COPY . .

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

EXPOSE 8000
CMD [ "uvicorn","rinha_capivara.app:app","--host", "0.0.0.0" ]