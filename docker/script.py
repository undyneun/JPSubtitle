from flask import Flask, request, jsonify
from flask_cors import CORS
from pyModule import mecabMod, openaiMod, crawlerMod, pytubeMod, whisperjaxMod
import os

app = Flask(__name__)
CORS(app, resources = {
    r"/parse": {"origins": "chrome-extension://iflcmnphhidflohhcokkbkpmdcdjined"},
    r"/translate": {"origins": "chrome-extension://iflcmnphhidflohhcokkbkpmdcdjined"},
    r"/crawler": {"origins": "chrome-extension://iflcmnphhidflohhcokkbkpmdcdjined"},
    r"/transcribe": {"origins": "chrome-extension://iflcmnphhidflohhcokkbkpmdcdjined"},
})
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/crawler', methods=['POST'])
def crawler():
    origin = normalForm = None
    if 'normalForm' in request.form:  normalForm = request.form['normalForm']
    if 'origin' in request.form:  origin = request.form['origin']
    if not origin or not normalForm:  
        return jsonify({"error": "No input provided"}), 400
    
    result, hasMeaning = crawlerMod.main(origin, normalForm)
    return jsonify({"result": result, "hasMeaning": hasMeaning}) 


@app.route('/parse', methods=['POST'])
def parse_text():
    if 'file' in request.files:
        file = request.files['file']
        input = "\n".join([line.decode('utf-8').strip() for line in file])
    if 'jpString' in request.form:
        jpString = request.form['jpString']
        input = jpString
    if not input:  
        return jsonify({"error": "No input provided"}), 400

    linesList = [mecabMod.getResult(line) for line in input.split("\n")]
    return jsonify(linesList)


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():    
    apiKey = request.form['apiKey']
    url = request.form['ytUrl']
    audioPath = pytubeMod.downloadYtMp3(url)
    if len(apiKey) > 100:
        result = openaiMod.whisper(audioPath, apiKey)
    elif apiKey == "test":
        result = [
            {"end": 2, "line": "テクノロジー", "start": 0},
            {"end": 4.92, "line": "ウィッグが絡まっちゃった", "start": 2.56},
            {"end": 5.9, "line": "助けて", "start": 4.98},
            {"end": 10.4, "line": "ピー", "start": 9.44},
            {"end": 17, "line": "君にとっては得だね", "start": 15.2},
            {"end": 22.26, "line": "良いものと良くないものでも判別するか良い", "start": 17.9},
            {"end": 23.24, "line": "ね良", "start": 22.26},
            {"end": 25, "line": "くないね良いね", "start": 23.24},
            {"end": 25.96, "line": "お", "start": -1},
            {"end": 27, "line": "前らとの思い出", "start": 25.96},
            {"end": 29, "line": "良いね", "start": 28.18},
            {"end": 31.68, "line": "シークレットレア", "start": 30.58},
            {"end": 34.12, "line": "行くか", "start": 33.06},
            {"end": 36, "line": "デリシャストリンクを飲みに", "start": 34.24},
            {"end": 38.08, "line": "いらっしゃいませ", "start": 37.08},
            {"end": 40, "line": "ご注文はお決まりでしょうか", "start": 38.08},
            {"end": 40.92, "line": "ん", "start": 40.58},
            {"end": 43.28, "line": "ダークストロングドラゴンで", "start": 41.64},
            {"end": 44.72, "line": "ないですね", "start": 43.92},
            {"end": 45.9, "line": "力", "start": 45.5},
            {"end": 49, "line": "エゴサでもしようかな", "start": 47.08},
            {"end": 53.78, "line": "頂天ちゃんとライオンってどっちが強いんかな", "start": 50.14},
            {"end": 57.1, "line": "馬鹿なモタクめ", "start": 55.16},
            {"end": 63.66, "line": "正解は頂天ちゃんのが強いでした", "start": 58.36},
            {"end": 66.3, "line": "補う", "start": 65.26},
            {"end": 68.78, "line": "最近伸びが良くない感じするな", "start": 66.3},
            {"end": 71.52, "line": "何が足りないんだろう", "start": 69.36},
            {"end": 73.18, "line": "萌えが足りないぜ", "start": 71.52},
            {"end": 74.78, "line": "もう一人の僕", "start": 73.18},
            {"end": 76.06, "line": "よし", "start": 75.54},
            {"end": 79.14, "line": "萌えをやるか", "start": 76.52},
            {"end": 79.86, "line": "無限", "start": 79.34},
            {"end": 82.12, "line": "にゃーん", "start": 81.5},
            {"end": 84.16, "line": "シャラーン", "start": 82.94},
            {"end": 87.12, "line": "キャッルーン", "start": 85.04},
            {"end": 90.26, "line": "みんな萌えてるか", "start": 88.26},
            {"end": 92.18, "line": "確かに", "start": 90.86},
            {"end": 96.66, "line": "なんか気分が良くないな", "start": 93.42},
            {"end": 98.58, "line": "ピーお薬いい", "start": 96.66},
            {"end": 102.26, "line": "ってこれおむすびやないかい", "start": 100.34},
            {"end": 103.72, "line": "シェー", "start": 102.78},
            {"end": 110.2, "line": "船長に咲く一輪の花", "start": 108.1},
            {"end": 113.37, "line": "今日は寿司を握るよ", "start": 111.36},
            {"end": 117.64, "line": "シャリにネタを乗せてに", "start": 114.3},
            {"end": 121.41, "line": "きにきにきにき", "start": 117.64},
            {"end": 123.45, "line": "す", "start": -1},
            {"end": 124.92, "line": "確", "start": -1},
            {"end": 126.1, "line": "かなこと", "start": 124.92},
            {"end": 129.44, "line": "火の鳥面白すぎる", "start": 126.56},
            {"end": 131.66, "line": "何事かと思うよね", "start": 129.78},
            {"end": 134.42, "line": "面白すぎて", "start": 131.66},
            {"end": 136.58, "line": "よっ面白い当初", "start": 134.42},
            {"end": 139.94, "line": "今日も火の鳥の話するよ", "start": 137.62},
            {"end": 143.94, "line": "オープニング曲のアレンジBGM", "start": 141.86},
            {"end": 148.66, "line": "ゲームのラスボスになったときのイメトレでもするか", "start": 144.88},
            {"end": 156.66, "line": "ツインテールA、Bを倒さないと厳しい奴になりたすぎる", "start": 152.22},
            {"end": 158.3, "line": "U型枠", "start": 156.66},
            {"end": 161.25, "line": "やる気出ないから", "start": 160.06},
            {"end": 164.94, "line": "アニメのエンディング風になろうかな", "start": 161.88},
            {"end": 169.43, "line": "ナンナンナンナン", "start": 165.94},
            {"end": 171.08, "line": "ヌーン", "start": 169.84},
            {"end": 174.38, "line": "フッフフフ", "start": 172.83}
        ]
    else:
        result = whisperjaxMod.getResult(audioPath)

    os.remove(audioPath)
    return jsonify(result)


