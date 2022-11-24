# -*- coding: utf-8 -*-

# Import libraries
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
import multiprocessing.connection
multiprocessing.connection.BUFSIZE = 2**32-1 # This is the absolute limit for this PC
from multiprocessing import Process, Pipe
import datetime
import time
import numpy as np
from itertools import cycle
import sys
import nidaqmx
import nidaqmx.system
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx import constants
import logging
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from force_profile import eval_force
import msvcrt

"""Send Morse code to LEDs via DAQ board"""


import morse

def main():
#    currentDT = datetime.datetime.now()
 #   logfolder = "../log/"
  #  os.makedirs(logfolder, exist_ok=True)
   # logging.basicConfig(filename = logfolder + "main.log", encoding='utf-8', level=logging.DEBUG)
    #logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))    



    # Reset device in case of DAQ malfunction
    """
    system = nidaqmx.system.System.local()
    for device in system.devices:
        print("Resetting device {}".format(device))
        logging.info("Resetting device {}".format(device))
        try:
            device.reset_device()
            logging.info("Device {} successfully reset".format(device))
        except:
            print("Device {} failed to reset".format(device))
            logging.warning("Device {} failed to reset".format(device))
    """        






    m = "Run 2: 2022.11.22"
    m_morse = morse.english_to_morse(m)
    m_sig = morse.morse_to_sig(m_morse)
    
    print(str(m_morse))
    print()
    print(str(m_sig))
    
    
    
    
    
    input()
    thresh_u = 5
    thresh_l = 4
    led_list = []

    for val in m_sig:
        if val == True:
            led_list.append(thresh_u)
        else:
            led_list.append(thresh_l)
            
        
    led = np.array(led_list, dtype=np.float64)    

    #led = np.array([5,5,5,5], dtype=np.float64) #At 5V, the LEDs turn on
    sampling_rate = 10

    try:    
        with nidaqmx.Task() as task0, nidaqmx.Task() as task1:
            
            ## Configure tasks
            ## Task 0 (Dev1/ao0)
            num_channels0 = 1
            num_samples0 = np.size(led)
            
            task0.ao_channels.add_ao_voltage_chan("Dev1/ao0")
            task0.ao_channels.all.ao_max = 10.0 #max_voltage
            task0.ao_channels.all.ao_min = -10.0 #min_voltage
            task0.timing.cfg_samp_clk_timing(sampling_rate,
                                             active_edge=nidaqmx.constants.Edge.RISING,
                                             sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                             samps_per_chan=num_samples0)
            
            writer0 = AnalogMultiChannelWriter(task0.out_stream, auto_start=False)
            buffer0 = np.reshape(led, (1, num_samples0))
            writer0.write_many_sample(buffer0, timeout=60)
            
            ## Task 1 (Dev1/ai0, Dev1/ai19, Dev1/ai3)
            num_channels1 = 1#3
            num_samples1 = 2 # Buffer size per channel
            
            #task1.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            #task1.ai_channels.add_ai_voltage_chan("Dev1/ai19") # Current pressure
            task1.ai_channels.add_ai_voltage_chan("Dev1/ai3")
            task1.ai_channels.all.ai_max = 10.0 #max_voltage
            task1.ai_channels.all.ai_min = -10.0 #min_voltage
            task1.timing.cfg_samp_clk_timing(sampling_rate,
                                             active_edge=nidaqmx.constants.Edge.RISING,
                                             sample_mode=constants.AcquisitionType.FINITE,
                                             samps_per_chan=num_samples1)
            
            
                                             
            
            reader1 = AnalogMultiChannelReader(task1.in_stream)
            buffer1 = np.zeros((num_channels1, num_samples1), dtype=np.float64)
            
            # Trigger causes task0 to wait for task1 to begin
            # Smaller delay without trigger
            
            task0.triggers.start_trigger.cfg_dig_edge_start_trig(task1.triggers.start_trigger.term)
            
            #task0.triggers.start_trigger.cfg_dig_edge_start_trig(task1.triggers.start_trigger.term)
            #task0.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source='Dev1/ai/StartTrigger', trigger_slope=nidaqmx.constants.Slope.RISING) # Setting the trigger on the analog input
            #task0.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source='APFI1', trigger_slope=nidaqmx.constants.Slope.RISING) # Setting the trigger on the analog input
            task0.start()

            # Attempt at reversal of trigger
            #task1.triggers.start_trigger.cfg_dig_edge_start_trig(task0.triggers.start_trigger.term)### Data acquisition doesn't start
            
            #task1.start()
            #task0.start()
            
            while True:
                try:
                    time_start = time.time()
                    reader1.read_many_sample(buffer1, num_samples1, timeout=constants.WAIT_INFINITELY)
                    time_end = time.time()
                    times = [time_start, time_end]
                    
                    data_live1 = buffer1.T.astype(np.float32)
                    print(str(data_live1))
                    
                    if task0.is_task_done():
                        time.sleep(10)
                        break
                    
                except nidaqmx.errors.DaqError as err:
                    print(err)
                    logging.error(err)
                    if task0:
                        task0.close()
                    if task1:
                        task1.close()
                    break
    except KeyboardInterrupt:
        logging.warning("Data acquisition stopped via keyboard interruption")
    finally:
        pass

    


# Run
if __name__ == "__main__":
    main()


  
