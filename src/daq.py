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
            
        

def daq_continuous_adv(sampling_rate=1, num_samples=4, input_channel_dict=None):
    
    input_channels = []
    for channel in input_channel_dict:
        input_channels.append(input_channel_dict[channel].channel)
    
    
    
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
        
        
        

    # Configure input task
    with nidaqmx.Task() as task:
        
    
        
        for channel in input_channels:
            task.ai_channels.add_ai_voltage_chan(channel)
        
        task.ai_channels.all.ai_max = 10.0 # max voltage
        task.ai_channels.all.ai_min = -10.0 # min voltage
        task.timing.cfg_samp_clk_timing(sampling_rate,
                                        active_edge=nidaqmx.constants.Edge.RISING,
                                        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        
        reader = TAMR(task.in_stream)
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
        task.start()
        
        
        
        while not task.is_task_done() and i < num_samples:
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
            
            #print("=================================")
            #print(str(data))
            #print(str(times))
            print("=================================")
            
            """
            #for line in data:
            for m in range(len(data)):
                for channel in input_channel_dict:
                    data_time = times[m]
                    data_data = data[m][input_channel_dict[channel].index]
              #      print(f"time = {data_time}")
               #     print(f"data = {data_data}")
                    
                    input_channel_dict[channel].pipe[1].send([data_time, data_data])
            """
            
            
            #print(str(type(data)))
            #print(str(len(data)))
            if True:
            #for m in range(len(data)):
                for channel in input_channel_dict:
                    data_time = times[:]
                    data_data = data[:,input_channel_dict[channel].index]
                    
                    #print(str(data_data))
                    
              #      print(f"time = {data_time}")
               #     print(f"data = {data_data}")
                    
                    input_channel_dict[channel].pipe[1].send([data_time, data_data])
            
            
          #  for channel in input_channel_dict:
           #     input_channel_dict[channel].index
                
                
            #    print(str([times, data[input_channel_dict[channel].index]]))
             #   input_channel_dict[channel].pipe[1].send([times, data[input_channel_dict[channel].index]])
            
            times_full.extend(times)
            data_full.extend(data)
            j = i
            
            #print(f"{times}, {data}")
            
       
        
        # Stop and check results
        buffer.flush()
        assert np.all(buffer > -1000)
        
        #input(str(times_full))
        input(str(data_full))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    





if __name__ == '__main__':
    
    input_channels = ["Dev1/ai0", "Dev1/ai19"]
    #aq_single(sampling_rate=1, num_samples=10, input_channels=input_channels)
    daq_continuous_simple(sampling_rate=10, num_samples=5, input_channels=input_channels)
    #aq_continuous_adv(sampling_rate=10, num_samples=100, input_channels=input_channels)