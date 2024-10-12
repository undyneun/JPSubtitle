#!/bin/bash

# 合併文件
if [ ! -f /app/mecab-ipadic-neologd/sys.dic ]; then
  cat /app/mecab-ipadic-neologd/sys.dic.part-* > /app/mecab-ipadic-neologd/sys.dic
  rm /app/mecab-ipadic-neologd/sys.dic.part-*
fi

# 啟動應用
exec python script.py