@app.route('/translate', methods=['POST'])
def translate_text():    
    if 'file' in request.files:
        file = request.files['file']
        input = "\n".join([line.decode('utf-8').strip() for line in file])
    if 'jpString' in request.form:
        jpString = request.form['jpString']
        input = jpString
        
    api_key = request.form['apiKey']
    # 輸入的 \n 轉成 _ 的部分在 openaiMod.chatgpt()
    sys_prompt = (
        "請翻譯以下日文或英文句子為繁體中文，" + 
        "確保翻譯後的句子保留原句的意思，" +
        "使用_分隔句子，確保輸出的_數量與輸入的_數量相同，" +
        "輸入的上下文類型可能包括日本動畫、歌曲、閒聊等，" + 
        "請勿在任何句子的末尾添加標點符號（如，。！？等）。以下是三個例子：" +                  
        '輸入："捕まえたdaydream 出遅れたストーリーと栄光が_どこへ叫び唱えても_荒れたトンネル 声もくぐれない_だからサイレンス 灯すためと"' + 
        '輸出："將白日夢緊揣於手 可故事與榮耀卻來得太遲_即便向著某處大聲疾呼_聲音也穿越不過 那荒廢的隧道_所以我將為了點亮這片寂靜而行"' +        
        '輸入："これ今画面見てない人めちゃくちゃかわいそうだなー_ま、茶番はこれくらいにして_お手紙でもいきますか"' +        
        '輸出："此刻如果不看螢幕的人實在是太可憐了_那麼，閒聊到此_讓我們來讀讀來信吧"' +
        '輸入："3は2のサックでサック2は2に2自身を元として加えたものだから_3は0と1と2を含む集合なのだ_正解ね"' +
        '輸出："3是2的公者，公者2是將二自身加上_因此3是包含0、1和2的集合呢_正確"' +
        "以下是輸入，請確保按照以上的規則輸出："
    )
    if len(api_key) > 100:
        text = openaiMod.chatgpt(input, api_key, sys_prompt)
    else:
        text = input
        
    return text


@app.route('/test', methods=['GET'])
def test():
    return "今日は本音とたてまえについてお話をします。"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)