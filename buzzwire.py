import logging, os, time
from enum import Enum
import RPi.GPIO as gpio
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(funcName)15s | %(message)s')

# constants #############################################################################
MAX_TIME_IN_START_S = 60     # After this time in state 'started', the game is aborted
time_started: time.time      # store the time when started

class State(Enum):
    waiting = 0
    started = 1
    finished = 2    

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
state = State.waiting     # Initial state
touched = False           # Touch state

def go_started():
    logging.info("Entering State.started")
    time_started = time.time()
    touched = False    
    state = State.started

def go_finished():
    logging.info("Entering State.finished")
    state = State.finished

def go_waiting():
    logging.info("Entering State.waiting")
    state = State.waiting

def add_one_touch():
    touched = True
    logging.info("Autsch")

def abort_started():
    logging.info("Game took too long, move to state='waiting'")
    state = State.waiting


logging.info("Starting main loop ...")
    
while True:   
    time.sleep(0.05)  # give room to other os processes
    if state == State.waiting:
        if get_wire('start'):
            go_started()
    
    elif state == State.started:
        if get_wire('start'):
            go_started()
        
        elif not touched:
            if get_wire('touch'):
                add_one_touch()
            
        elif get_wire('finish'):
            go_finished()    
            
        elif time.time() - time_started > MAX_TIME_IN_START_S:
            abort_started()
        
    elif state == State.finished:
        go_waiting()
        

    
    