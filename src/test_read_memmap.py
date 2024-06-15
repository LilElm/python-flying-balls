# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 19:11:59 2024

@author: ultservi
"""

import numpy as np



filename = './buffer.tmp'

with np.memmap(filename, dtype='float32', mode='r+', shape=(num_samples, len(input_channels))) as f:
    print(str(f[0]))