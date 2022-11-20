import logging, os, time
from enum import Enum
import threading
import RPi.GPIO as gpio
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
    return not(gpio.input(GPIO_NUMBERS[name]))

# init ##################################################################################


class StateMachine:
    def __init__(self, upon_start, upon_touch, upon_finish, upon_abort) -> None:
        self.upon_start = upon_start    # function to be called upon State.started entry
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
        self.state = State.about_to_start

    def go_started(self):
        self.upon_start()
        self.state = State.started
        
    def go_touched(self):
        self.state = State.touched
        self.touch_ctr += 1
        self.upon_touch()
        
    def go_finished(self):
        self.state = State.finished
        t = time.time() - self.time_started
        ctr = self.touch_ctr
        logging.info(f"Finished with {ctr=}, {t=}.")
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

def upon_touch():
    logging.info("Autsch!!")

def upon_finish():
    logging.info("Finished")

def upon_abort():
    logging.info("Abort")

sm = StateMachine(upon_start, upon_touch, upon_finish, upon_abort)

def log_periodically():
    while True:
        logging.info(sm)
        time.sleep(1)
        
threading.Thread(target=log_periodically).start()

logging.info("Starting main loop ...")

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
        

    
    