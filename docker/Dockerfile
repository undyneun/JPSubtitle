FROM python:3.9-slim

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8
ENV DEBIAN_FRONTEND=noninteractive

# 更新 apt 資料庫，安裝所需的依賴
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 添加 Google Chrome 的官方 PPA
RUN curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y \
    google-chrome-stable \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    xz-utils \
    file \
    sudo \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    mecab-utils \
    && apt-get clean

RUN pip install mecab-python3 flask flask-cors openai selenium webdriver-manager pytubefix

# 從 GitHub 克隆 mecab-ipadic-NEologd 並安裝
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git /opt/mecab-ipadic-neologd \
    && cd /opt/mecab-ipadic-neologd \
    && ./bin/install-mecab-ipadic-neologd -n -y

# 獲取 mecab-ipadic-neologd 的安裝路徑
RUN NEOLOGD_PATH=$(echo `mecab-config --dicdir`"/mecab-ipadic-neologd") \
    && echo "export MECAB_DICDIR=${NEOLOGD_PATH}" >> ~/.bashrc \
    && export MECAB_DICDIR=${NEOLOGD_PATH}

# 確保 mecabrc 文件存在
RUN ln -sf /etc/mecabrc /usr/local/etc/mecabrc

WORKDIR /app
COPY . /app
ENTRYPOINT ["bash", "-c", \
            "export MECAB_DICDIR=$(mecab-config --dicdir)/mecab-ipadic-neologd && python script.py"]
