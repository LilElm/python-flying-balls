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

"""Flying balls"""


class InputChannel:
    def __init__(self, channel):
        self.channel = channel


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, pipe, channelDict, *args, **kwargs):
        self.pipe = pipe
        self.channelDict = channelDict
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel('left', 'Voltage (V)')
        self.graphWidget.setLabel('bottom', 'Elapsed Time (s)')
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.addLegend()
        
        self.elapsed_time = []
        index = 0
        for channel in self.channelDict:
            index = index + 1
            self.channelDict[channel].index = index
            self.channelDict[channel].data = []
            #self.channelDict[channel].line = self.graphWidget.plot(self.elapsed_time, self.channelDict[channel].data, name=channel, pen=pg.mkPen(self.channelDict[channel].index - 95))
            self.channelDict[channel].line = self.graphWidget.plot(self.elapsed_time, self.channelDict[channel].data, name=self.channelDict[channel].name, pen=pg.mkPen(self.channelDict[channel].index - 95))
    
        self.counter = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(4) # 4 ms = 250 refreshes per sec
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        self.update_plot()
    
    def update_plot(self):
        try:
            if True:
                data = self.pipe.recv()
                if self.counter == 0:
                    self.time_start = data[0]
                    self.counter = 1

                elapsed_time = data[0] - self.time_start
                self.elapsed_time.append(elapsed_time)
                        
                for channel in self.channelDict:    
                    self.channelDict[channel].data.append(data[self.channelDict[channel].index])
                    if len(self.channelDict[channel].data) > 2000: # 100 data points per sec -> 2000 data points = 20 sec
                        self.elapsed_time = self.elapsed_time[1:]
                        self.channelDict[channel].data = self.channelDict[channel].data[1:]
                    self.channelDict[channel].line.setData(self.elapsed_time, self.channelDict[channel].data)
        except:
            print("Error in update_plot()")
            

def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "main.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))    

    msg = "Evaluating force profile"
    processlist = []
    processlist.append(Process(target=loading, args=(msg, )))
    for p in processlist:
        p.start()


    # Evalute the force profile
    time_idle = 4.0
    time_acc=0.05
    time_ramp=0.2
    sampling_rate=50000
    force_profile_times, force_profile_force, force_profile_x = eval_force(time_idle, time_acc, time_ramp, sampling_rate)

    for p in processlist:
        p.kill()
    
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


    # Create pipes to send data between processes
    p_live_dev1_2, p_live_dev1_1 = Pipe(duplex=False)
    p_time0_2, p_time0_1 = Pipe(duplex=False)
    p_manip_dev1_2, p_manip_dev1_1 = Pipe(duplex=False)
    p_plot_dev1_2, p_plot_dev1_1 = Pipe(duplex=False)
    p_kill_2, p_kill_1 = Pipe(duplex=False)
    
    
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
    processlist.append(Process(target=get_data, args=(p_live_dev1_1, p_time0_1, input_channels, sampling_rate, force_profile_force, )))
    processlist.append(Process(target=manipulate_data, args=(p_live_dev1_2, p_time0_2, p_manip_dev1_1, p_plot_dev1_1, channelDict, )))
    processlist.append(Process(target=store_data, args=(p_manip_dev1_2, p_kill_1, channel_names, )))
    processlist.append(Process(target=plot_data, args=(p_plot_dev1_2, channelDict, )))
    processlist.append(Process(target=loading, args=(msg, )))
    
    for p in processlist:
        try:
            logging.info("Starting process {}".format(p))
            p.start()
            print(str(p))
        except:
            print("Error starting {}".format(p))
            logging.error("Error starting {}".format(p))
            
            
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

            

# Function acquires and buffers live data from DAQ board and pipes it
# to manipualte_data()
def get_data(p_live, p_time, input_channels, sampling_rate, force_profile_force):
    try:    
        with nidaqmx.Task() as task0, nidaqmx.Task() as task1:
            
            ## Configure tasks
            ## Task 0 (Dev1/ao0)
            num_channels0 = 1
            num_samples0 = np.size(force_profile_force)
            
            task0.ao_channels.add_ao_voltage_chan("Dev1/ao0")
            task0.ao_channels.all.ao_max = 10.0 #max_voltage
            task0.ao_channels.all.ao_min = -10.0 #min_voltage
            task0.timing.cfg_samp_clk_timing(sampling_rate,
                                             active_edge=nidaqmx.constants.Edge.RISING,
                                             sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                             samps_per_chan=num_samples0)
            
            writer0 = AnalogMultiChannelWriter(task0.out_stream, auto_start=False)
            buffer0 = np.reshape(force_profile_force, (1, num_samples0))
            writer0.write_many_sample(buffer0, timeout=60)
            
            ## Task 1 (Dev1/ai0, Dev1/ai19, Dev1/ai3)
            num_channels1 = len(input_channels)
            num_samples1 = 10000 # Buffer size per channel
            
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
        buffer_rate = 0.01 #100 data points per channel per sec
        counter = 0
        while True:
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



# Function calls Qt MainWindow (defined at top of program) to plot data
def plot_data(p_plot, channelDict):
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(p_plot, channelDict)
    w.show()
    sys.exit(app.exec_())
    


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
def loading(msg):
    time.sleep(1)
    while True:
        try:
            for frame in cycle(["|","/","-","\\"]):
                sys.stdout.write("\r" + msg + " " + frame)
                sys.stdout.flush()
                time.sleep(0.15)
            sys.stdout.write("\r")
        except KeyboardInterrupt:
            logging.warning("Pinwheel stopped via keyboard interruption")
    


# Run
if __name__ == "__main__":
    main()


  
