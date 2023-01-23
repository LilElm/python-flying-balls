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
from ramp_profile import eval_ramp
from halfsine_profile import eval_halfsine
import msvcrt

from gui import start_gui
from gui import SignalStart
from camera import camera
"""Flying balls"""

"""
class InputChannel:
    def __init__(self, channel):
        self.channel = channel

"""
class Channel:
    def __init__(self, channel, measured=None):
        self.channel = channel
        if measured is not None:
            self.measured = measured



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
        lat_profile = pipe_param1a.recv()
        lat_params = pipe_param1a.recv()
        long_profile = pipe_param1a.recv()
        long_params = pipe_param1a.recv()
    except Exception as e:
        print(str(e))
    return sampling_rate, lat_profile, lat_params, long_profile, long_params





def force_profile(pipe_msgb, msg2, sampling_rate, profile, params):
    pipe_msgb.send(msg2)
    if profile == "Ramp Profile":
        velocity, idle, acc, ramp, rest = params
        f_profile = eval_ramp(velocity, idle, acc, ramp, rest, sampling_rate)
    elif profile == "Sine Profile":
        exit
    elif profile == "Half-sine Profile":
        amp, freq, idle, rest = params
        f_profile = eval_halfsine(amp, freq, idle, rest, sampling_rate)
        
    elif profile == "Upload Custom":
        exit
    
    return f_profile
    
    
    
    



