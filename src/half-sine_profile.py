# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:37:01 2023

@author: ultservi
"""
import numpy as np
import sys
from decimal import Decimal
import matplotlib.pyplot as plt
import datetime
import logging
import os
import shutil

def eval_halfsine(amp=1.0, freq=2.0, time_idle=1.0, time_rest=1.0, sampling_rate=100000.0):
    
    logfolder = "../log/"
    outfolder = "../out/"
    tmpfolder = "../tmp/"
    """
    if os.path.exists(tmpfolder) and os.path.isdir(tmpfolder):
        try:
            shutil.rmtree(tmpfolder)
            logging.info("Removed temporary folder " + str(tmpfolder))
        except:
            logging.warning("Failed to remove temporary folder " + str(tmpfolder))
            logging.warning("Trying again")
            try:
                time.sleep(0.5)
                shutil.rmtree(tmpfolder)
                logging.info("Removed folder " + str(tmpfolder))
            except:
                logging.warning("Failed to remove temporary folder " + str(tmpfolder))
                print("Unable to remove tmpfolder")
    """
            
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    os.makedirs(tmpfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "half-sine_profile.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    
    dt = 1.0 / sampling_rate
    time_half = 0.5 / freq
    
    
    # Modulo, whether via % of math.fmod() is completely broken
    # Decimal(str()) % Decimal(str()) offers a solution, even if clunky
    # Nota bene, this does not work with math.fmod(); only %
    if Decimal(str(time_idle)) % Decimal(str(dt)) != 0:
        print("time_idle is not a multiple of dt")
        input()
        exit()
        
    if Decimal(str(time_half)) % Decimal(str(dt)) != 0:
        print("time_ramp is not a multiple of dt")
        exit()
        
    if Decimal(str(time_rest)) % Decimal(str(dt)) != 0:
        print("time_rest is not a multiple of dt")
        exit()
    
    
    times_idle = np.arange(0.0, time_idle+dt, dt)
    times_half = np.arange(0.0, time_half+dt, dt)
    times_rest = np.arange(0.0, time_rest, dt)
    

    
    
    omega = 2.0 * np.pi * freq
    x_idle = [0 for time in times_idle]
    x_half = [amp * np.sin(omega * time) for time in times_half]
    x_rest = [0 for time in times_rest]
    profile = x_idle + x_half + x_rest
    
    times_idle, times_half = ArrayLink(times_idle, times_half)
    times_half, times_rest = ArrayLink(times_half, times_rest)
    
    len_times_idle = len(times_idle)
    len_times_half = len(times_half)
    len_times_rest = len(times_rest)
    
    times_tot = np.concatenate((times_idle, times_half, times_rest), axis=None)
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
    
    
    
    
    # Print to file
    with open((tmpfolder + "half-sine_profile.csv"), "w") as f:
        f.write("Seconds, Profile\n")
        for i in range(len_times_idle):
            f.write(f"{times_idle[i]}, {x_idle[i]}\n")
            
        for i in range(len_times_half):
            f.write(f"{times_half[i]}, {x_half[i]}\n")
            
        for i in range(len_times_rest):
            f.write(f"{times_rest[i]}, {x_rest[i]}\n")
        
    
    return times_tot, profile

    
    
def ArrayLink(array1, array2):
    # Drop final entry in array1
    # array2 = array2 - array2[first] + array1[final]
    
    array1_val = array1[-1]
    array1_new = array1[:-1]
    array2_val = array2[0]
    array2 = array2 - array2_val + array1_val
    return array1_new, array2
    

    
    
if __name__ == "__main__":
    main()