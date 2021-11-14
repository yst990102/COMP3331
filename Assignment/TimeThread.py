from threading import Thread
from time import sleep

class TimeThread(Thread):
    def __init__(self,block_duration):
        Thread.__init__(self)
        self.block_duration = block_duration
    
    def run(self):
        while self.block_duration:
            print(self.block_duration)
            self.block_duration -= 1
            sleep(1)
            if self.block_duration == 0: break

if __name__ == "__main__":
    testthread = TimeThread(5)
    testthread.start()
    print(testthread.is_alive())
    sleep(6)
    print(testthread.is_alive())