def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    tmpfolder = "../tmp/"
    os.makedirs(logfolder, exist_ok=True)
    os.makedirs(tmpfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "main.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))   
    
    
    # Define all input channels, including pipes for sending and receiving data
    input_channels = ["Dev1/ai17", "Dev1/ai18", "Dev1/ai19", "Dev1/ai20", "Dev1/ai21"]
    input_names = ["ai17", "ai18", "ai19", "ai20", "ai21"]
    input_channelDict = {channel: Channel(channel=channel) for channel in input_channels}
    index = 0
    for channel in input_channelDict:
        input_channelDict[channel].name = input_names[index]
        index = index + 1
        input_channelDict[channel].index = index
    pipe_inputa, pipe_inputb = Pipe(duplex=False)
    
   
    # Define all output channels, including pipes for sending and receiving data
    output_channels = ["Dev1/ao0", "Dev1/ao1"]
    measured_channels = ["Dev1/ai3", "Dev1/ai0"]
    output_names = ["Lateral Coils\nao0/ai3", "Longitudinal Coils\nao1/ai0"]
    output_channelDict = {channel: Channel(channel=channel, measured=measured) for channel in output_channels for measured in measured_channels}
    index = 0
    for channel in output_channelDict:
        output_channelDict[channel].name = output_names[index]
        index = index + 1
        output_channelDict[channel].index = index
    pipe_outputa, pipe_outputb = Pipe(duplex=False)


    # Make pipe for transferring input parameters from GUI
    pipe_param1a, pipe_param1b = Pipe(duplex=False)
    
    # Make pipe for restarting the program... Should this replace signal_start?
    pipe_signala, pipe_signalb = Pipe(duplex=False)
    
    # Create starting signal for GUI plots (deafult=False)
    signal_start = SignalStart()


    # Start GUI
    processlist = []
    proc0 = Process(target=start_gui, args=(input_channelDict, output_channelDict, pipe_param1b, pipe_inputa, pipe_outputa, signal_start, pipe_signalb))
    processlist.append(proc0)
    proc0.start()
    
    # Start message function
    pipe_msga, pipe_msgb = Pipe(duplex=False)
    msg1 = "Waiting for user input"
    msg2 = "Evaluating force profile"
    msg3 = "Acquiring data"
    msg4 = "Stop signal received"
    proc1 = Process(target=message, args=(pipe_msga, msg1, ))
    processlist.append(proc1)
    proc1.start()

    # Get input parameters from the GUI and evalute the force profile
    sampling_rate, lat_profile, lat_params, long_profile, long_params = get_parameters(pipe_param1a)
    force_profile_lat = force_profile(pipe_msgb, msg2, sampling_rate, lat_profile, lat_params)
    force_profile_long = force_profile(pipe_msgb, msg2, sampling_rate, long_profile, long_params)
    
    
    

    


    # Create pipes to send data between processes
    pipe_livea, pipe_liveb = Pipe(duplex=False)
    pipe_timea, pipe_timeb = Pipe(duplex=False)
    pipe_manipa, pipe_manipb = Pipe(duplex=False)
    pipe_killa, pipe_killb = Pipe(duplex=False)
    pipe_cama, pipe_camb = Pipe(duplex=False)
    pipe_recorda, pipe_recordb = Pipe(duplex=False)
    
    
    
    # Create processes
    processlist2 = []
    proc_cam = Process(target=camera, args=(pipe_cama, pipe_recordb, ))
    processlist2.append(proc_cam)
    #processlist2.append(Process(target=camera, args=(pipe_cama, pipe_recordb, )))
    processlist2.append(Process(target=get_data, args=(pipe_liveb, pipe_timeb, input_channels, measured_channels, output_channels, sampling_rate, force_profile_lat, force_profile_long, input_channelDict, )))
    processlist2.append(Process(target=manipulate_data, args=(pipe_livea, pipe_timea, pipe_manipb, pipe_inputb, pipe_outputb, input_channelDict, output_channelDict, )))
    processlist2.append(Process(target=store_data, args=(pipe_manipa, pipe_killb, input_channels, measured_channels, )))

 
        
    
    for p in processlist2:
        try:
            logging.info("Starting process {}".format(p))
            p.start()
            print(str(p))
            if p == proc_cam:
                cont = False
                while not cont:
                    if pipe_recorda.poll():
                        cont = pipe_recorda.recv()
        except:
            print("Error starting {}".format(p))
            logging.error("Error starting {}".format(p))
    
    
    # Turn on the GUI plots
    pipe_msgb.send(msg3)
    signal_start.signal = True
    
    
    
    
    while True:
        # If stop signal
        if pipe_signala.poll():
            while pipe_signala.poll():
                pipe_signala.recv()
            pipe_msgb.send(msg4)
            signal_start.signal = False
            
            # Stop camera
            pipe_camb.send(True)
            proc_cam.join()
            
            # Stop all processes
            for p in processlist2:
                try:
                    p.kill()
                except:
                    print("error killing process")
            
            # Recreate 'new' processes (processes cannot be reused)
            processlist2 = []
            proc_cam = Process(target=camera, args=(pipe_cama, pipe_recordb, ))
            processlist2.append(proc_cam)
            #processlist2.append(Process(target=camera, args=(pipe_cama, pipe_recordb, )))
            processlist2.append(Process(target=get_data, args=(pipe_liveb, pipe_timeb, input_channels, measured_channels, output_channels, sampling_rate, force_profile_lat, force_profile_long, input_channelDict, )))
            processlist2.append(Process(target=manipulate_data, args=(pipe_livea, pipe_timea, pipe_manipb, pipe_inputb, pipe_outputb, input_channelDict, output_channelDict, )))
            processlist2.append(Process(target=store_data, args=(pipe_manipa, pipe_killb, input_channels, measured_channels, )))

            
            # Get input parameters from the GUI
            pipe_msgb.send(msg1)
            sampling_rate, lat_profile, lat_params, long_profile, long_params = get_parameters(pipe_param1a)
            


                
            
            # Clear stop signals in case of build-up
            while pipe_signala.poll():
                pipe_signala.recv()
            
            
            # Evalute the force profiles
            force_profile_lat = force_profile(pipe_msgb, msg2, sampling_rate, lat_profile, lat_params)
            force_profile_long = force_profile(pipe_msgb, msg2, sampling_rate, long_profile, long_params)
            
            # Start processes
            for p in processlist2:
                try:
                    logging.info("Starting process {}".format(p))
                    p.start()
                    print(str(p))
                    if p == proc_cam:
                        cont = False
                        while not cont:
                            if pipe_recorda.poll():
                                cont = pipe_recorda.recv()
                except:
                    print("Error starting {}".format(p))
                    logging.error("Error starting {}".format(p))

            
            # Turn on the GUI plots
            pipe_msgb.send(msg3)
            signal_start.signal = True
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
   
    

# Function acquires and buffers live data from DAQ board and pipes it
# to manipualte_data()
def get_data(p_live, p_time, input_channels, measured_channels, output_channels, sampling_rate, force_profile_lat, force_profile_long, channelDict):
    try:
        with nidaqmx.Task() as task0, nidaqmx.Task() as task1:
            
            
            # Configure output task (Task 0)
            num_channels0 = len(output_channels)
            num_samples0 = np.size(force_profile_lat)
            for channel in output_channels:
                task0.ao_channels.add_ao_voltage_chan(channel)
            
            task0.ao_channels.all.ao_max = 10.0 #max_voltage
            task0.ao_channels.all.ao_min = -10.0 #min_voltage
            
            
            task0.timing.cfg_samp_clk_timing(sampling_rate,
                                             active_edge=nidaqmx.constants.Edge.RISING,
                                             sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                             samps_per_chan=num_samples0)
                
            
            
            writer0 = AnalogMultiChannelWriter(task0.out_stream, auto_start=False)
            buffer0 = np.vstack((force_profile_lat, force_profile_long))
            writer0.write_many_sample(buffer0, timeout=60)
            
            
            
            # Configure input task (Task 1) (Dev1/ai0, Dev1/ai19, Dev1/ai3)
            num_channels1 = len(input_channels) + len(measured_channels)
            
            # The buffer size must be sufficiently high, otherwise the buffer will overwrite itself
            # However, if the buffer size is large, so too will be the delay
            # Moreover, if the buffer is not a complete multiple of the sampling rate, data will be truncated
            #num_samples1 = int(4*sampling_rate / 1) # Buffer size per channel
            
            if sampling_rate <= 10000:
                num_samples1 = int(sampling_rate)
            elif sampling_rate <= 50000:
                num_samples1 = int(sampling_rate * 2)
            else:
                num_samples1 = int(sampling_rate * 5)
            
            for channel in input_channels:
                task1.ai_channels.add_ai_voltage_chan(channel)
                
            for channel in measured_channels:
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
def manipulate_data(p_live, p_time, p_manip, p_inputplot, p_outputplot, input_channelDict, output_channelDict):
    try:
        buffer_rate = 0.01 #100 data points per channel per sec
        counter = 0
        while True:
            try:
                # Unpackage the data
                data_live = p_live.recv()
                time_data = p_time.recv()
                
                for channel in input_channelDict:
                    input_channelDict[channel].dat = data_live[:, input_channelDict[channel].index - 1]
                
                size = len(input_channelDict)
                for channel in output_channelDict:
                    output_channelDict[channel].dat = data_live[:, size + output_channelDict[channel].index - 1]
                
                time_start = time_data[0]
                time_end = time_data[1]
                
                if counter == 0:
                    counter = 1
                    time_next = time_start
                
                
                # Restructure the data
                input_man = []
                output_man = []
                size = len(data_live)
                time_int = (time_end - time_start) / size  
                
                
                for i in range(size):
                    time_eval = time_start + time_int * i
                    dummylist = []
                    for channel in input_channelDict:
                        dummylist.append(input_channelDict[channel].dat[i])
                    input_man.append([time_eval, *dummylist])

                    dummylist = []
                    for channel in output_channelDict:
                        dummylist.append(output_channelDict[channel].dat[i])
                    output_man.append([time_eval, *dummylist])
                    
                    
                    if time_eval >= time_next:
                        time_next = time_next + buffer_rate
                        p_inputplot.send(input_man[i])
                        p_outputplot.send(output_man[i])
                
                # Send data to store_data()
                p_manip.send(input_man)
                p_manip.send(output_man)
            except:
                print("Error in data manipulation")
                break
    except KeyboardInterrupt:
        logging.warning("Data manipulation stopped via keyboard interruption")
    finally:
        pass



# Function connects to the server, recieves manipualted data from
# manipulated_data() and inserts it in the database
def store_data(p_manip, p_kill, input_channels, measured_channels):
    try:
        tmpfolder = '../tmp/'
        channels = input_channels + measured_channels
        
        timenow = time.time()
        
        with open((tmpfolder + str(timenow) + "_data.csv"), "w") as f:
            f.write("timestamp, " + ", ".join(channels) + "\n")
            while True:

                values_in = p_manip.recv()
                values_out = p_manip.recv()
                
                for i in range(len(values_in)):
                    f.write(', '.join(map(str, values_in[i])) + ', '.join(map(str, values_out[i])) + "\n")
                
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
def message(pipe, msg="Loading"):
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


  
