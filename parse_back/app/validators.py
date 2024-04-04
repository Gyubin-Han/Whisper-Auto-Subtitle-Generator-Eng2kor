from pytube import YouTube

def is_valid_youtube(link: str):
    
    try:
        yt = YouTube(link)
    except Exception as e:
        return False
    else:
        return True
    
def is_video_language_english(language):
    if language == 'en':
        return True
    else:
        return False
    