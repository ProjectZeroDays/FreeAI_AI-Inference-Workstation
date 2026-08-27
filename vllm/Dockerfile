# CUDA 13 (llmv parity) - requires host driver >= 580
FROM nvidia/cuda:13.0.1-devel-ubuntu24.04

RUN apt-get update && apt-get install -y python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir vllm

WORKDIR /vllm
COPY launch-vllm.sh .
RUN chmod +x launch-vllm.sh

ENTRYPOINT ["./launch-vllm.sh"]
