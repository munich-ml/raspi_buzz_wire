import os
import datetime as dt

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
    
    

    
print(save_record(3, 1/3+1))