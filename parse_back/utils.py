import textwrap
from typing import Iterator, TextIO
# from translate import translate
from tqdm import tqdm
from model import Translator_GoogleTrans, Translator_GoogleGemini, Translator_GoogleGemini_Multi, Translator_GoogleGemini_Multi_Separate
from time_utils import logging_time
from localization import get_current_date
import os
import io
from pydub import AudioSegment

def export_mp3_from_mp4(video: bytes, save_path, title):
    audio = AudioSegment.from_file(io.BytesIO(video), format="mp4")
    audio.export(save_path+f"{title}.mp3", format="mp3")
    
    return save_path+f"{title}.mp3"
    
def format_timestamp(seconds: float, always_include_hours: bool = False, fractionalSeperator: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{fractionalSeperator}{milliseconds:03d}"
    
def write_txt(transcript: Iterator[dict], file: TextIO):
    for segment in transcript:
        print(segment['text'].strip(), file=file, flush=True)


def write_vtt(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):
    print("WEBVTT\n", file=file)
    for segment in transcript:
        text = processText(segment['text'], maxLineWidth).replace('-->', '->')
        
        print(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
            f"{text}\n",
            file=file,
            flush=True,
        )
        
def write_srt(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):
    """
    Write a transcript to a file in SRT format.
    Example usage:
        from pathlib import Path
        from whisper.utils import write_srt
        result = transcribe(model, audio_path, temperature=temperature, **args)
        # save SRT
        audio_basename = Path(audio_path).stem
        with open(Path(output_dir) / (audio_basename + ".srt"), "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)
    """
    for i, segment in enumerate(transcript, start=1):
        text = processText(segment['text'].strip(), maxLineWidth).replace('-->', '->')
        text = make_full_stop(text)
        # write srt lines
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, fractionalSeperator=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, fractionalSeperator=',')}\n"
            f"{text}\n",
            file=file,
            flush=True,
        )
        
# 10 increment씩 증가하며 분할 요청        
@logging_time
def write_srt_ko(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):

    translator = Translator_GoogleGemini_Multi_Separate()
    
    indice = 0
    increment = 10
    
    while indice <= len(transcript):

        english_list = get_transcript_list(transcript[indice:indice+increment])
        translated_text = translator.translate(indice, english_list) 
        translated_text = [item.replace('<paragraph>', '').replace('</paragraph>', '') for item in translated_text]
        try:
            for i, segment in enumerate(transcript[indice:indice+increment], start=indice+1):

                print(
                    f"{i}\n"
                    f"{format_timestamp(segment['start'], always_include_hours=True, fractionalSeperator=',')} --> "
                    f"{format_timestamp(segment['end'], always_include_hours=True, fractionalSeperator=',')}\n"
                    f"{translated_text[i-indice-1]}\n",
                    file=file,
                    flush=True,
                )
        except:
            pass        
            
        indice += increment
        
def processText(text: str, maxLineWidth=None):
    if (maxLineWidth is None or maxLineWidth < 0):
        return text

    lines = textwrap.wrap(text, width=maxLineWidth, tabsize=4)
    return '\n'.join(lines)


def make_full_stop(text: str) -> list:
    last_ch = text[-1]
    
    if last_ch == '.' or last_ch == '?' or last_ch == '!': # 이미 full-stop 이거나 QM, SM이라면
        return text
    elif last_ch == ',': # comma라면
        return text[:-1] + '.' # 변경
    elif last_ch.isalnum(): # 숫자거나 단어라면
        return text + '.' # 구두점 추가
    else: # 예외가 있을 수 있음 그런경우 text
        return text
    
def get_transcript_list(transcript: Iterator[dict], maxLineWidth=None) -> list:
    
    transcript_list = []
    for i, segment in tqdm(enumerate(transcript, start=1)):
        text = processText(segment['text'].strip(), maxLineWidth).replace('-->', '->')
        text = make_full_stop(text)
        transcript_list.append(text)
        
    return transcript_list


def make_dirs(path):
    # 현재 디렉토리 경로 가져오기
    current_dir = os.getcwd()

    # 'video' 폴더 경로 생성
    path_dir = os.path.join(current_dir, path)

    # 'video' 폴더가 없으면 생성
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
        print(f"'{path_dir}' 폴더가 생성되었습니다.")
    else:
        print(f"'{path_dir}' 폴더가 이미 존재합니다.")
        
def make_path(title: str) -> str: 
        
    # 저장할 target_path를 만드는 함수
    current_date = get_current_date()
    root_path = os.getcwd()
    save_path = f'{root_path}/video/{current_date}/{title}/'
    make_dirs(path=save_path)
    return save_path