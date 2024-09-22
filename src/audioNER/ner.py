import whisper

model = whisper.load_model("base")
result = model.transcribe("news.mp3")

raw_text = result['text']
print(raw_text)

import spacy

from spacy import displacy

NER = spacy.load("en_core_web_sm")

text1= NER(raw_text)

for word in text1.ents:
    print(word.text,word.label_)

   