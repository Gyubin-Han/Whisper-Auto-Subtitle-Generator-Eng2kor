from pytube import YouTube
from typing import Iterator
from io import StringIO
import os
import whisper
import ffmpeg

from utils import write_srt, write_vtt, write_srt_ko, write_srt_ko_v2, make_dirs, make_path
from time_utils import logging_time
from localization import get_current_date

loaded_model = whisper.load_model("medium") # 9sec    

@logging_time
def populate_metadata(link):
    yt = YouTube(link)
    author = yt.author
    title = yt.title
    description = yt.description
    thumbnail = yt.thumbnail_url
    length = yt.length
    views = yt.views
    return author, title, description, thumbnail, length, views

@logging_time
def download_video(link, save_path):
    yt = YouTube(link)
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=save_path)
    return video

def getSubs(segments: Iterator[dict], format: str, maxLineWidth: int) -> str:
    segmentStream = StringIO()

    if format == 'vtt':
        write_vtt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    elif format == 'srt':
        write_srt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    elif format == 'srt_ko':
        write_srt_ko_v2(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    else:
        raise Exception("Unknown format " + format)

    segmentStream.seek(0)
    return segmentStream.read()

@logging_time
def inference(link, loaded_model, save_path):
    yt = YouTube(link)
    path = yt.streams.filter(only_audio=True)[0].download(filename=save_path+"audio.mp3")
    options = dict(task="transcribe", best_of=5)
    results = loaded_model.transcribe(path, **options)
    vtt = getSubs(results["segments"], "vtt", None)
    srt = getSubs(results["segments"], "srt", None)
    srt_ko = getSubs(results["segments"], "srt_ko", None)
    lang = results["language"]
    return results["text"], vtt, srt, srt_ko, lang


@logging_time
def generate_subtitled_video(video, audio, transcript):
    video_file = ffmpeg.input(video)
    audio_file = ffmpeg.input(audio)
    ffmpeg.concat(video_file.filter("subtitles", transcript, force_style='Language=kor'), audio_file, v=1, a=1).output("final_ko.mp4").run(quiet=True, overwrite_output=True)
    video_with_subs = open("final.mp4", "rb")
    return video_with_subs     

@logging_time
def process(link: str):
    
    author, title, description, thumbnail, length, views = populate_metadata(link)
    save_path = make_path(title)
    results = inference(link, loaded_model, save_path)
    video = download_video(link, save_path)
    lang = results[3]
        
    return results, video, save_path, title

@logging_time
def main():
    
    # 저장할 target_path를 만드는 함수
    def make_path(title=None):
        current_date = get_current_date()
        root_path = os.getcwd()
        save_path = f'{root_path}/video/{current_date}/{title}/'
        make_dirs(path=save_path)
        return save_path
    
    # loaded_model = whisper.load_model("base")
    
    # link = "https://www.youtube.com/watch?v=1aA1WGON49E" # 1분 20초
    link = "https://www.youtube.com/watch?v=5m-5dMP0NTI" # 5분
    # link = "https://www.youtube.com/watch?v=LK5j3pp0Too&t=2s" # 16분
    
    author, title, description, thumbnail, length, views = populate_metadata(link)
    save_path = make_path(title)
    results = inference(link, loaded_model, save_path)
    video = download_video(link, save_path)
    lang = results[3]
    
    # with open(save_path+"transcript.txt", "w+", encoding='utf8') as f:
    #     f.writelines(results[0])
    #     f.close()
        
    # with open(save_path+"transcript.vtt", "w+",encoding='utf8') as f:
    #     f.writelines(results[1])
    #     f.close()
        
    with open(save_path+f"{title}_en.srt", "w+",encoding='utf8') as f:
        f.writelines(results[2])
        f.close()
        
    with open(save_path+f"{title}.srt", "w+",encoding='utf8') as f:
        f.writelines(results[3])
        f.close()
        
        
    # video_with_subs = generate_subtitled_video(video, "audio.mp3", "transcript.srt")
    # video_with_subs = generate_subtitled_video(video, "audio.mp3", "transcript_ko.srt")
if __name__ == "__main__":
    main()
   