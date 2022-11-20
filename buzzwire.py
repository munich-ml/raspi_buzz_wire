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
gpio_numbers = {"start": 10,
                "finish": 9,
                "touch": 11}

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
for gpio_number in gpio_numbers.values():
    gpio.setup(gpio_number, gpio.IN, pull_up_down=gpio.PUD_OFF)


# init ##################################################################################
state = State.waiting     # Initial state

def go_started():
    logging.info("Entering State.started")
    time_started = time.time()    
    state = State.started

def go_finished():
    logging.info("Entering State.finished")
    state = State.finished

def go_waiting():
    logging.info("Entering State.waiting")
    state = State.waiting

def add_one_touch():
    logging.info("")

def abort_started():
    logging.info("Game took too long, move to state='waiting'")
    state = State.waiting


logging.info("Starting main loop ...")

while True:
    time.sleep(0.2)
    wire_start = not(gpio.input(gpio_numbers["start"]))
    wire_finish = not(gpio.input(gpio_numbers["finish"]))
    wire_touch = not(gpio.input(gpio_numbers["touch"]))

    logging.info(f"{wire_start=}\t{wire_finish=}\t{wire_touch=}")
#while True:   
#    time.sleep(0.05)  # give room to other os processes
#    if state == State.waiting:
#        if wire_start:
#            go_started()
#    
#    elif state == State.started:
#        if wire_start:
#            go_started()
#        
#        elif wire_touch:
#            add_one_touch()
#            
#        elif wire_finish:
#            go_finished()    
#            
#        elif time.time() - time_started > MAX_TIME_IN_START_S:
#            abort_started()
#        
#    elif state == State.finished:
#        go_waiting()
        

    
    