# -*- coding: utf-8 -*-

# Import libraries
import os
from shutil import rmtree
import multiprocessing.connection
multiprocessing.connection.BUFSIZE = 2**32-1 # This is the absolute limit for this PC
from multiprocessing import Process, Pipe
import datetime
import time
import numpy as np
from itertools import cycle
import sys
import pyvisa



#import nidaqmx
import nidaqmx.system
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx import constants


from nidaqmx import DaqError
from nidaqmx.error_codes import DAQmxErrors
from nidaqmx._task_modules.read_functions import _read_analog_f_64
from nidaqmx.constants import READ_ALL_AVAILABLE, FillMode, AcquisitionType





import logging

from camera import start_camera
from ramp_profile import eval_ramp
from halfsine_profile import eval_halfsine
from gui import start_gui






"""Flying balls"""



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


def get_parameters(pipe_parama, pipe_buffera, pipe_consoleb):
    try:
        # Wait for user input from GUI
        
        out_path = pipe_parama.recv()
        db_env = pipe_parama.recv()
        
        save = pipe_parama.recv()
        sampling_rate = pipe_parama.recv()
        f0 = pipe_parama.recv()
        df = pipe_parama.recv()
        k = pipe_parama.recv()
        lat_profile = pipe_parama.recv()
        lat_params = pipe_parama.recv()
        long_profile = pipe_parama.recv()
        long_params = pipe_parama.recv()
        
        
        val_ni, val_ni_checkbox, val_guiresolution, val_camtimeout, val_camcheckbox = pipe_buffera.recv()
        print(f"val_ni = {val_ni}")

        #val_ni_checkbox = pipe_buffera.recv()
        print(f"val_ni_checkbox = {val_ni_checkbox}")
        #val_guiresolution = pipe_buffera.recv()
        print(f"val_guiresolution = {val_guiresolution}")
        
       # print(f"val_ni = {val_ni}")
       # print(f"val_ni_checkbox = {val_ni_checkbox}")
       # print(f"val_guiresolution = {val_guiresolution}")
       
       
        print(f"val_camtimeout = {val_camtimeout}")
        print(f"val_camcheckbox = {val_camcheckbox}")
        
        
    except Exception as e:
        print(str(e))
        pipe_consoleb.send(str(e))
    return out_path, db_env, save, sampling_rate, f0, df, k, lat_profile, lat_params, long_profile, long_params, val_ni, val_ni_checkbox, val_guiresolution, val_camtimeout, val_camcheckbox


def force_profile(outfolder, timestamp, sampling_rate, f0, df, k, profile, params, channel, coil):
    f_profile = None
    if profile == "Ramp Profile":
        drive_tar, idle, acc, ramp, rest = params
        
        # Find current drive of coil
        drive_cur = 0
        try:
            with nidaqmx.Task() as task:
                # Configure input task (Task 1) (Dev1/ai0, Dev1/ai19, Dev1/ai3)
                num_samples = 10
                rate = 1000
                data = np.zeros(num_samples)
                
                task.ai_channels.add_ai_voltage_chan(channel)
                task.ai_channels.all.ai_max = 10.0 #max_voltage
                task.ai_channels.all.ai_min = -10.0 #min_voltage
                task.timing.cfg_samp_clk_timing(rate,
                                                samps_per_chan=num_samples)
                
                data = task.read(num_samples, timeout=10.0)
                drive_cur = data[-1]
                
        except KeyboardInterrupt:
            logging.warning("Data acquisition stopped via keyboard interruption")

        
        
        f_profile = eval_ramp(f0, df, k, drive_tar, drive_cur, idle, acc, ramp, rest, sampling_rate, coil, outfolder, timestamp)
    elif profile == "Sine Profile":
        sys.exit()
    elif profile == "Half-sine Profile":
        amp, freq, idle, rest = params
        f_profile = eval_halfsine(amp, freq, idle, rest, sampling_rate, coil, outfolder, timestamp)
    elif profile == "Upload Custom":
        f_profile = []
        t = 0
        dt = 1.0 / sampling_rate
        
        path_old = params[0]
        #path_new = f"../tmp/{coil}_custom_profile.csv"
        path_new = f"{outfolder}{coil}_custom_profile_{timestamp}.csv"
        with open((path_old), "r") as f_old:
            with open((path_new), 'w') as f_new:
                f_new.write("Seconds, Profile\n")
                for line in f_old:
                    l = float(line.lower().strip("\n"))
                    f_profile.append(l)
                    f_new.write(f"{t}, {l}\n")
                    t = t + dt
                f_old.seek(0)
        
    return f_profile
    






