# -*- coding: utf-8 -*-
"""
zmq_client.py

This one will send message to server.
https://www.pythonforthelab.com/blog/using-pyzmq-for-inter-process-communication-part-1/
"""
import zmq

context = zmq.Context()
print("Connecting to Server on port 5555")

socket = context.socket(zmq.REQ)
socket.connect("tcp://*:5555")

print('Sending Hello')
socket.send(b"Hello")
print('Waiting for answer')
message = socket.recv()
print(f"Received: {message}")
