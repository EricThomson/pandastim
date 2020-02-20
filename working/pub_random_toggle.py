"""
zeromq publisher to generate random sequence of zeroes and ones.

Setting up to pair with subscriber wrapped in event handler (see event_handlers_play.py)

"""

import zmq
import time
import random

ctx = zmq.Context()
sock = ctx.socket(zmq.PUB)
sock.bind("tcp://*:1234")

print("Starting loop...")
i = 1
while True:
    delay_time = random.uniform(0.5, 3)
    random_state = random.randint(0, 1)
    topic = b"stim_state"
    msg = str(random_state).encode('ascii')
    data = topic + b" " + msg
    sock.send(data)
    print(f"pub.py: sent data: {data}")
    i += 1
    time.sleep(delay_time)
sock.close()
ctx.term()