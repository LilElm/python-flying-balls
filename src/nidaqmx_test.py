import numpy as np
import nidaqmx as ni
from nidaqmx import DaqError
from nidaqmx.error_codes import DAQmxErrors
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx._task_modules.read_functions import _read_analog_f_64
from nidaqmx.constants import READ_ALL_AVAILABLE, FillMode, AcquisitionType
from time import sleep
import time

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


##### SETUP
n_tot = 100000
sample_rate = 200000
#sample_rate = 1000

with ni.Task("signals") as task:
    task.ai_channels.add_ai_voltage_chan(
        "Dev1/ai0", 
        min_val=-10, max_val=10,
    ) 
    n_channels = task.number_of_channels
    task.timing.cfg_samp_clk_timing(
        rate=sample_rate,
        sample_mode=AcquisitionType.CONTINUOUS#,
#        samps_per_chan=n_tot,
    )
    reader = TAMR(task.in_stream)
    read_buffer = np.memmap(
        "test.tmp",
        dtype=np.float,
        mode="w+",
        shape=(n_tot, n_channels))
    read_buffer[:] = -1000 # impossible output
    i = 0
    ##### START
    task.start()
    while not task.is_task_done() :#and i < n_tot:
        
        sleep(0.01) # pretend to be busy with other tasks
        n = reader._in_stream.avail_samp_per_chan
        if n == 0: continue
        n = min(n, n_tot-i) # prevent reading too many samples
        ##### READ
        time_1 = time.time()
        i += reader.read_many_sample(
            read_buffer[i:i+n, :], # read directly into array using a view
            number_of_samples_per_channel=n
        )
        time2 = time.time()
        
        print(str(n))
        #print(str(read_buffer))
    ##### STOP AND CHECK RESULTS
    task.stop()
    print(str(read_buffer))
    read_buffer.flush()
    assert np.all(read_buffer > -1000)
print("Complete")
input()