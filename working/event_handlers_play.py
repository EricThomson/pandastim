# -*- coding: utf-8 -*-
"""
Playing with custom event handlers in panda3d

First create your DirectObject subclass
Second, 
"""
from direct.showbase import DirectObject
from direct.showbase.ShowBase import ShowBase
import zmq
import time


#%%
class HelloWorld(DirectObject.DirectObject):
    """
    Creates a class that listens for events: an event handler.
    You run this while running showbase and it will work.
    """
    def __init__(self):
        self.accept('h', self.printHello)
        
    def printHello(self):
        print("Hello, world!")
        

class ByeWorld(DirectObject.DirectObject):
    def __init__(self):
        self.accept('b', self.printBye)
        
    def printBye(self):
        print("Goodbye, world!")
        
class Fire:
    def __init__(self):
        self.accept('m', self.sendMissile)
        
    def sendMissile(self):
        print("Sending missiles!")
        # Could set input (3) to random number
        messenger.send("missile", [3])
        
class ConsumeMissile(DirectObject.DirectObject):
    def __init__(self):
        self.accept("missile", self.printMissile)
        
    def printMissile(self, num_missiles):
        print("blam! "*3)
        
  
# # Set up subscriber to send messages that will be consumed
# ctx = zmq.Context()
# sock = ctx.socket(zmq.SUB)
# sock.connect("tcp://127.0.0.1:1234")
# sock.subscribe("stim") # Subscribe to messages with stim topic

# print("Starting receiver loop ...")
# while True:
#     # Following makes it non-blocking (otherwise sock.recv sits and waits for a message indefinitely)
#     # https://stackoverflow.com/questions/26012132/zero-mq-socket-recv-call-is-blocking
#     try:
#         data = sock.recv(flags = zmq.NOBLOCK) #recv_string()
#         topic, message = data.split()
#         print(topic, message)
#         if message == b'1':
#             print("\tYou got a 1!")
#         elif message == b'0':
#             print("\tDo some zero processing here.")
#     except zmq.Again:
#         pass
#     time.sleep(0.1)
# sock.close()
# ctx.term()

      
# class HelloZmq(DirectObject.DirectObject):
#     def __init__(self):
        
    
base = ShowBase()     
h = HelloWorld()
b = ByeWorld()
c = ConsumeMissile()
base.run()