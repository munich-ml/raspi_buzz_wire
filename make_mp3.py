from gtts import gTTS
import os, random, time, sys

text = "los gehts"

special_chars = {" ": "_",
                    ",": "",
                    "ü": "ue"}

fn = text
for org, repl in special_chars.items():
    fn = fn.replace(org, repl)

gTTS(text, lang="de").save(os.path.join("mp3", fn+".mp3"))

