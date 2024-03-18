import textwrap
from typing import Iterator, TextIO
# from translate import translate
from tqdm import tqdm
from model import Translator_GoogleTrans, Translator_GoogleGemini, Translator_GoogleGemini_Multi
from time_utils import logging_time

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

def write_srt_ko(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):
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
    # translator = Translator_GoogleTrans() # Standard
    translator = Translator_GoogleGemini()
    for i, segment in tqdm(enumerate(transcript, start=1)):
        text = processText(segment['text'].strip(), maxLineWidth).replace('-->', '->')
        text = make_full_stop(text)
        text = translator.translate(text)
        # write srt lines
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, fractionalSeperator=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, fractionalSeperator=',')}\n"
            f"{text}\n",
            file=file,
            flush=True,
        )

@logging_time
def write_srt_ko_v2(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):

    translator = Translator_GoogleGemini_Multi()
    
    english_list = get_transcript_list(transcript)
    translated_text = translator.translate(english_list)    
    translated_text = [item.replace('<paragraph>', '').replace('</paragraph>', '') for item in translated_text]
    
    for i, segment in tqdm(enumerate(transcript, start=1)):

        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, fractionalSeperator=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, fractionalSeperator=',')}\n"
            f"{translated_text[i-1]}\n",
            file=file,
            flush=True,
        )    
    # with (
    #      open('transcript.srt', 'r', encoding='utf-8') as en,  
    #      open('transcript_ko.srt', 'w', encoding='utf-8') as ko
    # ):
    #     lines = en.readlines()
    #     count = 0
    #     for idx, line in enumerate(lines):
    #         if 4*count + 2 == idx:
    #             ko.write(translated_text[count] + "\n")
    #             count += 1
    #         else:
    #             ko.write(line)        
        
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
