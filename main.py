from typing import Union

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parse import process

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

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/youtube", response_class=FileResponse)
def get_yt_link(link: str):
    
    results, video = process(link)
    
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
                        
    return FileResponse(path=video, media_type='application/octet-stream',filename="video.mp4")            
    # return StreamingResponse(iterfile(),media_type="video/mp4")
    
@app.get("/youtube/subtitle_download", response_class=FileResponse)
def get_yt_subtitle():
    return FileResponse(path="transcript_ko.srt", media_type='application/octet-stream', filename='transcript.srt')
        
    