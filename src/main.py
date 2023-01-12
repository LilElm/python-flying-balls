# -*- coding: utf-8 -*-

# Import libraries
import os
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

from gui import start_gui
from gui import SignalStart
"""Flying balls"""

"""
class InputChannel:
    def __init__(self, channel):
        self.channel = channel

"""
class Channel:
    def __init__(self, channel):
        self.channel = channel



def gen_numbers(channelDict):
    while True:
        for channel in channelDict:
            numbers = np.random.rand(4)
            channelDict[channel].pipeb.send(numbers)
        time.sleep(1)


def get_parameters(pipe_param1a):
    try:
        # Wait for user input from GUI
        sampling_rate = pipe_param1a.recv()
        lat_params = pipe_param1a.recv()
        long_params = pipe_param1a.recv()
    except Exception as e:
        print(str(e))
    return sampling_rate, lat_params, long_params





def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "main.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))    

    

    # Make pipe for transferring input parameters from GUI
    pipe_param1a, pipe_param1b = Pipe(duplex=False)
    
    # Make pipe for restarting the program... Should this replace signal_start?
    pipe_signala, pipe_signalb = Pipe(duplex=False)
    
    
    # Define all input channels, including pipes for sending and receiving data
    input_channels = ["Dev1/ai0", "Dev1/ai19", "Dev1/ai3", "Dev1/ai13", "Dev1/ai1"]
    input_names = ["ai0", "ai19", "ai3", "ai13", "ai1"]
    input_channelDict = {channel: Channel(channel=channel) for channel in input_channels}
    index = 0
    for channel in input_channelDict:
        input_channelDict[channel].name = input_names[index]
        #input_channelDict[channel].pipea, input_channelDict[channel].pipeb = Pipe(duplex=False)
        index = index + 1
        input_channelDict[channel].index = index
    
   
    pipe_plota, pipe_plotb = Pipe(duplex=False)
   
    
   
    
      
    # Define all output channels, including pipes for sending and receiving data
    output_channels = ["Dev1/ao0", "Dev1/ao1"]
    output_names = ["ao0", "ao1"]
    output_channelDict = {channel: Channel(channel=channel) for channel in output_channels}
    index = 0
    for channel in output_channelDict:
        output_channelDict[channel].name = output_names[index]
        #output_channelDict[channel].pipea, output_channelDict[channel].pipeb = Pipe(duplex=False)
        index = index + 1
        output_channelDict[channel].index = index
    
   
    
   
    
   
    
   
    
    #### Create starting signal for GUI plots (deafult=False)
    signal_start = SignalStart()
    



    # Start GUI
    processlist = []
    proc0 = Process(target=start_gui, args=(input_channelDict, pipe_param1b, pipe_plota, signal_start, pipe_signalb))
    processlist.append(proc0)
    proc0.start()
    
    # Start loading function
    pipe_msga, pipe_msgb = Pipe(duplex=False)
    msg1 = "Acquiring data"
    msg2 = "Waiting for user input"
    proc1 = Process(target=loading, args=(pipe_msga, msg2, ))
    processlist.append(proc1)
    proc1.start()
    
    # Create a process to generate random numbers
    # This will be replaced by the proper processes later
    proc2 = Process(target=gen_numbers, args=(input_channelDict, ))
    processlist.append(proc2)

    #proc2.start()

    

    
    #############################################################################################################
    

    # Will only progress past get_parameters() once START has been pressed

    # Get input parameters from the GUI
    sampling_rate, lat_params, long_params = get_parameters(pipe_param1a)
    lat_velocity, lat_idle, lat_acc, lat_ramp, lat_rest = lat_params
    long_velocity, long_idle, long_acc, long_ramp, long_rest = long_params
    
    
    
    
    #while True:
     #   for channel in input_channelDict: 
      #      input_channelDict[channel].pipeb.send([0.25, 1.0, 2.0, 0.0, 0.25, 1.0, 2.0, 0.0])
       # time.sleep(0.2)

    
    
    # Evalute the force profile
    force_profile_times_lat, force_profile_force_lat, force_profile_x_lat = eval_force(lat_velocity, lat_idle, lat_acc, lat_ramp, lat_rest, sampling_rate)
    force_profile_times_long, force_profile_force_long, force_profile_x_long = eval_force(long_velocity, long_idle, long_acc, long_ramp, long_rest, sampling_rate)
  
    
    # Turn on the GUI plots
    signal_start.signal = True
    
    
    
    #############################################################################################################
    # Create pipes to send data between processes
    pipe_livea, pipe_liveb = Pipe(duplex=False)
    pipe_timea, pipe_timeb = Pipe(duplex=False)
    pipe_manipa, pipe_manipb = Pipe(duplex=False)
    pipe_killa, pipe_killb = Pipe(duplex=False)
    
  
    
    
    # Create processes
    processlist2 = []
    processlist2.append(Process(target=get_data, args=(pipe_liveb, pipe_timeb, input_channels, output_channels, sampling_rate, force_profile_force_lat, force_profile_force_long, input_channelDict, )))
    processlist2.append(Process(target=manipulate_data, args=(pipe_livea, pipe_timea, pipe_manipb, pipe_plotb, input_channelDict, )))
    processlist2.append(Process(target=store_data, args=(pipe_manipa, pipe_killb, input_names, )))
       
    # Update loading function message
    pipe_msgb.send(msg1)
        
    
    for p in processlist2:
        try:
            logging.info("Starting process {}".format(p))
            p.start()
            print(str(p))
        except:
            print("Error starting {}".format(p))
            logging.error("Error starting {}".format(p))
    
    
    
    
    
    
    while True:
        if pipe_signala.poll(): #if stop signal
            pipe_signala.recv()
            
            print("stop signal received")
            
            # Stop all processes
            for p in processlist2:
                try:
                    p.kill()
                except:
                    print("error killing process")
            
            # Recreate 'new' processes (processes cannot be reused)
            processlist2 = []
            processlist2.append(Process(target=get_data, args=(pipe_liveb, pipe_timeb, input_channels, output_channels, sampling_rate, force_profile_force_lat, force_profile_force_long, input_channelDict, )))
            processlist2.append(Process(target=manipulate_data, args=(pipe_livea, pipe_timea, pipe_manipb, pipe_plotb, input_channelDict, )))
            processlist2.append(Process(target=store_data, args=(pipe_manipa, pipe_killb, input_names, )))
            
            # Update loading function message
            pipe_msgb.send(msg2)
            
            # Start processes
            for p in processlist2:
                try:
                    p.start()
                except:
                    print("error starting process")
            
            # Send loading function message
            pipe_msgb.send(msg1)
            time.sleep(0.125)
            
            
            
        else: #if no signal
            time.sleep(0.125)
    
    
    
    
    
    
    
    """
            
            
    # If store_data() has ended, end all
    # Nota bene, the 'msvcrt' method will only work with Windows
    print("Press RETURN to stop data acquisition\n")
    try:
        while True:
            if msvcrt.kbhit():
                if msvcrt.getch()==b'\r':
                    print("Data acquisition stopped via keyboard interruption")
                    logging.warning("Data acquisition stopped via keyboard interruption")
                    break
            if pipe_killa.poll():
                print("Data acquisition stopped via store_data()")
                logging.warning("Data acquisition stopped via store_data()")
                break
            
    except KeyboardInterrupt:
        logging.warning("Data acquisition stopped via keyboard interruption")
        print("Data acquisition stopped via keyboard interruption")
        pass
    finally:
        for p in processlist2:
            logging.info("Killing process {}".format(p))
            p.kill()
     
    
    print("Program completed successfully")
    
    """
            
            
    
    
    
    
    
    
    """
    
    while True:
        
        if pipe_signala.poll():
            print("a")
            time.sleep(1)
           # proc1.kill()
           # proc2.kill()
           # print("fcnlskjbcnbnjskl")
        else: #if no signal
            
            
        
        
            # Wait for user input from GUI
            sampling_rate = pipe_param1a.recv()
            lat_params = pipe_param1a.recv()
            long_params = pipe_param1a.recv()
            lat_velocity, lat_idle, lat_acc, lat_ramp, lat_rest = lat_params
            long_velocity, long_idle, long_acc, long_ramp, longt_rest = long_params
            
            
            # Start pinwheel
          #  msg = "Evaluating force profile"
            #proc1 = Process(target=loading, args=(msg, ))
            #processlist.append(proc1)
            proc1.start()
        
        
            # Evalute the force profile
            force_profile_times, force_profile_force, force_profile_x = eval_force(lat_velocity, lat_idle, lat_acc, lat_ramp, lat_rest, sampling_rate)
            proc1.kill()
            
            # Turn on the GUI plots (and throw some random numbers at them)
            signal_start.signal = True
            
            #proc2 = Process(target=gen_numbers, args=(pipeDict_send, ))
        #    proc2 = Process(target=gen_numbers, args=(channelDict, ))
        #    processlist.append(proc2)
            proc2.start()
    

    """

    
    input("done")
    
    for p in processlist:
        p.kill()
        
    for p in processlist2:
        p.kill()
        
        
    input("done")
    
    pass
    
    """
    # Reset device in case of DAQ malfunction
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
    """
    # Create pipes to send data between processes
    pipe_livea, pipe_liveb = Pipe(duplex=False)
    pipe_timea, pipe_timeb = Pipe(duplex=False)
    pipe_manipa, pipe_manipb = Pipe(duplex=False)
    pipe_plota, pipe_plotb = Pipe(duplex=False)
    pipe_killa, pipe_killb = Pipe(duplex=False)
    
    
    # Define all input channels
    input_channels = ["Dev1/ai0", "Dev1/ai19", "Dev1/ai3", "Dev1/ai13"]
    channel_names = ["ai0", "ai19", "ai3", "ai13"]
    channelDict = {channel: InputChannel(channel=channel) for channel in input_channels}
    index = 0
    for channel in channelDict:
        channelDict[channel].name = channel_names[index]
        index = index + 1
        channelDict[channel].index = index

    # Create processes
    msg = "Running"
    processlist = []
    processlist.append(Process(target=get_data, args=(pipe_liveb, pipe_timeb, input_channels, sampling_rate, force_profile_force, )))
    processlist.append(Process(target=manipulate_data, args=(pipe_livea, pipe_timea, pipe_manipb, pipe_plotb, channelDict, )))
    processlist.append(Process(target=store_data, args=(pipe_manipa, pipe_killb, channel_names, )))
    #processlist.append(Process(target=plot_data, args=(pipe_plota, channelDict, )))
    processlist.append(Process(target=loading, args=(msg, )))
    
    
    for p in processlist:
        try:
            logging.info("Starting process {}".format(p))
            p.start()
            print(str(p))
        except:
            print("Error starting {}".format(p))
            logging.error("Error starting {}".format(p))
            
    """
            
    """
    # If store_data() has ended, end all
    # Nota bene, the 'msvcrt' method will only work with Windows
    print("Press RETURN to stop data acquisition\n")
    try:
        while True:
            if msvcrt.kbhit():
                if msvcrt.getch()==b'\r':
                    print("Data acquisition stopped via keyboard interruption")
                    logging.warning("Data acquisition stopped via keyboard interruption")
                    break
            if p_kill_2.poll():
                print("Data acquisition stopped via store_data()")
                logging.warning("Data acquisition stopped via store_data()")
                break
            
    except KeyboardInterrupt:
        logging.warning("Data acquisition stopped via keyboard interruption")
        print("Data acquisition stopped via keyboard interruption")
        pass
    finally:
        for p in processlist:
            logging.info("Killing process {}".format(p))
            p.kill()
     
    
    print("Program completed successfully")
