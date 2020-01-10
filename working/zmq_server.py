# -*- coding: utf-8 -*-
"""
zmq play: build server to listen for messages

https://www.pythonforthelab.com/blog/using-pyzmq-for-inter-process-communication-part-1/
"""
from time import sleep
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
try:
    print("Binding to port 5555")
    socket.bind("tcp://*:5555")
except Exception as e:
    print(f"Exception during binding: {e}")

while True:
    message = socket.recv()
    print(f"Received message: {message}")
    sleep(1)
    socket.send(b"Message received")

