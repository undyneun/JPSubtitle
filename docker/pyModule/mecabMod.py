import re
import os
from typing import *
import MeCab

dic_path = os.environ.get('MECAB_DICDIR')
tagger = MeCab.Tagger(f'-d {dic_path}')
jp = str.maketrans({
    "ア":"あ", "イ":"い", "ウ":"う", "エ":"え", "オ":"お",
    "カ":"か", "キ":"き", "ク":"く", "ケ":"け", "コ":"こ",
    "サ":"さ", "シ":"し", "ス":"す", "セ":"せ", "ソ":"そ",
    "タ":"た", "チ":"ち", "ツ":"つ", "テ":"て", "ト":"と",
    "ナ":"な", "ニ":"に", "ヌ":"ぬ", "ネ":"ね", "ノ":"の", 
    "ハ":"は", "ヒ":"ひ", "フ":"ふ", "ヘ":"へ", "ホ":"ほ",
    "マ":"ま", "ミ":"み", "ム":"む", "メ":"め", "モ":"も",
    "ヤ":"や", "ユ":"ゆ", "ヨ":"よ", "ラ":"ら", "リ":"り", 
    "ル":"る", "レ":"れ", "ロ":"ろ", "ワ":"わ", "ヲ":"を", 
    "ン":"ん", "ガ":"が", "ギ":"ぎ", "グ":"ぐ", "ゲ":"げ", 
    "ゴ":"ご", "ザ":"ざ", "ジ":"じ", "ズ":"ず", "ゼ":"ぜ", 
    "ゾ":"ぞ", "ダ":"だ", "ヂ":"ぢ", "ヅ":"づ", "デ":"で", 
    "ド":"ど", "バ":"ば", "ビ":"び", "ブ":"ぶ", "ベ":"べ", 
    "ボ":"ぼ", "パ":"ぱ", "ピ":"ぴ", "プ":"ぷ", "ペ":"ぺ", 
    "ポ":"ぽ", "ャ":"ゃ", "ュ":"ゅ", "ョ":"ょ", "ァ":"ぁ",
    "ィ":"ぃ", "ゥ":"ぅ", "ェ":"ぇ", "ォ":"ぉ", "ッ":"っ"})

def getKanjiIndex(japanese):
    kanji_index = ""
    kanji_pattern = re.compile(r'[\u4E00-\u9FAF\u3005]')
    for i, char in enumerate(japanese):
        if kanji_pattern.match(char):
            kanji_index += str(i)
    if kanji_index == "":
        return "-1"
    return kanji_index

def getKanjiReading(original, reading, kanji_index):
    if kanji_index == "-1": 
        return "none"

    # get notKanjiIndex
    notKanjiIndex = ["0" for _ in range(len(reading))] 
    j = len(reading) - 1
    for i in range(len(original)-1, -1, -1):
        if str(i) not in kanji_index:
            while reading[j].translate(jp) != original[i] and j >= 0:
                j -= 1
            notKanjiIndex[j] = "1"
    if '1' not in notKanjiIndex: 
        return reading
    
    # get result
    result = ""
    s = 0
    for i in range(len(notKanjiIndex)):
        if notKanjiIndex[i] == "1":
            if result != "" and reading[s:i] != "":
                result += ":"
            result += reading[s:i]
            s = i+1
    if reading[s:] != "":
        if result != "":
            result += ":"
        result += reading[s:]

    return result

def getAfter(parsed):
    lines = parsed.split("\n")
    for i, line in enumerate(lines[:-1]):
        count = line.count(',')
        if count != 8 and '\t' in line:
            original = line[:line.index('\t')]
            if original == ',':
                original = ' '
            lines[i] += f",{original},{original}"
    after = "\n".join(lines)
    return after

def preprocess(text):
    # 使用正則表達式一次性匹配所有需要的部分
    pattern = re.compile(r'([^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+)')
    matches = pattern.finditer(text.strip())
    
    # 將匹配的部分用 "/*...*/" 包裹
    for match in reversed(list(matches)):
        s, e = match.span()
        text = text[:s] + "/*" + text[s:e] + "*/" + text[e:]

    pattern = re.compile(r'/\*.*?\*/')
    matches = pattern.finditer(text)
    indices = []
    for match in matches:
        s, e = match.span()
        indices.append((s, e))
    
    return text, indices

def getCompleteJp(dic_path, text):
    if text == "":
        return []

    tokensList : List[dict] = []
    mecab_tagger = MeCab.Tagger(f"-d {dic_path}")
    parsed = mecab_tagger.parse(text)
    after = getAfter(parsed)
    split_result = re.split(r'(\t|\n|,)', after)

    tokens = list(zip(split_result[::20][:-1], split_result[16::20], split_result[14::20]))
    for token in tokens:
        tokensList.append(dict())
        kanji_index = getKanjiIndex(token[0])
        kanji_reading = getKanjiReading(token[0], token[1], kanji_index)
        # 原本、(動詞原形)、漢字位置、漢字讀法
        tokensList[-1]["origin"] = token[0]
        tokensList[-1]["normalForm"] = token[2] if token[2] != "*" else token[0]
        tokensList[-1]["kanji_index"] = kanji_index
        tokensList[-1]["kanji_reading"] = kanji_reading.translate(jp)
    return tokensList

def getResult(line, dic_path=dic_path):
    # line 已經 line.decode('utf-8').strip() 了
    tokens = []
    text, indices = preprocess(line) # 日文以外用/**/包住額外處理
    jp_s = 0
    for (s, e) in indices:
        jp = text[jp_s:s]
        tokens += getCompleteJp(dic_path, jp)
        tokens.append(dict())
        tokens[-1]["origin"] = text[s+2:e-2]
        tokens[-1]["normalForm"] = text[s+2:e-2]
        tokens[-1]["kanji_index"] = "-1"
        tokens[-1]["kanji_reading"] = "none"
        jp_s = e
    if jp_s < len(text):
        tokens += getCompleteJp(dic_path, text[jp_s:])
    return tokens