#    input("Program completed successfully")

    """        

# Function acquires and buffers live data from DAQ board and pipes it
# to manipualte_data()
def get_data(p_live, p_time, input_channels, output_channels, sampling_rate, force_profile_force_lat, force_profile_force_long, channelDict):
    try:
        

        
        
        
        with nidaqmx.Task() as task0, nidaqmx.Task() as task1:
            
            
            # Configure output task (Task 0)
            num_channels0 = len(output_channels)
            num_samples0 = np.size(force_profile_force_lat)
            for channel in output_channels:
                task0.ao_channels.add_ao_voltage_chan(channel)
            
            task0.ao_channels.all.ao_max = 10.0 #max_voltage
            task0.ao_channels.all.ao_min = -10.0 #min_voltage
            
            
            task0.timing.cfg_samp_clk_timing(sampling_rate,
                                             active_edge=nidaqmx.constants.Edge.RISING,
                                             sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                             samps_per_chan=num_samples0)
                
            
            
            writer0 = AnalogMultiChannelWriter(task0.out_stream, auto_start=False)
            #buffer0 = np.reshape(force_profile_force, (1, num_samples0))
            
            buffer0 = np.vstack((force_profile_force_lat, force_profile_force_long))
            
            writer0.write_many_sample(buffer0, timeout=60)
            
            
            #######################################################
            #######################################################
            
            
            
            
            
            
            # Configure input task (Task 1) (Dev1/ai0, Dev1/ai19, Dev1/ai3)
            num_channels1 = len(input_channels)
            num_samples1 = 10000 # Buffer size per channel
            num_samples1 = 2 # Buffer size per channel
            
            for channel in input_channels:
                task1.ai_channels.add_ai_voltage_chan(channel)
            
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
            task0.start()
            
            while True:
                try:
                    time_start = time.time()
                    reader1.read_many_sample(buffer1, num_samples1, timeout=constants.WAIT_INFINITELY)
                    time_end = time.time()
                    times = [time_start, time_end]
                    
                    data_live1 = buffer1.T.astype(np.float32)
                    p_live.send(data_live1)
                    p_time.send(times)
                    
                    
                   
                    
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



# Function recieves buffered data from get_data(), restructures it and pipes
# it to store_data()
def manipulate_data(p_live, p_time, p_manip, p_plot, channelDict):
    try:  
        
        
        
        #while True:
         #   for channel in channelDict: 
          #      channelDict[channel].pipeb.send([0.25, 1.0, 2.0, 0.0, 0.25, 1.0, 2.0, 0.0])
           # time.sleep(0.2)
        
        
        
        
        buffer_rate = 0.01 #100 data points per channel per sec
        counter = 0
        while True:
            
            """
            for channel in channelDict: 
                channelDict[channel].pipeb.send([0.25, 1.0, 2.0, 0.0, 0.25, 1.0, 2.0, 0.0])
                print("sent")
                time.sleep(0.2)
            """
            
            try:
                # Unpackage the data
                data_live = p_live.recv()
                time_data = p_time.recv()
                
                for channel in channelDict:
                    channelDict[channel].dat = data_live[:,channelDict[channel].index - 1]
                
                time_start = time_data[0]
                time_end = time_data[1]
                
                if counter == 0:
                    counter = 1
                    time_next = time_start
                
                
                # Restructure the data
                data_manipulated = []
                size = len(data_live)
                time_int = (time_end - time_start) / size  
                
                
                for i in range(size):
                    time_eval = time_start + time_int * i
                    dummylist = []
                    for channel in channelDict:
                        dummylist.append(channelDict[channel].dat[i])
                    data_manipulated.append([time_eval, *dummylist])
                    
                    
                   
                    if time_eval >= time_next:
                        time_next = time_next + buffer_rate
                        p_plot.send(data_manipulated[i])
                
                p_manip.send(data_manipulated)
               
            except:
                print("Error in data manipulation")
                break
    except KeyboardInterrupt:
        logging.warning("Data manipulation stopped via keyboard interruption")
    finally:
        pass


"""
# Function calls Qt MainWindow (defined at top of program) to plot data
def plot_data(p_plot, channelDict):
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(p_plot, channelDict)
    w.show()
    sys.exit(app.exec_())
