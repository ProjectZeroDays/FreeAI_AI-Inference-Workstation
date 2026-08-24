FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir vllm

WORKDIR /vllm
COPY launch-vllm.sh .
RUN chmod +x launch-vllm.sh

ENTRYPOINT ["./launch-vllm.sh"]
