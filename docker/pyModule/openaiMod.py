import os
from openai import OpenAI
# from pyannote.audio import Pipeline
# from pydub import AudioSegment

hf_token = "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"

def chatgpt(input, apiKey, sysPrompt):
    client = OpenAI(api_key=apiKey)
    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
        {"role": "system", "content": sysPrompt},
        {"role": "user", "content": input}
    ])
    return completion.choices[0].message.content

def whisper(audioPath, apiKey):
    # segs = getSegs(audioPath)
    # audio = AudioSegment.from_wav(audioPath)
    # saveAudioPath = createVoiceonly("audio.mp3", segs, audio)
    # audioFile = open(saveAudioPath, "rb")

    audioFile = open(audioPath, "rb")
    client = OpenAI(api_key=apiKey)

    json = client.audio.transcriptions.create(
        file=audioFile,
        model="whisper-1",
        language = 'ja',
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )

    text = "\n".join(json.text.split(" "))
    return text

# def getSegs(audioPath, thredhold=0.7):
#     pipeline = Pipeline.from_pretrained(
#         "pyannote/voice-activity-detection",
#         use_auth_token=hf_token
#     )
#     result = pipeline(audioPath)
#     segs:list = [[seg.start, seg.end] for seg in result.get_timeline().support()] # 防frozen
    
#     # 切太細的段黏起來
#     i = 0
#     while True:
#         if (i+1) >= len(segs):
#             break
#         while (i+1) < len(segs) and abs(segs[i+1][0] - segs[i][1]) < thredhold:
#             segs[i][1] = segs[i+1][1]
#             segs.pop(i+1)
#         i+=1
#     return segs

# def createVoiceonly(savename, segs, audio):
#     voice_only = AudioSegment.empty()
#     for seg in segs:
#         s = seg[0] * 1000  # ms->s
#         e = seg[1] * 1000
#         voice_only += audio[s:e]
#     obj = voice_only.export(savename, format="mp3")
#     return os.path.abspath(obj.name)