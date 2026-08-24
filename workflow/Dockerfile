FROM python:3.10-slim

WORKDIR /workflow
COPY . /workflow

RUN pip install --no-cache-dir fastapi uvicorn requests pydantic

EXPOSE 8040
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8040"]
