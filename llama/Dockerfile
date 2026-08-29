# syntax=docker/dockerfile:1.4
# CPU-only build — avoids CUDA driver requirement on CI runners
FROM ubuntu:24.04 AS builder
RUN apt-get update && apt-get install -y git build-essential cmake && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/ggerganov/llama.cpp.git /src \
    && cmake -S /src -B /src/build \
    && cmake --build /src/build --config Release -j "$(nproc)"

FROM ubuntu:24.04
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/build/bin/llama-server /usr/local/bin/llama-server
ENV LLAMA_SERVER_BIN=/usr/local/bin/llama-server
WORKDIR /stack
COPY launch-llama.sh .
RUN chmod +x launch-llama.sh
ENTRYPOINT ["./launch-llama.sh"]
