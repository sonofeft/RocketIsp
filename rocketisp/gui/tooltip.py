#!/usr/bin/env python
# -*- coding: ascii -*-

''' tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014
'''
from __future__ import unicode_literals

from builtins import object
import os
import sys

if sys.version_info < (3,):
    from future import standard_library
    standard_library.install_aliases()
    
from tkinter import *
    
class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info', background='white'):
        self.widget = widget
        self.text = text
        self.background = background
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
        self.tw = False
        
    def enter(self, event=None):
        x = y = 0
        
        try:
            x_y_cx_cy = self.widget.bbox("insert")
        except:
            x_y_cx_cy = None
        
        if x_y_cx_cy is not None:
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 40
            y += self.widget.winfo_rooty() - 24
            # creates a toplevel window
            self.tw = Toplevel(self.widget)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = Label(self.tw, text=self.text, justify='left',
                           background=self.background, relief='solid', borderwidth=1,
                           font=("times", "12", "normal"))
            label.pack(ipadx=1)
        
    def close(self, event=None):
        if self.tw:
            self.tw.destroy()
            
# testing ...
if __name__ == '__main__':
    root = Tk()
    btn1 = Button(root, text="button 1")
    btn1.pack(padx=10, pady=5)
    button1_ttp = CreateToolTip(btn1, "mouse is over button 1")
    btn2 = Button(root, text="button 2")
    btn2.pack(padx=10, pady=5)
    button2_ttp = CreateToolTip(btn2, "mouse is over button 2")
    root.mainloop()