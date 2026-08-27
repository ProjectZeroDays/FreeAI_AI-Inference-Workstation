FROM python:3.10-slim

WORKDIR /dashboard
COPY . /dashboard

RUN pip install --no-cache-dir flask requests

EXPOSE 8030
CMD ["python3", "backend.py"]
