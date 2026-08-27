# syntax=docker/dockerfile:1.4
# CUDA 13 (llmv parity) - requires host driver >= 580
FROM nvidia/cuda:13.0.1-devel-ubuntu24.04 AS builder
RUN apt-get update && apt-get install -y git build-essential cmake && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/ggerganov/llama.cpp.git /src \
    && cmake -S /src -B /src/build -DGGML_CUDA=ON \
    && cmake --build /src/build --config Release -j "$(nproc)"

FROM nvidia/cuda:13.0.1-runtime-ubuntu24.04
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/build/bin/llama-server /usr/local/bin/llama-server
ENV LLAMA_SERVER_BIN=/usr/local/bin/llama-server
WORKDIR /stack
COPY launch-llama.sh .
RUN chmod +x launch-llama.sh
ENTRYPOINT ["./launch-llama.sh"]
