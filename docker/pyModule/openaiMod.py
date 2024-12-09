from openai import OpenAI

def getSenDurations(jsonText, jsonWords, returnLines=False):
    lines = [""] 
    senDurations:list[list[float, float]] = [[-1.0, -1.0]]
    sens = jsonText.split('\n')
    sensIdx = 0
    for jsonidx in range(len(jsonWords)):
        word = jsonWords[jsonidx]["word"]
        if word not in sens[sensIdx] and senDurations[-1][1] == -1.0:
            senDurations[-1][1] = jsonWords[jsonidx-1]["end"]
            senDurations.append([-1.0, -1.0])
            sensIdx += 1
            lines.append("")
        if senDurations[-1][0] == -1.0 and word in sens[sensIdx]:
            senDurations[-1][0] = jsonWords[jsonidx]["start"]
        lines[-1] += word
    senDurations[-1][1] = jsonWords[-1]["end"]

    for i, d in enumerate(senDurations, 1):
        if d[0] == -1.0:
            d[0] = senDurations[i-1][1]

    if returnLines:
        return senDurations, lines
    return senDurations

def chatgpt(input:str, apiKey, sysPrompt):
    input = input.replace("\n", "_")
    client = OpenAI(api_key=apiKey)
    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
        {"role": "system", "content": sysPrompt},
        {"role": "user", "content": input}
    ])
    return completion.choices[0].message.content

def whisper(audioPath, apiKey):
    audioFile = open(audioPath, "rb")
    client = OpenAI(api_key=apiKey)

    output = client.audio.transcriptions.create(
        file=audioFile,
        model="whisper-1",
        language = 'ja',
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )

    jsonWords = [{"word":obj.word, "start":obj.start, "end":obj.end} for obj in output.words]
    jsonText = "\n".join(output.text.split(" "))
    senDurations, lines = getSenDurations(jsonText, jsonWords, returnLines=True)
    result = [{"line":lines[i], "start":senDurations[i][0], "end":senDurations[i][1]} for i in range(len(lines))]
    return result

