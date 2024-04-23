from pytube import YouTube

from fastapi import HTTPException
from typing import Iterator
from io import StringIO

import os
import ffmpeg
import hashlib 
import asyncio, aiohttp

from app.utils import write_srt, write_vtt, write_srt_ko, make_dirs, make_path, export_mp3_from_mp4, redis_set_value, redis_get_value
from app.time_utils import logging_time
from app.localization import get_current_date
from app.validators import is_video_language_english    

import requests

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

    def update_redis(percentage):
        redis_set_value(link, percentage)
        
    yt = YouTube(link)
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=save_path)
    update_redis(100)

    return video

def getSubs(segments: Iterator[dict], format: str, maxLineWidth: int, link) -> str:
    segmentStream = StringIO()

    if format == 'vtt':
        # await write_vtt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
        pass
    elif format == 'srt':
        write_srt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    elif format == 'srt_ko':
        write_srt_ko(segments, file=segmentStream, maxLineWidth=maxLineWidth, link=link)
    else:
        raise Exception("Unknown format " + format)

    segmentStream.seek(0)
    return segmentStream.read()

@logging_time
def inference(link, save_path):
    
    def update_redis(percentage):
        redis_set_value(link, percentage)
        
    results = []
    update_redis(5) # 5% 완료 not working well..
    url = "https://tools.gyu.be/model/whisper/transcribe"
    data = {"link": link, "save_path": save_path}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        results = response.json()
        update_redis(10) # 10% 완료
        print("응답 OK")
        vtt = getSubs(results["segments"], "vtt", None, link)
        srt = getSubs(results["segments"], "srt", None, link)
        srt_ko = getSubs(results["segments"], "srt_ko", None, link)
        lang = results["language"]
        return results["text"], vtt, srt, srt_ko, lang
    else:
        print(f"요청 실패: {response.status_code}")
        error_detail = response.json().get("detail")
        update_redis(-1)
        raise HTTPException(status_code=response.status_code, detail=error_detail)
    # results = await asyncio.to_thread(loaded_model.transcribe, path, **options)
   
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
    results = inference(link, save_path)
    video = download_video(link, save_path)
        
    return results, video, save_path, title

# User Upload

@logging_time
def inference_upload(path, save_path):
    options = dict(task="transcribe", language='en', best_of=5)
    results = loaded_model.transcribe(path, **options)
    vtt = getSubs(results["segments"], "vtt", None)
    srt = getSubs(results["segments"], "srt", None)
    srt_ko = getSubs(results["segments"], "srt_ko", None)
    lang = results["language"]
    return results["text"], vtt, srt, srt_ko, lang

@logging_time
def process_upload(video, title, limited_hash):
    
    save_path = make_path(limited_hash) # upload 일떄는 hash를 파일 폴더로
    path = export_mp3_from_mp4(video, save_path, limited_hash) # filename -> limited_hash
    
    results = inference_upload(path, save_path)
    lang = results[3]
        
    return results, save_path, title

def background_process(video, file_name, limited_hash):
    results, save_path, title = process_upload(video, file_name, limited_hash) 
    
    if not is_video_language_english(results[4]):
        raise HTTPException(status_code=400, detail="Other language video cannot be translated yet.")
        
    with open(save_path+f"{limited_hash}_en.srt", "w+",encoding='utf8') as f: # filename -> limited_hash
        f.writelines(results[2])
        f.close()
        
    with open(save_path+f"{limited_hash}.srt", "w+",encoding='utf8') as f: # filename -> limited_hash
        f.writelines(results[3])
        f.close()

@logging_time
def main():
    
    # 저장할 target_path를 만드는 함수
    def make_path(title=None):
        current_date = get_current_date()
        root_path = os.getcwd()
        save_path = f'{root_path}/video/{current_date}/{title}/'
        make_dirs(path=save_path)
        return save_path
    
    # link = "https://www.youtube.com/watch?v=1aA1WGON49E" # 1분 20초
    link = "https://www.youtube.com/watch?v=5m-5dMP0NTI" # 5분
    # link = "https://www.youtube.com/watch?v=LK5j3pp0Too&t=2s" # 16분
    
    author, title, description, thumbnail, length, views = populate_metadata(link)
    save_path = make_path(title)
    results = inference(link, loaded_model, save_path)
    video = download_video(link, save_path)
    lang = results[3]
        
    with open(save_path+f"{title}_en.srt", "w+",encoding='utf8') as f:
        f.writelines(results[2])
        f.close()
        
    with open(save_path+f"{title}.srt", "w+",encoding='utf8') as f:
        f.writelines(results[3])
        f.close()
        

if __name__ == "__main__":
    main()
   