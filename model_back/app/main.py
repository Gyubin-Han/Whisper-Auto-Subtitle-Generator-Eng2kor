from typing import Union
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import whisper
import os 
import torch

from pytube import YouTube
from pytube.exceptions import RegexMatchError, AgeRestrictedError
from urllib.parse import unquote

from fastapi.routing import APIRoute

from typing import Callable


class CustomRoute(APIRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = asyncio.Lock()

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            await self.lock.acquire()
            response: Response = await original_route_handler(request)
            self.lock.release()
            return response
    
        return custom_route_handler
        
model_path = "medium.pt"
loaded_model = whisper.load_model(model_path)

app = FastAPI()
app.router.route_class = CustomRoute

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


@app.post("/transcribe")
def model_transcribe(data: dict):
    
    def make_dirs(path):
        # 현재 디렉토리 경로 가져오기
        current_dir = os.getcwd()

        # 'video' 폴더 경로 생성
        path_dir = os.path.join(current_dir, path)

        # 'video' 폴더가 없으면 생성
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)


    link = unquote(data["link"])
    save_path = unquote(data["save_path"])
    save_path = os.getcwd() + '/' + '/'.join(save_path.split('/')[1:])
    make_dirs(save_path)
    
    try:
        yt = YouTube(link)
        path = yt.streams.filter(only_audio=True)[0].download(filename=save_path+"audio.mp3")
        
    except AgeRestrictedError as e:
        raise HTTPException(status_code=400, detail="연령 제한 혹은 지원되지 않는 유튜브 영상 입니다.")
    
    options = dict(task="transcribe", best_of=5)

    try:
        results = loaded_model.transcribe(path, **options)
    except Exception as e:
        raise e
    
    if results["language"] != 'en':
        raise HTTPException(status_code=400, detail=f'현재 영어 영상 번역 기능만 지원합니다. 탐지된 언어 {results["language"]}')
    
    print("작업이 완료되었습니다")
    return results

    
if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8200)