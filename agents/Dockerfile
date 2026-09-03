FROM python:3.10-slim

WORKDIR /agents
COPY . /agents

RUN pip install --no-cache-dir fastapi uvicorn requests pydantic

EXPOSE 8120
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8120"]
