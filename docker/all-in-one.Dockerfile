# All-in-one FreeAI stack image (supervisord inside).
# Multi-stage: 60% smaller — devel only for llama build.
# CUDA 13 (llmv parity) - host driver >= 580 required.
FROM nvidia/cuda:13.0.1-devel-ubuntu24.04 AS llama-builder
RUN apt-get update && apt-get install -y git build-essential cmake && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/ggerganov/llama.cpp.git /src \
    && (cmake -S /src -B /src/build -DGGML_CUDA=ON && cmake --build /src/build -j "$(nproc)") \
    || (cmake -S /src -B /src/build -DGGML_CUDA=OFF && cmake --build /src/build -j "$(nproc)")

FROM nvidia/cuda:13.0.1-runtime-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv supervisor curl && rm -rf /var/lib/apt/lists/*

WORKDIR /stack
COPY . /stack
RUN python3 -m venv /stack/venv \
    && /stack/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /stack/venv/bin/pip install --no-cache-dir -r /stack/requirements.txt

COPY --from=llama-builder /src/build/bin/llama-server /usr/local/bin/llama-server
ENV LLAMA_SERVER_BIN=/usr/local/bin/llama-server
COPY docker/supervisord-all.conf /etc/supervisor/conf.d/freeai.conf

VOLUME ["/stack/models", "/stack/workspaces"]
EXPOSE 8010 8020 8030 8040 8050 9001
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/freeai.conf"]
