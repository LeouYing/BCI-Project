import sender_filtering
import receiver_game
from multiprocessing import Process
from multiprocessing import Pipe

if __name__ == '__main__':
    # create the pipe
    conn1, conn2 = Pipe()
    
    # this will open a separate process in a shell --> helpful for debuggin 
    # --> plz do this for me cute bb gurl, or, at least, ellucidate your paradigm in your data pipeline more clearly
    # (it'll need to be placed in a separate module)
    # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    # subprocess.Popen('start /wait python python_script.py', shell=True);
    
    # start the sender
    sender_process = Process(target=sender_filtering.sender, args=(conn2,))
    sender_process.start()
    # start the receiver
    receiver_process = Process(target=receiver_game.receiver, args=(conn1,))
    receiver_process.start()
    # wait for all processes to finish
    sender_process.join()
    receiver_process.join()