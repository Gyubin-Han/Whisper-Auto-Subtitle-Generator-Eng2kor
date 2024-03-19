from typing import Union

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parse import process, populate_metadata
from utils import make_path

app = FastAPI()

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
   
    results, video, save_path, title = process(link)
        
    with open(save_path+f"{title}_en.srt", "w+",encoding='utf8') as f:
        f.writelines(results[2])
        f.close()
        
    with open(save_path+f"{title}.srt", "w+",encoding='utf8') as f:
        f.writelines(results[3])
        f.close()
                        
    return FileResponse(path=video, media_type='application/octet-stream',filename=f"{title}.mp4")
    
@app.get("/youtube/subtitle_download", response_class=FileResponse)
def get_yt_subtitle(link: str):
    
    author, title, description, thumbnail, length, views = populate_metadata(link)
    save_path = make_path(title)
    
    return FileResponse(path=save_path+f"{title}.srt", media_type='application/octet-stream', filename=f"{title}.srt")
        
    