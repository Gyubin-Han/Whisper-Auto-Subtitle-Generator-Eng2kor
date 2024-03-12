# Whisper English/Korean Subtitle Auto Generator

Whisper Based Automatic Speech Recognition (ASR) and Translate using selectable models


## Use Models
- ASR
    - [Whisper](https://github.com/openai/whisper)
        - base 
        - small
        - medium 

- Translate (models.py)
    - [NLLB](https://huggingface.co/NHNDQ/nllb-finetuned-ko2en)
    - [Antropic API (Claude3)](https://www.anthropic.com/api)
    - [Deep API](https://www.deepl.com/ko/pro-api?cta=header-pro-api)
    - [GoogleTrans](https://pypi.org/project/googletrans-py/)

## 언어 모델 정보
1. NLLB
    
    번역 속도는 빠름 용량자체가 작기 떄문, 자막으로 달기에 너무 ruff 한 느낌
    
    장점 : 무료
    
    단점 : 번역 퀄리티
    
2. Claude API
    
    번역 속도도 좋고, 번역 퀄리티도 좋음, 무료 버전으로 사용하기에 너무 제한적인 RPM
    
    장점 : 전반적으로 성능이 뛰어남
    
    단점 : 유료, 무료는 ( RPM 5 ) → 번역에 사용하기 어려움
    
3. DeepL
    
    번역 속도 좋고, 번역 퀄리티 나쁘지 않음, 무료버전으로 500,000자 까지 번역가능
    
    장점 : 무료 버전으로 50만자 번역 가능
    
    단점 : 유료 ( 10분 정도 되는 길이 하나에 1.5만자 정도 ) 
    
4. GoogleTrans ( UnOfficial )
    
    번역 퀄리티 괜찮고 속도도 좋음 무료버전으로 사용할 수 있는 마지노선 
    
    번역 퀄리티가 생각보다 좋지 않음 DeepL > GoogleTrans..
    
    장점: 무료
    
    단점: 1000 req / hours 경우의 IP block, 영상 길이가 길어지면 요청 가능 한도가 넘어 IP 블락이 될 수 있음
