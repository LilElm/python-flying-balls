# -*- coding: utf-8 -*-

# Import libraries
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

import multiprocessing.connection as conns
conns.BUFSIZE = 2**32-1 # This is the absolute limit for this PC
# BUFSIZE is typically set as 2**13 for Windows


from multiprocessing.connection import wait
from multiprocessing import Process, Pipe, Queue
import datetime
import time
import numpy as np
#import pandas as pd
from itertools import cycle
import sys
#import pyvisa
import nidaqmx
import nidaqmx.system
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx import constants
import logging
from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from force_profile import eval_force

"""Flying balls"""


def main():

    try:
        
        
        p_live_dev1_2, p_live_dev1_1 = Pipe(duplex=False)
        p_time0_2, p_time0_1 = Pipe(duplex=False)
        
        q = Queue()
        
        
        
        
        
        processlist = []
        processlist.append(Process(target=get_data, args=(p_live_dev1_1, q, )))
        processlist.append(Process(target=manipulate_data, args=(p_live_dev1_2, q, )))
       
        
        for p in processlist:
            try:
                p.start()
                print(str(p))
            except:
                print("Error starting {}".format(p))
            
        # If get_data has ended, end all
        try:
            input("Press RETURN to stop data acquisition\n")
            pass
        except KeyboardInterrupt:
            #for p in processlist:
            #    p.kill()
            pass
        finally:
            for p in processlist:
                p.kill()
         
    
        # Close database
    except:
        pass
    finally:
        pass

    



# Function acquires and buffers live data from DAQ board and pipes it
# to manipualte_data()
# One multi-channel task has been used, as multiple tasks (at different
# sampling rates) would require multiple clocks.
def get_data(p_live, q):
    try:
        for i in range(10000):
            p_live.send(i)
            #q.put(i)
            print(str(i))
    except:
        print("errrrrr")
            

# Function recieves buffered data from get_data(), restructures it and pipes
# it to store_manipulated_data()
def manipulate_data(p_live, q):

    while True:
        try:
            # Unpackage the data
            time.sleep(10)
            data_live = p_live.recv()
            #data_live = q.get()
            
            
            
        except:
            print("errr2")
                






# Run
if __name__ == "__main__":
    main()


  
