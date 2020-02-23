"""
pandastim/examples/pub_class_toggle3.py
zeromq publisher that generates random sequence of ints between 0-2
Useful for testing socket-based communication protocols. For instance, see
X

Needs to be paired with a subscriber that monitors its output.

Part of pandastim package: https://github.com/EricThomson/pandastim
"""

import time
import random
from utils import Publisher as Pub

pub = Pub(port = "1234")
print("Starting publisher loop to generate random outputs...")
while True:
    delay_time = random.uniform(0.5, 3)
    output = random.randint(0, 2)
    topic = b"stim"
    msg = str(output).encode('ascii')
    data = topic + b" " + msg
    pub.socket.send(data)
    print(f"pub.py: sent data: {data}")
    time.sleep(delay_time)
pub.kill()