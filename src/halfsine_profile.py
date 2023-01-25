# -*- coding: utf-8 -*-

# Import libraries
import numpy as np
import sys
from decimal import Decimal
import matplotlib.pyplot as plt
import datetime
import logging
import os


def eval_halfsine(amp=1.0, freq=2.0, time_idle=1.0, time_rest=4.0, sampling_rate=10000.0, coil=None):
    
    logfolder = "../log/"
    outfolder = "../out/"
    tmpfolder = "../tmp/"
            
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
        input()
        exit()
        
    if Decimal(str(time_rest)) % Decimal(str(dt)) != 0:
        print("time_rest is not a multiple of dt")
        input()
        exit()
    
    
    times_idle = np.arange(0.0, time_idle, dt)
    times_half = np.arange(0.0, time_half, dt)
    times_rest = np.arange(0.0, time_rest, dt)
    
    
    omega = 2.0 * np.pi * freq
    x_idle = [0 for time in times_idle]
    x_half = [amp * np.sin(omega * time) for time in times_half]
    x_rest = [0 for time in times_rest]
    profile = x_idle + x_half + x_rest
    
    
    times_half = times_half + time_idle
    times_rest = times_rest + time_idle + time_half
    
        
    times_tot = np.concatenate((times_idle, times_half, times_rest), axis=None)
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
    
    
    # Print to file
    with open((tmpfolder + "halfsine_profile.csv"), "w") as f:
        f.write("Seconds, Profile\n")
        for i in range(len(times_tot)):
            f.write(f"{times_tot[i]}, {profile[i]}\n")
    
    

    if coil is None:
        path = f"{tmpfolder}halfsine_profile.png"
    else:
        path = f"{tmpfolder}{coil}_halfsine_profile.png"
        
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(times_tot, profile)
    #plt.show()
    fig.savefig(path, bbox_inches="tight", dpi=600)
    
    return profile


    
    
if __name__ == "__main__":
    eval_halfsine()