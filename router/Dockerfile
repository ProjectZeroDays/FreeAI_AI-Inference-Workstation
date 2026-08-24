FROM python:3.10-slim

WORKDIR /router
COPY . /router

RUN pip install --no-cache-dir flask requests

EXPOSE 8010
CMD ["python3", "router.py"]
