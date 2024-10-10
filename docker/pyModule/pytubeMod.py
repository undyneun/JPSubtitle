from pytubefix import YouTube, exceptions

def downloadYtMp3(url: str):
    try:
        yt = YouTube(url)
        audioPath = yt.streams.filter().get_audio_only().download("", "audio.wav")
        return audioPath
    except exceptions.VideoUnavailable as e:
        raise e
    