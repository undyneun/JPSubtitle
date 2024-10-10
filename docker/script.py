from flask import Flask, request, jsonify
from flask_cors import CORS
from pyModule import mecabMod, openaiMod, crawlerMod, pytubeMod, whisperjaxModJson
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
    normalForm = request.form['normalForm']
    origin = request.form['origin']
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
    # if len(api_key) > 100:
    #     text = openaiMod.whisper(audioPath, apiKey)
    # else:
    #     text = whisperjaxModJson.getResult(audioPath)
    result = whisperjaxModJson.getResult(audioPath)
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
    sys_prompt = r"""
        Translate the following Japanese or English content into Traditional Chinese romantically.
        Make sure the translation retains the original meaning of the sentence, while keeping the sentence structure and flow.
        The number of sentences before translation should be the same as after translation.
        Input context types may include Japanese anime, songs, idle chat etc.
        Don't add punctuation marks (like ，, 。, ！, ？ and so on) to the end of any sentence.

        Here are three examples:

        Input: "捕まえたdaydream 出遅れたストーリーと栄光が\nどこへ叫び唱えても\n荒れたトンネル 声もくぐれない\nだからサイレンス 灯すためと\n"
        Output: "將白日夢緊揣於手 可故事與榮耀卻來得太遲\n即便向著某處大聲疾呼\n聲音也穿越不過 那荒廢的隧道\n所以我將為了點亮這片寂靜而行"

        Input: "これ今画面見てない人めちゃくちゃかわいそうだなー\nま、茶番はこれくらいにして\nお手紙でもいきますか\n"
        Output: "此刻如果不看螢幕的人實在是太可憐了\n那麼，閒聊到此\n讓我們來讀讀來信吧"

        Input: "3は2のサックでサック2は2に2自身を元として加えたものだから\n3は0と1と2を含む集合なのだ\n正解ね\n"
        Output: "3是2的公者，公者2是將二自身加上\n因此3是包含0、1和2的集合呢\n正確"

        Below is the input, please output the answer with the format mentioned above:
    """
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