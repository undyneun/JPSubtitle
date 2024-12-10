# JPSubtitle
可以邊看 Youtube 邊學日文的擴充功能 :)  
(需要有 docker)

範例影片

https://github.com/user-attachments/assets/5ebb538e-834c-4f9d-954a-f3400d3b29cd

按下擴充功能按鈕會跳出的視窗，除了用 whisper 轉錄影片字幕外還能自行上傳 (影片不知道為甚麼截不到)

![1](https://github.com/user-attachments/assets/12045770-c7d0-47fc-98bc-9935da518c08)

# 檔案結構
```bash
.
├─.github
│  └─workflows
├─docker                      
│  ├─script.py                # flask 框架的伺服器
│  ├─cache                    # Mazii 網站結果的緩存
│  ├─mecab-ipadic-neologd     # mecab 套件的字典檔
│  \─pyModule
│           crawlerMod.py     # Mazii 網站查詢日文意思和例句
│           mecabMod.py       # mecab 套件來日文分詞、提供讀音
│           openaiMod.py      # 要輸入 apikey 使用 gpt 和 whisper 
│           pytubeMod.py      
│           whisperjaxMod.py
│           __init__.py
└─extension                   # 在 chrome 的 擴充功能/載入未封裝項目 使用
   └─icons
```



