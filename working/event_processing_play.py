
# -*- coding: utf-8 -*-
"""
experiments.py: module in pandastim package
Code related to running experiments
https://github.com/EricThomson/pandastim

Includes classes and functions for running experiments (e.g., generating
sequences of stimuli, saving data) and other resources directly related
to running experiments.

"""

from direct.showbase.ShowBase import ShowBase

class EventPlay(ShowBase):
    def __init__(self):
        super().__init__()
        self.accept('b', self.pressed, ['b']) #event handler
        self.accept('g', self.pressed, ['g'])
        
    def pressed(self, data):
        print(f"{data} pressed")
        return

if __name__ == '__main__':
        event_play = EventPlay()
        event_play.run()





        #%% hi
