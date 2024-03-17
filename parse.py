from pytube import YouTube
from utils import write_srt, write_vtt, write_srt_ko
from typing import Iterator
from io import StringIO
import os
import whisper
import ffmpeg

# For Debug 
from cProfile import Profile
from pstats import Stats

loaded_model = whisper.load_model("medium")

def populate_metadata(link):
    yt = YouTube(link)
    author = yt.author
    title = yt.title
    description = yt.description
    thumbnail = yt.thumbnail_url
    length = yt.length
    views = yt.views
    return author, title, description, thumbnail, length, views

def download_video(link):
    yt = YouTube(link)
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
    return video

def getSubs(segments: Iterator[dict], format: str, maxLineWidth: int) -> str:
    segmentStream = StringIO()

    if format == 'vtt':
        write_vtt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    elif format == 'srt':
        write_srt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    elif format == 'srt_ko':
        write_srt_ko(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    else:
        raise Exception("Unknown format " + format)

    segmentStream.seek(0)
    return segmentStream.read()

def inference(link, loaded_model):
    yt = YouTube(link)
    path = yt.streams.filter(only_audio=True)[0].download(filename="audio.mp3")
    options = dict(task="transcribe", best_of=5)
    results = loaded_model.transcribe(path, **options)
    vtt = getSubs(results["segments"], "vtt", None)
    srt = getSubs(results["segments"], "srt", None)
    srt_ko = getSubs(results["segments"], "srt_ko", None)
    lang = results["language"]
    return results["text"], vtt, srt, srt_ko, lang


def generate_subtitled_video(video, audio, transcript):
    video_file = ffmpeg.input(video)
    audio_file = ffmpeg.input(audio)
    ffmpeg.concat(video_file.filter("subtitles", transcript, force_style='Language=kor'), audio_file, v=1, a=1).output("final_ko.mp4").run(quiet=True, overwrite_output=True)
    video_with_subs = open("final.mp4", "rb")
    return video_with_subs     

def process(link: str):
    
    author, title, description, thumbnail, length, views = populate_metadata(link)
    results = inference(link, loaded_model)
    video = download_video(link)
    lang = results[3]
    
    with open("transcript.txt", "w+", encoding='utf8') as f:
        f.writelines(results[0])
        f.close()
        
    with open("transcript.vtt", "w+",encoding='utf8') as f:
        f.writelines(results[1])
        f.close()
        
    with open("transcript.srt", "w+",encoding='utf8') as f:
        f.writelines(results[2])
        f.close()
        
    with open("transcript_ko.srt", "w+",encoding='utf8') as f:
        f.writelines(results[3])
        f.close()
        
        
    return results, video

def main():
    # loaded_model = whisper.load_model("base")
    
    # link = "https://www.youtube.com/watch?v=1aA1WGON49E" # 1m 20
    link = "https://www.youtube.com/watch?v=5m-5dMP0NTI" 
    
    author, title, description, thumbnail, length, views = populate_metadata(link)
    results = inference(link, loaded_model)
    video = download_video(link)
    lang = results[3]
    
    with open("transcript.txt", "w+", encoding='utf8') as f:
        f.writelines(results[0])
        f.close()
        
    with open("transcript.vtt", "w+",encoding='utf8') as f:
        f.writelines(results[1])
        f.close()
        
    with open("transcript.srt", "w+",encoding='utf8') as f:
        f.writelines(results[2])
        f.close()
        
    with open("transcript_ko.srt", "w+",encoding='utf8') as f:
        f.writelines(results[3])
        f.close()
        
        
    # video_with_subs = generate_subtitled_video(video, "audio.mp3", "transcript.srt")
    # video_with_subs = generate_subtitled_video(video, "audio.mp3", "transcript_ko.srt")
if __name__ == "__main__":
        
    profiler = Profile()
    profiler.runcall(main)
    
    stats = Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative') # 누적 통계
    stats.print_stats(10)
    stats.print_callers(.5, 'init')
   