import uvicorn

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import hashlib
import aiofiles
import random
import os
import asyncio
import ffmpeg

# Local Import
from app.parse import process, populate_metadata, process_upload, background_process
from app.utils import make_path, redis_get_value, redis_set_value
from app.validators import is_valid_youtube, is_video_language_english
from app.media_utils import get_concat_subtitles
app = FastAPI(root_path="/api/v1")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/youtube", response_class=FileResponse)
def get_yt_link(link: str):
    
    def update_redis(percentage):
        redis_set_value(link, percentage)
        
    update_redis(0)    
    
    if not is_valid_youtube(link):
        update_redis(-1)
        raise HTTPException(status_code=400, detail="적절한 유튜브 URL을 넣어주세요")

    results, video, save_path, title = process(link)
        
    with open(save_path+f"{title}_en.srt", "w+",encoding='utf8') as f:
        f.writelines(results[2])
        f.close() 
        
    with open(save_path+f"{title}.srt", "w+",encoding='utf8') as f:
        f.writelines(results[3])
        f.close()
    
    subtitled_video = get_concat_subtitles(video, subtitle_path=save_path+f"{title}.srt", save_path=save_path)
    
    # video는 현재, 기본 동영상
    # subtitled_video는 자막이 적용된 영상
    update_redis(100)

    return FileResponse(path=subtitled_video, media_type='application/octet-stream',filename=f"{title}.mp4")
    
@app.get("/youtube/subtitle_download", response_class=FileResponse)
def get_yt_subtitle(link: str):
    
    author, title, description, thumbnail, length, views = populate_metadata(link)
    save_path = make_path(title)
    
    return FileResponse(path=save_path+f"{title}.srt", media_type='application/octet-stream', filename=f"{title}.srt")
        
@app.post("/upload")
async def upload_video(video: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        # 영상 데이터 읽기
        video_data = await video.read()
                
        # 해시 값 계산
        
        full_hash = hashlib.sha256(video_data).hexdigest()

        # 해시 값을 10자로 제한
        limited_hash = full_hash[:10]  # 바이트 객체에서 앞의 10글자만 취함

        # 바이트 객체를 16진수 문자열로 변환
        # limited_hash_hex = limited_hash.hex()   
        
        # 번역 작업은 background로 넘기기
        background_tasks.add_task(background_process, video_data, video.filename, limited_hash)

        # 해시 값 반환
        return {"hash": limited_hash}
    finally:
        # 파일 핸들러 닫기
        await video.close()
        
@app.get("/upload/subtitle_download",  response_class=FileResponse)
async def get_custom_video_subtitle_download(limited_hash: str):
    
    save_path = make_path(title=limited_hash)
    
    try:
        return FileResponse(path=save_path+f"{limited_hash}.srt", media_type='application/octet-stream', filename=f"{limited_hash}.srt")
    except:
        raise HTTPException(status_code=404, detail="File not existed!")
    
if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)

@app.get("/status")
def get_value(key: str):
    return redis_get_value(key)
