from direct.showbase import DirectObject
from direct.showbase.ShowBase import ShowBase
import random

class TriggerMissiles(DirectObject.DirectObject):
    """
    event handler class: to do-- try running as sep process/file see if consumer
    can consume it.
    """
    def __init__(self):
        self.accept('m', self.sendMissile)
    def sendMissile(self):
        num_missiles = random.randint(1,10)
        messenger.send("missile", [num_missiles])

class LaunchMissiles(DirectObject.DirectObject):
    def __init__(self):
        self.accept("missile", self.printMissile)
    def printMissile(self, num_missiles):
        print("\t" + "blam! "*num_missiles)

base = ShowBase()
t = TriggerMissiles()
c = LaunchMissiles()
base.run()
