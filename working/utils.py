# -*- coding: utf-8 -*-
"""
utils.py
Utility functions for the pandastim repository
From the pandastim repo: https://github.com/EricThomson/pandastim
"""
import sys
def get_dpi(screen_num = 0):
    """Calculate the logical dpi of the user's monitor(s)
    Note panda3d does not scale with windows scale factor,
    so you can just use physical monitor size and pixel numbers.
    That is, this should probably be replaced by something in panda3d"""
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    screen = app.screens()[screen_num]
    dpi = screen.physicalDotsPerInch()
    app.quit()
    return dpi


if __name__ == "__main__":
    print(get_dpi())