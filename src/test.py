# -*- coding: utf-8 -*-

# Import libraries
import numpy as np
import pyvisa
import nidaqmx
import sys
import os
import time
import datetime



from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx import constants
'''
This program is a DAQ board test.
'''


def main():
    
    #rm = pyvisa.ResourceManager()
    #print(rm.list_resources())
    #address = 'ASRL3::INSTR'
    #dev = rm.open_resource(address)
    #input()
    


    
    # Measure the output voltage via the DAQ board
   # data = daq(max_voltage, min_voltage,
    #                rate, samps_per_chan, timeout)
    
    
    try:
        with nidaqmx.Task() as task:
            num_channels = 1
            num_samples = 50
            rate = 50
           
            
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.timing.cfg_samp_clk_timing(rate, sample_mode=constants.AcquisitionType.CONTINUOUS)
            reader = AnalogMultiChannelReader(task.in_stream)
            buffer = np.zeros((num_channels, num_samples), dtype=np.float64)
            while True:
                time_start = time.time()
                reader.read_many_sample(buffer, num_samples, timeout=constants.WAIT_INFINITELY)
                time_end = time.time()
                data = buffer.T.astype(np.float32)
                print(str(data))
                              
                print(str(time_start))
                print(str(time_end))
                print(str(rate))
                


    except KeyboardInterrupt:
        task.close()
    finally:
        task.close()





def daq(max_voltage, min_voltage, rate, samps_per_chan, timeout):
#    system = nidaqmx.system.System.local()
#    print(system.driver_version)
    
#    for device in system.devices:
#        print(device)
    
    with nidaqmx.Task() as task:
        #task.ai_channels.add_ai_voltage_chan(gen.channel)
        task.ai_channels.all.ai_max = max_voltage
        task.ai_channels.all.ai_min = min_voltage
        time = samps_per_chan / rate
        task.timing.cfg_samp_clk_timing(rate=rate,
                                        samps_per_chan=samps_per_chan)
        data = np.zeros(samps_per_chan)

        try:
            data = task.read(samps_per_chan, timeout=timeout)
        except KeyboardInterrupt:
            sys.exit()
        
    return data





# Run
if __name__ == "__main__":
    main()