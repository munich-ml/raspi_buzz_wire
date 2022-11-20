import logging, os, time
from enum import Enum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(funcName)15s | %(message)s')
MAX_TIME_IN_START_S = 60     # After this time in state 'started', the game is aborted
time_started: time.time      # store the time when started

class State(Enum):
    waiting = 0
    started = 1
    finished = 2    

wire_start = False
wire_finish = False
wire_touch = False
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
    time.sleep(0.05)  # give room to other os processes
    if state == State.waiting:
        if wire_start:
            go_started()
    
    elif state == State.started:
        if wire_start:
            go_started()
        
        elif wire_touch:
            add_one_touch()
            
        elif wire_finish:
            go_finished()    
            
        elif time.time() - time_started > MAX_TIME_IN_START_S:
            abort_started()
        
    elif state == State.finished:
        go_waiting()
        

    
    