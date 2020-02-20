import random
# import multiprocessing as mp
import threading as tr
import time
import zmq
from direct.showbase import DirectObject
from direct.showbase.ShowBase import ShowBase
from pubsub_classes import Subscriber as Sub

class TriggerMissiles(DirectObject.DirectObject):
    """
    Interface class between publisher and event handler
    Code for running as thread is based partly on:
        https://dev.to/hasansajedi/running-a-method-as-a-background-process-in-python-21li
    
    To do:
      Change to multiprocessing? (w/shared memory between trigger and Launch?)
    """
    def __init__(self, subscriber):
        self.sub = subscriber
        self.run_thread = tr.Thread(target = self.run)
        self.run_thread.daemon = True #let's you kill it
        self.run_thread.start()

    def run(self): 
        """
        to consider:
            remove try/except but keep while loop. it will just 
            wait until it gets a message. it will still block but
            that's ok in a process/thread problably. (Obviously take
            out the noblock stuff so it will just sit and wait)
        """
        while True:
            try:
                data = self.sub.socket.recv(flags = zmq.NOBLOCK) #recv_string()
                topic, message = data.split()
                print(topic, message)
                if message == b'1':
                    num_to_send = random.randint(1,5)
                    messenger.send("missile", [num_to_send])
            except zmq.Again:
                pass
            time.sleep(0.001)
            
    def destroy(self):
        self.run_thread.join()
        
            

class LaunchMissiles(DirectObject.DirectObject):
    def __init__(self):
        self.accept("missile", self.printMissile)
    def printMissile(self, num_missiles):
        print("\t" + "blam! "*num_missiles)
    def kill(self):
        self.ignoreAll()

if __name__ == '__main__':
    base = ShowBase()
    sub = Sub(topic = "stim")
    trigger = TriggerMissiles(sub)

    launcher = LaunchMissiles()       
    base.run()

    trigger.destroy()
    launcher.destroy()


