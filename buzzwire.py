import os, threading, time
import datetime as dt
import RPi.GPIO as gpio
from enum import Enum
from gtts import gTTS

# setup logging##########################################################################
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(funcName)15s | %(message)s')

# constants #############################################################################
MAX_TIME_IN_START_S = 60     # After this time in state 'started', the game is aborted
time_started: time.time      # store the time when started

class State(Enum):
    waiting = 0
    about_to_start = 1
    started = 2
    touched = 3
    finished = 4

# setup GPIOs ###########################################################################
GPIO_NUMBERS = {"start": 10,
                "finish": 9,
                "touch": 11}

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
for gpio_number in GPIO_NUMBERS.values():
    gpio.setup(gpio_number, gpio.IN, pull_up_down=gpio.PUD_OFF)

def get_wire(name: str = "start") -> bool:
    """Polls the Raspi GPIO pin

    Args:
        name (str): GPIO name out of ("start", "finish", "touch")

    Returns:
        bool: True means active pull down, False mease inactive
    """
    return not(gpio.input(GPIO_NUMBERS[name]))

def play_sound(fp: str):
    """Play sound on raspberry pi

    Args:
        fp (str): Filepath
    """
    os.system(f"cvlc --play-and-exit {fp}")

def save_record(ctr: int, t: float, dir_: str = "records") -> tuple[int, int]:
    """Saves the record

    Args:
        ctr (int): Error count
        t (float): Time to complete the game
        dir_ (str, optional): Name of the directory. Defaults to "records".

    Returns:
        tuple[int, int]: Return (rank, records_cnt) as tuple
    """
    # Create error str with 3 digits like 002
    err = str(int(ctr))
    while len(err) < 3:
        err = "0" + err
    
    # Create milliseconds str with 6 digits like 001000 for 1s
    ms = str(int(t * 1000))
    while len(ms) < 6:
        ms = "0" + ms
    
    # Join filename str with datetime str
    fn = "e{}_{}ms_".format(err, ms)
    fn += dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # Save data as filename
    if dir_ not in os.listdir():
        os.mkdir(dir_)
    open(os.path.join(dir_, fn), "w")
    
    # Compute rank and records_cnt for return
    all_records = sorted(os.listdir(dir_))
    rank = all_records.index(fn) +1
    records_cnt = len(all_records)
    return (rank, records_cnt)

class StateMachine:
    def __init__(self, upon_start, upon_about_to_start, upon_touch, upon_finish, upon_abort) -> None:
        self.upon_start = upon_start    # function to be called upon State.started entry
        self.upon_about_to_start = upon_about_to_start 
        self.upon_touch = upon_touch    # function to be called upon State.touched entry
        self.upon_finish = upon_finish  # function to be called upon State.finished entry
        self.upon_abort = upon_abort    # function to be called upon abort_started call
        self.state = State.waiting
        self.time_started: float        # stores the time in State.started
        self.touch_ctr: int
        
    def __str__(self):
        return str(self.state)
    
    def go_about_to_start(self):
        self.touch_ctr = 0
        self.time_started = time.time()
        self.upon_about_to_start()
        self.state = State.about_to_start

    def go_started(self):
        self.upon_start()
        self.state = State.started
        
    def go_touched(self):
        self.state = State.touched
        self.touch_ctr += 1
        self.upon_touch()
        
    def go_finished(self):
        """Switch state machine to the State.finished
        """
        self.state = State.finished
        
        # time to complete the game
        t = time.time() - self.time_started  
        
        # save the records and compute the rank
        rank, recorts_cnt = save_record(self.touch_ctr, t)
        
        # Create a str for voice output
        s = "Geschafft in {:.1f} Sekunden ".format(t)
        if self.touch_ctr == 0:
            s += "ohne Treffer"
        elif self.touch_ctr == 1:
            s += "mit einem Treffer."
        else:
            s += "mit {} Treffern. ".format(self.touch_ctr)
        
        s += "Das ist Platz {} aus {}".format(rank, recorts_cnt)
        
        logging.info(s)
        fp = os.path.join("mp3", "finished.mp3")
        gTTS(s, lang="de").save(fp)
        play_sound(fp)
        self.upon_finish()

    def go_waiting(self):
        self.state = State.waiting
        
    def max_time_reached(self) -> bool:
        return time.time() - self.time_started > MAX_TIME_IN_START_S
    
    def abort_started(self):
        self.upon_abort()
        self.state = State.waiting
        
def upon_start():
    logging.info("Starting ...")

def upon_about_to_start():
    play_sound(os.path.join("mp3", "los_gehts.mp3"))

def upon_touch():
    logging.info("Autsch!!")

def upon_finish():
    logging.info("Finished")

def upon_abort():
    logging.info("Abort")

sm = StateMachine(upon_start, upon_about_to_start, upon_touch, upon_finish, upon_abort)

def log_periodically():
    while True:
        logging.info(sm)
        time.sleep(1)
        
threading.Thread(target=log_periodically).start()

logging.info("Starting main loop ...")
play_sound(os.path.join("mp3", "lasset_die_Spiele_beginnen.mp3"))

while True:   
    time.sleep(0.05)  # give room to other os processes
    
    if sm.state == State.waiting:
        if get_wire('start'):
            sm.go_about_to_start()
    
    elif sm.state == State.about_to_start:
        if not get_wire('start'):
            sm.go_started()
    
    elif sm.state == State.started:
        if get_wire('start'):
            sm.go_about_to_start()
        
        elif get_wire('touch'):
            sm.go_touched()
            
        elif get_wire('finish'):
            sm.go_finished()    
            
        elif sm.max_time_reached():
            sm.abort_started()
        
    elif sm.state == State.touched:
        if not get_wire('touch'):
            sm.go_started()
   
    elif sm.state == State.finished:
        sm.go_waiting()
        

    
    