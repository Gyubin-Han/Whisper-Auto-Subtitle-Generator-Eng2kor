from transformers import pipeline
from huggingface_hub import login

from anthropic import Anthropic

import deepl

from googletrans import Translator

import os

# ! Need

# login("your-huggingface-login-read-token")

class Translator_NLLB:
    
    def __init__(self):
        # Load model
        read_token = os.environ.get('HUGGING_FACE_READ_TOKEN')
        login(read_token)
        
        self.model = pipeline('translation', model='NHNDQ/nllb-finetuned-en2ko', device=0, src_lang='eng_Latn', tgt_lang='kor_Hang', max_length=512)
        
    def translate(self, text: str) -> str:
        # Run inference
        model_output = self.model(text, max_length=512)

        # Post-process output to return only the translation text
        translation = model_output[0]["translation_text"]

        return translation
    
    
class Translator_Anthropic:
    def __init__(self):        
        self.client = Anthropic() # default env get
        
    def response_test(self):
        message = self.client.messages.create(
            max_tokens = 512,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! what is your name"
                }
            ],
            model="claude-3-sonnet-20240229"
        )
        
        return message


    def translate(self, english: str):
        message = self.client.messages.create(
            max_tokens = 512,
            temperature = 0.2,
            system="You are a highly skilled translator with expertise in English and Korean languages. \
                    Your task is to identify the language of the text I provide and accurately translate it into the specified target language \
                    while preserving the meaning, tone, and nuance of the original text.\
                    Please maintain proper grammar, spelling, and punctuation in the translated version.\
                    You can contain only english and korean, not allowed Chinese Character",
            messages=[
                {
                    "role": "user",
                    "content": f"{english} -> Korean"
                }
            ],
            model="claude-3-sonnet-20240229"
        )
        
        return message
    
class Translator_Deepl:
    
    def __init__(self):
        self.auth_key = os.environ.get('DEEPL_AUTH_KEY')
        self.translator = deepl.Translator(self.auth_key)
        
    def translate(self, text: str):
        result = self.translator.translate_text(text, target_lang="KO")
        return result.text
        
        
class Translator_GoogleTrans:
    def __init__(self):
        self.translator = Translator()
        
    def translate(self, text: str):
        return self.translator.translate(text, dest = 'ko', src = 'en').text