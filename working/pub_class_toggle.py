"""
zeromq publisher to generate random sequence of zeroes and ones.

Setting up to pair with subscriber wrapped in event handler (see event_handlers_play.py)

"""


import time
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
        self.socket.bind(r"tcp://127.0.0.1:" + self.port)

    def kill(self):
        self.socket.close()
        self.context.term()
    
pub = Publisher()
print("Starting loop...")
i = 1
while True:
    delay_time = random.uniform(0.5, 3)
    random_state = random.randint(0, 1)
    topic = b"stim_state"
    msg = str(random_state).encode('ascii')
    data = topic + b" " + msg
    pub.socket.send(data)
    print(f"pub_toggle.py: sent data: {data}")
    i += 1
    time.sleep(delay_time)
pub.kill()