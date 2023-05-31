import testmp
import testgame
import multiprocessing as mp
from multiprocessing import Queue
import time
import random
def play_game(game, num):
    game.play(num)
    
def test_game(num):
    print("test: ", num)

def process1_send_function(conn):
    while True:
        #accinput = random.randint(1, 10)
        accinput = testmp.main()
        conn.send(accinput)
        print("Num Sent: ", accinput)
        time.sleep(5)
  
def process2_recv_function(conn):
    g = testgame.Game()
    accqueue = mp.Queue()
    while True:
        accoutput = conn.recv()
        accqueue.put(accoutput)
        if (accqueue.qsize() > 0):
            #print("inside if")
            num = accqueue.get()
            #game_process = mp.Process(target=play_game, args=(g, num,))
            game_process = mp.Process(target=test_game, args=(num,))
            game_process.start()
            print("started")
            time.sleep(5)
            print("after 5")
            game_process.close()
            print("close")
        print("Num Recieved: ", accoutput)
  

def run():
    conn1, conn2 = mp.Pipe()
    process_1 = mp.Process(target=process1_send_function, args=(conn1,))
    process_2 = mp.Process(target=process2_recv_function, args=(conn2,))
    process_1.start()
    process_2.start()
    process_1.join()
    process_2.join()

if __name__ == "__main__":
    run()
