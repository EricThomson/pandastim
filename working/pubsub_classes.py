import zmq

class Publisher:
    """
    Publisher wrapper class for zmq.
    """
    def __init__(self, port = "1234"):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(r"tcp://127.0.0.1:" + self.port)

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
        

