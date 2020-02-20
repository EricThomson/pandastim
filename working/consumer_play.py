"""
Use the output of pub_random_toggle in an event handler.
"""
#from direct.showbase import DirectObject
#from direct.showbase.ShowBase import ShowBase
import random
import zmq

class Publisher:
    """
    Publisher wrapper class for zmq.
    """
    def __init__(self, port = "1234"):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(r"tcp://*:" + self.port)

    def kill(self):
        self.socket.close()
        self.context.term()
    
class Subscriber:
    """
    Basic subscriber wrapper class for zmq.
    Default topic is every topic (""). 
    """
    def __init__(self, port = "1234", topic = ""):
        self.port = port
        self.topic = topic
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(r"tcp://127.0.0.1:" + self.port)
        self.socket.subscribe(self.topic)
        
    def kill(self):
        self.socket.close()
        self.context.term()
        
if __name__ == '__main__':
    sub = Subscriber("1234", topic = "stim")
    print("Starting receiver loop ...")
    while True:
        try:
            data = sub.socket.recv(flags = zmq.NOBLOCK) #recv_string()
            topic, message = data.split()
            print(topic, message)
            if message == b'1':
                print("\tYou got a 1!")
            elif message == b'0':
                print("\tDo some zero processing here.")
        except zmq.Again:
            pass
        time.sleep(0.1)
    sub.kill()
