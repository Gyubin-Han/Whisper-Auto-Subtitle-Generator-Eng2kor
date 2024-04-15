FROM nvidia/cuda:12.3.1-base-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev \
    libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev liblzma-dev ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz && \
    tar -xf Python-3.12.2.tgz && \
    cd Python-3.12.2 && \
    ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make altinstall && \
    ln -s /usr/local/bin/python3.12 /usr/local/bin/python && \
    ln -s /usr/local/bin/python3.12 /usr/bin/python && \
    ln -s /usr/local/bin/pip3.12 /usr/local/bin/pip && \
    ln -s /usr/local/bin/pip3.12 /usr/bin/pip

WORKDIR /code

RUN wget https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root