"""


# Function connects to the server, recieves manipualted data from
# manipulated_data() and inserts it in the database
def store_data(p_manip, p_kill, channel_names):
    try:
        tmpfolder = '../tmp/'
        with open((tmpfolder + "data.csv"), "w") as f:
            f.write("timestamp, " + ", ".join(channel_names) + "\n")
            while True:

                values = p_manip.recv()
                
                for i in range(len(values)):
                    f.write(', '.join(map(str, values[i])) + "\n")
                
                # Exit if pipe is empty
                # Send kill signal
                # This is not an elegant solution. Consider revising
                if p_manip.poll() is False:
                    time.sleep(2)
                if p_manip.poll() is False:                    
                    p_kill.send(True)
                    break
                
    except KeyboardInterrupt:
        logging.warning("Data storage stopped via keyboard interruption")
        pass
    finally:
        
        p_kill.send(True)
        logging.info("Process kill signal sent from store_data()")



# Function shows a pretty pinwheel
def loading(pipe, msg="Loading"):
    time.sleep(1)
    while True:
        try:
            for frame in cycle(["|","/","-","\\"]):
                if pipe.poll():
                    msg = pipe.recv()
                    sys.stdout.write("\n")
                
                sys.stdout.write("\r" + msg + " " + frame)
                sys.stdout.flush()
                time.sleep(0.15)
            sys.stdout.write("\r")

        except KeyboardInterrupt:
            logging.warning("Pinwheel stopped via keyboard interruption")
    


# Run
if __name__ == "__main__":
    main()


  
