import nidaqmx.system
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx import constants


from nidaqmx import DaqError
from nidaqmx.error_codes import DAQmxErrors
from nidaqmx._task_modules.read_functions import _read_analog_f_64
from nidaqmx.constants import READ_ALL_AVAILABLE, FillMode, AcquisitionType


import numpy as np
import sys

import threading

def daq_single(sampling_rate=1, num_samples=4, input_channels=None):
    
    data = np.zeros(num_samples)
    try:
        with nidaqmx.Task() as task:
            for channel in input_channels:
                task.ai_channels.add_ai_voltage_chan(channel)
            
            task.ai_channels.all.ai_max = 10.0 #0.5 #max voltage
            task.ai_channels.all.ai_min = -10.0 #0.5 #min voltage
            task.timing.cfg_samp_clk_timing(sampling_rate,
                                            samps_per_chan=num_samples)
                
            data = task.read(num_samples, timeout=10.0)
            return data
            #input(f"{data}")
    except nidaqmx.errors.DaqError as err:
        print(err)
        if task:
            task.close()
        sys.exit(1)
            
        



def daq_continuous_simple(sampling_rate=1, num_samples=4, input_channels=None):

    num_channels = len(input_channels)
    data = np.zeros([num_channels, num_samples])
    try:
        with nidaqmx.Task() as task:
    
            
            
            for channel in input_channels:
                task.ai_channels.add_ai_voltage_chan(channel)
            
            task.ai_channels.all.ai_max = 10.0 #0.5 #max voltage
            task.ai_channels.all.ai_min = -10.0 #0.5 #min voltage
            task.timing.cfg_samp_clk_timing(sampling_rate,
                                            samps_per_chan=num_samples)
            
            
            reader = AnalogMultiChannelReader(task.in_stream)
            
            while True:
                reader.read_many_sample(data=data, 
                                        number_of_samples_per_channel=num_samples,
                                        timeout=10.0)
            
            
            
                print(f"{data}")
    except nidaqmx.errors.DaqError as err:
        print(err)
        if task:
            task.close()
        sys.exit(1)
            
        

def daq_continuous_adv(sampling_rate=1, num_samples=4,
                       input_channel_dict=None, output_channel_dict=None,
                       main_thread_id=None):
    print(f"sampling rate = {sampling_rate}")
    input_channels = []
    for channel in input_channel_dict:
        input_channels.append(input_channel_dict[channel].channel)
    
    
    
    force_profiles = []
    for channel in output_channel_dict:
        input_channels.append(output_channel_dict[channel].channel)
        force_profiles.append(output_channel_dict[channel].force_profile)
        #print(f"\n==\nfp = {output_channel_dict[channel].force_profile}\n\n")
    
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
        
    
    
    
    
        

    with nidaqmx.Task() as task_output, nidaqmx.Task() as task_input:
        # Configure output task
        num_samples = np.size(force_profiles[0])
        
        for channel in output_channel_dict:
            task_output.ao_channels.add_ao_voltage_chan(output_channel_dict[channel].channel_output)
        task_output.ao_channels.all.ao_max = 10.0 #0.5 #max voltage
        task_output.ao_channels.all.ao_min = -10.0 #0.5 #min voltage
        task_output.timing.cfg_samp_clk_timing(sampling_rate,
                                               active_edge=nidaqmx.constants.Edge.RISING,
                                               sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                               samps_per_chan=num_samples)
     
        try:
            writer = AnalogMultiChannelWriter(task_output.out_stream, auto_start=False)
            #buffer_output = np.vstack((force_profiles[0], force_profiles[1]))
            buffer_output = np.vstack((force_profiles))
            #buffer0 = np.vstack((force_profile_lat, force_profile_long))
            writer.write_many_sample(buffer_output, timeout=60)
        except nidaqmx.errors.DaqError as err:
            print(err)
            if task_output:
                task_output.close()
            if task_input:
                task_input.close()
            sys.exit(1)
    
    
    
    
    
        # Configure input task   
        for channel in input_channels:
            task_input.ai_channels.add_ai_voltage_chan(channel)
        
        task_input.ai_channels.all.ai_max = 10.0 # max voltage
        task_input.ai_channels.all.ai_min = -10.0 # min voltage
        task_input.timing.cfg_samp_clk_timing(sampling_rate,
                                              active_edge=nidaqmx.constants.Edge.RISING,
                                              sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        
        reader = TAMR(task_input.in_stream)
        buffer = np.memmap(
            f"./buffer.tmp",
            dtype=np.float64,
            mode="w+",
            shape=(num_samples, len(input_channels))
            )
        buffer[:] = -1000 # impossible output
        i = 0
        
        dt = 1.0 / sampling_rate
        j = 0
        times_full = []
        data_full = []
        
        
        
        ##### START
        task_output.triggers.start_trigger.cfg_dig_edge_start_trig(task_input.triggers.start_trigger.term)
        task_output.start()
        task_input.start()
        
        
        
        while not task_input.is_task_done() and i < num_samples:
            n = reader._in_stream.avail_samp_per_chan
            if n == 0: continue
            n = min(n, num_samples-i) # prevent reading too many samples
            ##### READ
            
            
            i += reader.read_many_sample(
                buffer[i:i+n, :], # read directly into array using a view
                number_of_samples_per_channel=n
            )
            data = buffer[i-n:i, :].astype(np.float32)
            times = [dt * k for k in range(j, i)]

            
            for channel in input_channel_dict:
                data_channel = data[:,input_channel_dict[channel].index]
                input_channel_dict[channel].pipe[1].send([times, data_channel])
            
            for channel in output_channel_dict:
                data_channel = data[:,output_channel_dict[channel].index]
                output_channel_dict[channel].pipe[1].send([times, data_channel])
            
        
            times_full.extend(times)
            data_full.extend(data)
            j = i
            
            
            # Check if the main thread is still running
            # This ensures that the DAQ board will quit with the main thread
            # Otherwise it may still be in use when the program is restarted
            # This hasn't been formally checked to see if it works
            is_alive = any([th for th in threading.enumerate() if th.ident == main_thread_id])
            if not is_alive:
                sys.exit(1) #   close
        
       
        
        # Stop and check results
        task_output.stop()
        buffer.flush()
        assert np.all(buffer > -1000)
        
        # Send 'False' signal to stop the GUI
        for channel in input_channel_dict:
            input_channel_dict[channel].pipe[1].send(False)
            
        for channel in output_channel_dict:
            output_channel_dict[channel].pipe[1].send(False)
        
        #input(str(times_full))
        #input(str(data_full))
        print("daq finished")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    





if __name__ == '__main__':
    
    input_channels = ["Dev1/ai0", "Dev1/ai19"]
    #aq_single(sampling_rate=1, num_samples=10, input_channels=input_channels)
    daq_continuous_simple(sampling_rate=10, num_samples=5, input_channels=input_channels)
    #aq_continuous_adv(sampling_rate=10, num_samples=100, input_channels=input_channels)