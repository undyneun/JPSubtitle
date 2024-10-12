FROM python:3.9-slim

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=utf-8 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    gnupg \
    git \
    make \
    xz-utils \
    file \
    sudo \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    mecab-utils && \
    rm -rf /var/lib/apt/lists/*

# 裝 chrome
RUN curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

RUN pip install mecab-python3 flask flask-cors openai selenium webdriver-manager pytubefix pytest

# 確保 mecabrc 在
RUN ln -sf /etc/mecabrc /usr/local/etc/mecabrc

WORKDIR /app
COPY . /app
COPY ./init.sh /app/init.sh
RUN chmod +x /app/init.sh
ENTRYPOINT ["/app/init.sh"]
