# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 18:58:43 2023

@author: ultservi
"""

import numpy as np


mylist = [1,2,3,4,5,6,7,8,9]
array = np.array(mylist)
num_samples = len(array)

buffer0 = np.reshape(array, (1, num_samples))

print(str(array))
input(str(buffer0))






#buffer1 = np.concatenate((array, array),axis=0)
buffer1 = np.vstack((array, array))
input(str(buffer1))