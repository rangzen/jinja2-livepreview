FROM python:3.11-alpine

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY . /app

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

ENV PORT 9797
EXPOSE 9797

CMD ["python", "web.py"]