def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    tmpfolder = "../tmp/"
    
    #if os.path.exists(tmpfolder) and os.path.isdir(tmpfolder):
     #   rmtree(tmpfolder)
    os.makedirs(logfolder, exist_ok=True)
    os.makedirs(tmpfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "main.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))
    pipe_consolea, pipe_consoleb = Pipe(duplex=False)
    
    
    # Define all input channels, including pipes for sending and receiving data
#    input_channels = ["Dev1/ai17", "Dev1/ai18", "Dev1/ai19", "Dev1/ai20", "Dev1/ai21"]
 #   input_names = ["ai17", "ai18", "ai19", "ai20", "ai21"]
    input_channels = ["Dev1/ai17", "Dev1/ai18", "Dev1/ai19", "Dev1/ai20", "Dev1/ai21", "Dev1/ai6", "Dev1/ai7"]
    input_names = ["ai17", "ai18", "ai19", "ai20", "ai21", "ai6", "ai7"]


    input_channelDict = {channel: Channel(channel=channel) for channel in input_channels}
    index = 0
    for channel in input_channelDict:
        input_channelDict[channel].name = input_names[index]
        index = index + 1
        input_channelDict[channel].index = index
    pipe_inputa, pipe_inputb = Pipe(duplex=False)
    
    
    # Define all output channels, including pipes for sending and receiving data
    output_channels = [("Dev1/ao3", "Dev1/ai3"),
                       ("Dev1/ao1", "Dev1/ai0")]
    
    
    measured_channels = [x for y,x in output_channels]
    output_names = ["Lateral Coils\nao3/ai3", "Longitudinal Coils\nao1/ai0"]
    output_channelDict = {channel: Channel(channel=channel, measured=measured) for channel,measured in output_channels}
    index = 0
    for channel in output_channelDict:
        output_channelDict[channel].name = output_names[index]
        index = index + 1
        output_channelDict[channel].index = index
    
    
    

    # Define the PSU
    try:
        rm = pyvisa.ResourceManager()
        #print(rm.list_resources())
        address = 'GPIB0::10::INSTR'
        psu = rm.open_resource(address)
        psulist = [1, 2, 3, 4]
        psuDict = {}
    except:
        logging.error("Failed to connect to the PSU")
        input("Error: Failed to connect to the PSU")
        sys.exit(1)

    
    
    # Create pipes for the GUI
    pipe_outputa, pipe_outputb = Pipe(duplex=False)
    pipe_parama, pipe_paramb = Pipe(duplex=False)
    pipe_signala, pipe_signalb = Pipe(duplex=False) # Restarts

    
    # Create pipes to send data between processes
    pipe_livea, pipe_liveb = Pipe(duplex=False)
    pipe_timea, pipe_timeb = Pipe(duplex=False)
    pipe_manipa, pipe_manipb = Pipe(duplex=False)
    pipe_store_donea, pipe_store_doneb = Pipe(duplex=False)
    pipe_man_donea, pipe_man_doneb = Pipe(duplex=False)
    pipe_cama, pipe_camb = Pipe(duplex=False)
    pipe_recorda, pipe_recordb = Pipe(duplex=False)
    pipe_msga, pipe_msgb = Pipe(duplex=False)
    pipe_buffera, pipe_bufferb = Pipe(duplex=False)
    pipe_getdataa, pipe_getdatab = Pipe(duplex=False)
    
    # Pipes to start and stop the GUI
    pipe_inputplota, pipe_inputplotb = Pipe(duplex=False)
    pipe_outputplota, pipe_outputplotb = Pipe(duplex=False)



    # Start GUI
    processlist = []
    proc0 = Process(target=start_gui, args=(input_channelDict,
                                            output_channelDict,
                                            pipe_paramb,
                                            pipe_inputa,
                                            pipe_outputa,
                                            pipe_signalb,
                                            pipe_consolea,
                                            pipe_bufferb,
                                            pipe_camb,
                                            pipe_getdatab,
                                            pipe_inputplota,
                                            pipe_inputplotb,
                                            pipe_outputplota,
                                            pipe_outputplotb, ))
    processlist.append(proc0)
    proc0.start()
    

    
    # Start message function
    msg0 = "Waiting for the camera"
    msg1 = "Waiting for user input"
    msg2 = "Evaluating force profiles"
    msg3 = "Starting acquisition"
    msg4 = "Acquiring data"
    msg5 = "Stop signal received"
    proc1 = Process(target=message, args=(pipe_msga, pipe_consoleb, msg0, ))
    processlist.append(proc1)
    proc1.start()
    


    # Connect to camera
    proc3 = Process(target=start_camera, args=(pipe_cama, pipe_recordb, ))
    processlist.append(proc3)
    proc3.start()
    pipe_camb.send(4)


    while True:
        while True:
            running = True
            # Get input parameters from the GUI and evalute the force profile
            pipe_msgb.send(msg1)
            outfolder, db_env, save, sampling_rate, f0, df, k, lat_profile, lat_params, long_profile, long_params, val_ni, val_ni_checkbox, val_guiresolution, val_camtimeout, val_camcheckbox = get_parameters(pipe_parama, pipe_buffera, pipe_consoleb)
            clear_pipes([pipe_livea, pipe_timea, pipe_manipa, pipe_store_donea, pipe_cama, pipe_recorda, pipe_parama, pipe_getdataa])
            
            if outfolder == None:
                outfolder = os.getcwd()
                outfolder = outfolder.rsplit('\\', 1)[0]
                outfolder = outfolder + "\\out\\"
            
            """
            timestamp = time.time()
            outfolder0 = outfolder + 'out_unprocessed/'
            outfolder1 = outfolder0 + f'out_{timestamp}/'
            outfolder2 = outfolder + 'out_processed/'
            os.makedirs(outfolder, exist_ok=True)
            os.makedirs(outfolder0, exist_ok=True)
            os.makedirs(outfolder1, exist_ok=True)
            os.makedirs(outfolder2, exist_ok=True)
            """
            
            
            timestamp = time.time()
            outfolder0 = "out_unprocessed/"
            outfolder1 = "out_processed/"
            outfolder00 = f"out_{timestamp}/"
            
            
            #outfolder = f"{outfolder0}out_{timestamp}/"
            #outfolder00 = "out_{timestamp}/"
    #        outfolder3 = outfolder + outfolder1
            
            outfolder_timestamp = outfolder + outfolder0 + outfolder00
            
            os.makedirs(outfolder, exist_ok=True)
            os.makedirs(f"{outfolder}{outfolder0}", exist_ok=True)
            os.makedirs(f"{outfolder}{outfolder0}{outfolder00}", exist_ok=True)
            os.makedirs(f"{outfolder}{outfolder1}", exist_ok=True)
            
            
            

            
            
            if pipe_getdataa.poll():
                while pipe_getdataa.poll():
                    pipe_getdataa.recv()
                break
            
            
            pipe_msgb.send(msg2)
            force_profile_lat = force_profile(outfolder_timestamp, timestamp, sampling_rate, f0, df, k, lat_profile, lat_params, measured_channels[0], coil="lat")
            force_profile_long = force_profile(outfolder_timestamp, timestamp, sampling_rate, f0, df, k, long_profile, long_params, measured_channels[1], coil="long")
            
            # Check length and adjust accordingly
            len_lat = len(force_profile_lat)
            len_long = len(force_profile_long)
    
                      
            while len_lat < len_long:
                val = force_profile_lat[-1]
                force_profile_lat = np.append(force_profile_lat, val)
                len_lat = len(force_profile_lat)
                
                
            while len_long < len_lat:
                val = force_profile_long[-1]
                force_profile_long = np.append(force_profile_long, val, axis=None)
                len_long = len(force_profile_long)
                
            
            # Get PSU currents
            for channel in psulist:
                try:
                    psuDict[channel] = float(psu.query(f"ISET? {channel}"))
                except:
                    # This means the PSU has reached the overvoltage protection i.e. a coil has quenched
                    try:
                        psuDict[channel] = str(psu.query(f"ISET? {channel}"))
                        print(str(psu.query(f"ISET? {channel}")))
                    except:
                        # This means that the PSU is turned off
                        print("PSU error")
                    pass
            
            
            if pipe_getdataa.poll():
                while pipe_getdataa.poll():
                    pipe_getdataa.recv()
                break
            
        
            # Create processes
            p_get_data = Process(target=get_data2, args=(pipe_liveb, pipe_timeb, input_channels, measured_channels, output_channels, sampling_rate, force_profile_lat, force_profile_long, input_channelDict, val_ni, val_ni_checkbox, pipe_getdataa, pipe_consoleb, val_guiresolution, input_channelDict, outfolder_timestamp, tmpfolder, ))
            p_man_data = Process(target=manipulate_data, args=(pipe_livea, pipe_timea, pipe_manipb, pipe_inputb, pipe_outputb, pipe_man_donea, input_channelDict, output_channelDict, val_guiresolution, pipe_consoleb, ))
            #p_store_data = Process(target=store_data, args=(pipe_manipa, pipe_store_donea, input_channels, measured_channels, psuDict, save, outfolder, outfolder0, outfolder_timestamp, outfolder1, db_env, pipe_consoleb, ))
            
            processlist2 = []
            processlist2.append(p_get_data)
            processlist2.append(p_man_data)
            #processlist2.append(p_store_data)
        
            
            if pipe_getdataa.poll():
                while pipe_getdataa.poll():
                    pipe_getdataa.recv()
                break
        
            
            # Start camera
            if val_camcheckbox:
                pipe_camb.send(True)
                cam = False
                pipe_msgb.send(msg0)
                time_cam1 = time.time()
                while not cam:
                    if pipe_recorda.poll():
                        while pipe_recorda.poll():
                            cam = pipe_recorda.recv()
                    else:
                        # Camera timeout
                        time_cam2 = time.time()
                        t = time_cam2 - time_cam1
                        if t > val_camtimeout:
                            print("Failed to communicate with the camera")
                            pipe_consoleb.send("Failed to communicate with the camera")
                            break
    
            
    
            #pipe_inputplotb.send(False)
            #pipe_outputplotb.send(False)
    
            pipe_msgb.send(msg3)
            for p in processlist2:
                try:
                    logging.info("Starting process {}".format(p))
                    p.start()
                    print(str(p))
                except:
                    running = False
                    print("Error starting {}".format(p))
                    pipe_consoleb.send("Error starting {}".format(p))
                    logging.error("Error starting {}".format(p))
                    # Stop all processes
                    for p in processlist2:
                        try:
                            p.kill()
                        except:
                            print(f"error killing process {p}")
                            pipe_consoleb.send(f"error killing process {p}")
                     
                    # Clear stop signals in case of build-up
                    while pipe_signala.poll():
                        pipe_signala.recv()
                    
                    if pipe_getdataa.poll():
                        while pipe_getdataa.poll():
                            pipe_getdataa.recv()
                        break
            
        
            # Turn on the GUI plots
            pipe_msgb.send(msg4)
            #signal_start.signal = True
        
            if pipe_getdataa.poll():
                while pipe_getdataa.poll():
                    pipe_getdataa.recv()
                break
    
    

    
    
            while running:
                # If stop signal
                if pipe_signala.poll():
                    while pipe_signala.poll():
                        pipe_signala.recv()
                    pipe_msgb.send(msg5)
                    #signal_start.signal = False
                    
    
                    
                    clear_pipes([pipe_livea, pipe_timea, pipe_manipa, pipe_store_donea, pipe_cama, pipe_recorda, pipe_parama, pipe_getdataa])
                    """
                    # Clear all pipes (fix attempt 16/02/2023)
                    if pipe_livea.poll():
                        while pipe_livea.poll():
                            pipe_livea.recv()
                            
                    
                    if pipe_timea.poll():
                        while pipe_timea.poll():
                            pipe_timea.recv()
                            
                    
                    if pipe_manipa.poll():
                        while pipe_manipa.poll():
                            pipe_manipa.recv()
                            
                    
                    if pipe_store_donea.poll():
                        while pipe_store_donea.poll():
                            pipe_store_donea.recv()
                            
                    
                    if pipe_man_donea.poll():
                        while pipe_man_donea.poll():
                            pipe_man_donea.recv()
                            
                    
                    if pipe_cama.poll():
                        while pipe_cama.poll():
                            pipe_cama.recv()
                            
                    
                    if pipe_recorda.poll():
                        while pipe_recorda.poll():
                            pipe_recorda.recv()
                            
                    if pipe_parama.poll():
                        while pipe_parama.poll():
                            pipe_parama.recv()
                    """
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    """
                    if pipe_recorda:
                        while pipe_recorda.poll():
                            cam = pipe_recorda.recv()"""
                    
                    
                    # Stop camera
                    pipe_camb.send(False)
                    # Stop all processes
                    for p in processlist2:
                        try:
                            p.kill()
                        except:
                            print(f"error killing process {p}")
                            pipe_consoleb.send(f"error killing process {p}")
                    running = False
                        
        
                if not p_get_data.is_alive():
                    running = False ####### added 12/06/23 to reset program automatically automatically
                    #pipe_inputplotb.send(False)
                    #pipe_outputplotb.send(False)
                    
                    #signal_start.signal = False ######### also added
                    clear_pipes([pipe_livea, pipe_timea, pipe_manipa, pipe_store_donea, pipe_cama, pipe_recorda, pipe_parama])
                    time.sleep(1.0)
                    pipe_camb.send(False)
                    #if p_store_data.is_alive():
                    #    pipe_store_doneb.send(True)
                    #    p_store_data.join()
                    if p_man_data.is_alive():
                        pipe_man_doneb.send(True)
                        p_man_data.join()
                        
  
    
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
   

def get_data2(p_live,
              p_time,
              input_channels,
              measured_channels,
              output_channels,
              sampling_rate,
              force_profile_lat,
              force_profile_long,
              channelDict,
              val_ni,
              val_ni_checkbox,
              pipe_getdataa,
              pipe_consoleb,
              val_guiresolution,
              input_channelDict,
              outfolder_timestamp,
              tmpfolder):
    
    """
    This has been adapted from the solution posted by GitHub user spalatofhi at
    https://github.com/ni/nidaqmx-python/issues/90 .
    """
    
    class TAMR(AnalogMultiChannelReader): # TAMR is a subclass   
    # Transposed Analog Multichannel Reader.
    # essentially a copy of the parent function, with an inverted `array_shape`
        def _verify_array(self, data, number_of_samples_per_channel,
                          is_many_chan, is_many_samp):
            if not self._verify_array_shape:
                return
            channels_to_read = self._in_stream.channels_to_read
            number_of_channels = len(channels_to_read.channel_names)
            array_shape = (number_of_samples_per_channel, number_of_channels)
            if array_shape is not None and data.shape != array_shape:
                raise DaqError(
                    'Read cannot be performed because the NumPy array passed into '
                    'this function is not shaped correctly. You must pass in a '
                    'NumPy array of the correct shape based on the number of '
                    'channels in task and the number of samples per channel '
                    'requested.\n\n'
                    'Shape of NumPy Array provided: {0}\n'
                    'Shape of NumPy Array required: {1}'
                    .format(data.shape, array_shape),
                    DAQmxErrors.UNKNOWN.value, task_name=self._task.name)

        # copy of parent method, simply using a different fill_mode argument
        def read_many_sample(self, data, 
                number_of_samples_per_channel=READ_ALL_AVAILABLE, timeout=10.0):
            number_of_samples_per_channel = (
                self._task._calculate_num_samps_per_chan(
                    number_of_samples_per_channel))

            self._verify_array(data, number_of_samples_per_channel, True, True)
            
            return _read_analog_f_64(self._handle, data,
                number_of_samples_per_channel, timeout,
                fill_mode=FillMode.GROUP_BY_SCAN_NUMBER)





    with nidaqmx.Task() as task0, nidaqmx.Task() as task1:
        # Configure output task (Task 0)
        num_samples0 = np.size(force_profile_lat)
        for channel, measured in output_channels:
            task0.ao_channels.add_ao_voltage_chan(channel)
        
        task0.ao_channels.all.ao_max = 10.0 #0.5 #max voltage
        task0.ao_channels.all.ao_min = -10.0 #0.5 #min voltage
        task0.timing.cfg_samp_clk_timing(sampling_rate,
                                         active_edge=nidaqmx.constants.Edge.RISING,
                                         sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                         samps_per_chan=num_samples0)
            
        
        try:
            writer0 = AnalogMultiChannelWriter(task0.out_stream, auto_start=False)
            buffer0 = np.vstack((force_profile_lat, force_profile_long))
            writer0.write_many_sample(buffer0, timeout=60)
        except nidaqmx.errors.DaqError as err:
            print(err)
            pipe_consoleb.send(str(err))
            logging.error(err)
            if task0:
                task0.close()
            if task1:
                task1.close()
            sys.exit(1)


        # Configure input task (Task 1)
        num_channels1 = len(input_channels) + len(measured_channels)

        for channel in input_channels:
            print(str(channel))
            task1.ai_channels.add_ai_voltage_chan(channel)
            
        for channel in measured_channels:
            print(str(channel))
            task1.ai_channels.add_ai_voltage_chan(channel)
        
        task1.ai_channels.all.ai_max = 10.0 # max voltage
        task1.ai_channels.all.ai_min = -10.0 # min voltage
        task1.timing.cfg_samp_clk_timing(sampling_rate,
                                         active_edge=nidaqmx.constants.Edge.RISING,
                                         sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        
        
        reader1 = TAMR(task1.in_stream)
        buffer1 = np.memmap(
            f"{tmpfolder}/buffer.tmp",
            dtype=np.float64,
            mode="w+",
            shape=(num_samples0, num_channels1)
            )
        buffer1[:] = -1000 # impossible output
        i = 0
        
        
        buffer_rate = 1.0 / val_guiresolution
        
        
        
        
        ##### START
        task0.triggers.start_trigger.cfg_dig_edge_start_trig(task1.triggers.start_trigger.term)
        task0.start()
        task1.start()
        

        dt = 1.0 / sampling_rate
        
        
        # evaluate which samples are to be sent to manipulate_data()
        # this is a product of dt and buffer_rate
        
        nth_interval = sampling_rate / val_guiresolution # every nth data point can be sent to manipualte_data()
        nth_data = 0
        
        
        
        
        while not task1.is_task_done() and i < num_samples0:
            n = reader1._in_stream.avail_samp_per_chan
            if n == 0: continue
            n = min(n, num_samples0-i) # prevent reading too many samples
            ##### READ
            #time_start = time.time()
            time_start = time.time()
            
            
            
            if i == 0:
                p_time.send([time_start, dt])
                #p_time.send([timestamp, dt])
                #time_next = time_start# + buffer_rate
                #timestamp = time_start
            
            i += reader1.read_many_sample(
                buffer1[i:i+n, :], # read directly into array using a view
                number_of_samples_per_channel=n
            )
            #time_end = time.time()
#            time_end = time_start + 1.0/sampling_rate * n
            #time_end = time_start + dt * (n-1)
            
            
            
            """
            # attempt at fixing dt
            
            
            
            """
             
            # Write the times to file
            # If this is changed so that each data point is exactly
            # the sampling time after the last, we don't need this step ##################### This should be changed
            #f.write(f"{time_start}, {time_end}, {n}\n")

            
            # Send required data to manipulate_data() (and hence the GUI)
            #if time_end >= time_next:  
            #print(f"i = {i}")
            #if i >= n:
            if True:
            #if i >= nth_data:
                nth_data = nth_data + nth_interval
                #times = [time_start, time_end]
                #time_next = time_next + buffer_rate
                data_live1 = buffer1[i-n:i, :].astype(np.float32)
                p_live.send(data_live1) ###currently sending more data across than necessary
                #p_live.send([data_live1, i]) ###currently sending more data across than necessary
                #p_time.send(times)
                #p_time.send([time_start, dt])
        
            
            # Break if the stop button is pressed
            if pipe_getdataa.poll():
                while pipe_getdataa.poll():
                    pipe_getdataa.recv()
                break
        
        
        # Stop and check results
        task0.stop()
        buffer1.flush()
        assert np.all(buffer1 > -1000)
        
        
        
        # Write data to disk
        pipe_consoleb.send("Writing data to disk")
        print("Writing data to disk")
        logging.info("Writing data to disk")
        channels = input_channels + measured_channels
        n = len(buffer1)
        times = []
        for j in range(n):
            time_eval = time_start + dt * j
            times.append(time_eval)
        
        
        with open((f"{outfolder_timestamp}data_{time_start}.csv"), "w+") as f:
            f.write(f"Start time: {time_start}\n")
            f.write(f"dt: {dt}\n")
            f.write("timestamp, " + ", ".join(channels) + "\n")
            

            
            
            for j in range(n):
                #dat = ', '.join(map(str, buffer1[index+j].astype(np.float32)))
                dat = ', '.join(map(str, buffer1[j].astype(np.float32)))
                f.write(f"{times[j]}, {dat}\n")
            #print(str(time_start))
            
            #for t in range(num_samples0): ###########################################################
            #    dat = ', '.join(map(str, buffer1[index+j].astype(np.float32)))
            #    f.write(f"{times[j]}, {dat}\n")
                #index = index + n
            
            
            """
            for i in range(len(time_data)-1):
                time_start = time_data[i][0]
                time_end = time_data[i][1]
                n = int(time_data[i][2])
                times = []
                time_int = (time_end - time_start) / (n-1)
                
                for j in range(n):
                    time_eval = time_start + time_int * j
                    times.append(time_eval)
                    
                for j in range(n):
                    dat = ', '.join(map(str, buffer1[index+j].astype(np.float32)))
                    f.write(f"{times[j]}, {dat}\n")
                index = index + n
            """    

    # Leave get_data()        
    print("Leaving get_data()")
    pipe_consoleb.send("Leaving get_data()")
    logging.info("Leaving get_data()")






# Function recieves buffered data from get_data(), restructures it and pipes
# it to store_data()
def manipulate_data(p_live,
                    p_time,
                    p_manip,
                    p_inputplot,
                    p_outputplot,
                    p_done,
                    input_channelDict,
                    output_channelDict,
                    val_guiresolution,
                    pipe_consoleb):
    
    try:
        #buffer_rate = 0.0125 #80 data points per channel per sec
        #buffer_rate = 0.05 #80 data points per channel per sec
        #buffer_rate = 0.01
        buffer_rate = 1.0 / val_guiresolution
        
        counter = 0
        while True:
            if p_done.poll():
                while p_done.poll():
                    p_done.recv()
                
                # Send 'done' signal to GUI plots
                p_inputplot.send(False)
                p_outputplot.send(False)
                sys.exit(0)






            # Unpackage the data
            try:    
                if p_time.poll():
                    time_start, dt = p_time.recv()
                    time_eval = time_start - dt


                if p_live.poll():# and p_time.poll():
                    data_live = p_live.recv()
                    #print(str(data_live))
                    #time_data = p_time.recv()
            
                    for channel in input_channelDict:
                        input_channelDict[channel].dat = data_live[:, input_channelDict[channel].index - 1]
                    
                    size = len(input_channelDict)
                    for channel in output_channelDict:
                        output_channelDict[channel].dat = data_live[:, size + output_channelDict[channel].index - 1]
                    
                    #time_start = time_data[0]
                    #time_end = time_data[1]
                    
                    if counter == 0:
                        counter = 1
                        time_next = time_start
                    
                    
                    # Restructure the data
                    input_man = []
                    output_man = []
                    size = len(data_live)
                    #time_int = (time_end - time_start) / size  
                    
                    
                    for i in range(size):
                        #time_eval = time_start + time_int * i
                        time_eval = time_eval + dt
                        #print(str(time_eval))
                        dummylist = []
                        for channel in input_channelDict:
                            dummylist.append(input_channelDict[channel].dat[i])
                        input_man.append([time_eval, *dummylist])
    
                        dummylist = []
                        for channel in output_channelDict:
                            dummylist.append(output_channelDict[channel].dat[i])
                        #output_man.append([time_eval, *dummylist])
                        output_man.append([*dummylist])
                        
                        
                        if time_eval >= time_next:
                            time_next = time_next + buffer_rate
                            p_inputplot.send(input_man[i])
                            p_outputplot.send([time_eval, *dummylist])
                    
                    # Send data to store_data()
                    #p_manip.send(input_man)
                    #p_manip.send(output_man)
                    
                    #time_now = time.time()
                    #time_delay = time_now - time_start
                    #print(str(time_delay))
            except:
                print("Error in manipulate_data")
                pipe_consoleb.send("Error in manipulate_data()")
                break
    except KeyboardInterrupt:
        logging.warning("Data manipulation stopped via keyboard interruption")
    finally:
        logging.info("Leaving manipulate_data()")
        print("Leaving manipulate_data()")
        pipe_consoleb.send("Leaving manipulate_data()")



# Function connects to the server, recieves manipualted data from
# manipulated_data() and inserts it in the database
def store_data(p_manip, p_done, input_channels, measured_channels, psuDict, save, outfolder, outfolder0, outfolder_timestamp, outfolder1, db_env, pipe_consoleb):
    try:
        if save:
            logging.info("Save signal received")
            channels = input_channels + measured_channels
            """
            with open((f"{outfolder1}data.csv"), "w") as f:
                f.write("timestamp, " + ", ".join(channels) + "\n")
                while True:
                    values_in = p_manip.recv()
                    values_out = p_manip.recv()
                    
                    ### Read first timestamp
                    timestamp = str(values_in[0][0])
                    
                    
                    
            """

            
            
            
            
            ### Read first timestamp
            values_in = p_manip.recv()
            values_out = p_manip.recv()
            timestamp = str(values_in[0][0])
            
            
            currents = []
            for coil in psuDict:
                currents.append(psuDict[coil])
            
            
            ### Write PSU settings to file
            with open((f"{outfolder_timestamp}coils_{timestamp}.csv"), "w") as f:
                f.write("timestamp, coil1, coil2, coil3, coil4\n")
                f.write(f"{timestamp}, " + ", ".join(map(str, currents)))
            
            
            
            
            with open((f"{outfolder_timestamp}data_{timestamp}.csv"), "w") as f:
                f.write("timestamp, " + ", ".join(channels) + "\n")
                for i in range(len(values_in)):
                    f.write(', '.join(map(str, values_in[i])) + ", " + ', '.join(map(str, values_out[i])) + "\n")
                    
                while True:
                    # Exit upon signal
                    if p_done.poll():
                        while p_done.poll():
                            p_done.recv()
                        # Store data in a database
                        # This is ran in a separate environment as to not interfere with the camera
                        os.system(f'start python mysql_update.py {outfolder} {outfolder0} {outfolder1} {db_env}')
                        sys.exit(0)
                       
                    
                    
                    if p_manip.poll():
                        values_in = p_manip.recv()
                        if p_manip.poll():
                            values_out = p_manip.recv()
                    
                            for i in range(len(values_in)):
                                f.write(', '.join(map(str, values_in[i])) + ", " + ', '.join(map(str, values_out[i])) + "\n")
                    
                   
                    
        else:
            logging.info("No save signal received")
            sys.exit(0)
                
    except KeyboardInterrupt:
        logging.warning("Data storage stopped via keyboard interruption")
        pass
    finally:
        logging.info("Leaving store_data()")
        print("Leaving store_data()")
        pipe_consoleb.send("Leaving store_data()")
        


def clear_pipes(pipes):
    for pipe in pipes:
        if pipe.poll():
            while pipe.poll():
                pipe.recv()
                






# Function shows a pretty pinwheel
def message(pipe, pipe_console, msg="Loading"):
    time.sleep(1)
    while True:
        try:
            for frame in cycle(["|","/","-","\\"]):
                if pipe.poll():
                    msg = pipe.recv()
                    pipe_console.send(msg)
                    sys.stdout.write("\n")
                
                sys.stdout.write("\r" + msg + " " + frame)
                sys.stdout.flush()
                #pipe_console.send("\r" + msg + " " + frame)
                time.sleep(0.15)
            sys.stdout.write("\r")
            #pipe_console.send("\r")

        except KeyboardInterrupt:
            logging.warning("Pinwheel stopped via keyboard interruption")
    







# Run
if __name__ == "__main__":
    #os.system('@echo off')#' start python mysql_update.py {outfolder} {outfolder0} {outfolder1} {db_env}')
    main()
    



  
