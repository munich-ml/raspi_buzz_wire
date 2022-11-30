from gtts import gTTS
import os, random, time, sys

WINDOWS = "win" in sys.platform

def make_mp3s():
    texts = ["Du hast verkackt",
             "Autsch, das tat weh",
             "Ujujuj",
             "Ach Du grüne Neune",
             "Alter, pass auf",
             "Vorsicht"]
    
    special_chars = {" ": "_",
                     ",": "",
                     "ü": "ue"}
    
    for text in texts:
        fn = text
        for org, repl in special_chars.items():
            fn = fn.replace(org, repl)
        gTTS(text, lang="de").save(os.path.join("mp3", fn+".mp3"))


def play(fp: str):
    if WINDOWS:
        from playsound import playsound
        playsound(fp)
    else:    # on raspi
        os.system(f"cvlc --play-and-exit {fp}")


if __name__ == "__main__":
    make_mp3s()
    
    mp3s = [os.path.join(os.getcwd(), "mp3", fn) for fn in os.listdir("mp3")]  
    while True:
        fp = random.choice(mp3s)
        print("play", fp)
        play(fp)
        time.sleep(1)