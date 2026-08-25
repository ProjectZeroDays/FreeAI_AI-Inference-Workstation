# All-in-one Tokugawa stack image (supervisord inside).
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git curl wget build-essential cmake pkg-config libcurl4-openssl-dev \
    python3 python3-pip python3-venv supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /stack
COPY . /stack

RUN python3 -m venv /stack/venv \
    && /stack/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /stack/venv/bin/pip install --no-cache-dir -r /stack/requirements.txt

# llama.cpp CUDA build (skips gracefully to CPU if nvcc mismatch)
RUN git clone --depth 1 https://github.com/ggerganov/llama.cpp.git /opt/llama.cpp \
    && (cmake -S /opt/llama.cpp -B /opt/llama.cpp/build -DGGML_CUDA=ON \
        && cmake --build /opt/llama.cpp/build --config Release -j "$(nproc)") \
    || (cmake -S /opt/llama.cpp -B /opt/llama.cpp/build -DGGML_CUDA=OFF \
        && cmake --build /opt/llama.cpp/build --config Release -j "$(nproc)")
ENV LLAMA_SERVER_BIN=/opt/llama.cpp/build/bin/llama-server

COPY docker/supervisord-all.conf /etc/supervisor/conf.d/tokugawa.conf

VOLUME ["/stack/models", "/stack/workspaces"]
EXPOSE 8010 8020 8030 8040 8050 9001

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/tokugawa.conf"]
