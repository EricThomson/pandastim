import multiprocessing as mp
import zmq

class Monitor:
    """
    Takes in a subscriber, and uses a thread to continuously monitor output of publisher
    """
    def __init__(self, subscriber):
        self.sub = subscriber
        self.monitor = mp.Process(target = self.monitor)
        
    def run(self):
        """ Start the monitor process"""
        self.monitor.start()

    def monitor(self):     
        while True:
            data = self.sub.socket.recv() #recv_string()
            topic, message = data.split()
            print(f"Topic/message: {topic}/{message}")
            if message == b'1':
                print("\tEmail just got sent")
            elif message == b'0':
                print("\tNo email sent")

                    
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
    sub = Subscriber(topic = "stim")
    mon = Monitor(sub)
    mon.run()
    