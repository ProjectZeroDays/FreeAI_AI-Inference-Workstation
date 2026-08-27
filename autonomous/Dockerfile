FROM python:3.10-slim

WORKDIR /stack
COPY . /stack

RUN pip install --no-cache-dir fastapi uvicorn requests pydantic

ENV WORKSPACES_DIR=/stack/workspaces
VOLUME ["/stack/workspaces"]

EXPOSE 8050
CMD ["uvicorn", "autonomous.api:app", "--host", "0.0.0.0", "--port", "8050"]
