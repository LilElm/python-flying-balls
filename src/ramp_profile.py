# -*- coding: utf-8 -*-

# Import libraries
import numpy as np
import sys
from decimal import Decimal
import matplotlib.pyplot as plt
import datetime
import logging
import os
import time

"""
Flopper ramp current - Python translation for flying balls
"""

def eval_ramp(drive_target=10, drive_current=5, time_idle=4.0, time_acc=1.0, time_ramp=4.0, time_rest=1.25, sampling_rate=10000.0, coil=None, velocity=0.1):
    # I think velocity is in mm/s, but all times are in seconds.
    # The program is now normalised and scaled with respect to drive, rendering the velocity parameter redundant
    
    logfolder = "../log/"
    outfolder = "../out/"
    tmpfolder = "../tmp/"
    
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    os.makedirs(tmpfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "ramp_profile.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    dt = 1.0 / sampling_rate
    #velocity = 1.0 #mm/s
    df = 0.019 # FWHM I think
    f0 = 8.026#4.0#8.026 # Resonant frequency I think
    k = 0.825 # Spring constant I think
    
    """
    # Modulo, whether via % of math.fmod() is completely broken
    # Decimal(str()) % Decimal(str()) offers a solution, even if clunky
    # Nota bene, this does not work with math.fmod(); only %
    if Decimal(str(time_idle)) % Decimal(str(dt)) != 0:
        input("time_idle is not a multiple of dt")
        exit()
        
    if Decimal(str(time_acc)) % Decimal(str(dt)) != 0:
        input("time_acc is not a multiple of dt")
        exit()
        
    if Decimal(str(time_ramp)) % Decimal(str(dt)) != 0:
        input("time_ramp is not a multiple of dt")
        exit()
        
    if Decimal(str(time_rest)) % Decimal(str(dt)) != 0:
        input("time_rest is not a multiple of dt")
        exit()
    
    """
    
    # Times start at 0, but will be corrected later to reflect the true times
    times_idle = np.arange(0.0, time_idle, dt)
    times_acc = np.arange(0.0, time_acc, dt)
    times_ramp = np.arange(0.0, time_ramp, dt)
    times_dec = times_acc
    times_rest = np.arange(0.0, time_rest, dt)
        
    len_times_idle = len(times_idle)
    len_times_acc = len(times_acc)
    len_times_ramp = len(times_ramp)
    len_times_rest = len(times_rest)
    
    
    
    # x is the evaluated position of equilibrium, x = F / (mw^2)    
    xs_idle = np.zeros(len_times_idle)
    xs_acc = np.zeros(len_times_acc)
    xs_ramp = np.zeros(len_times_ramp)
    xs_rest = np.zeros(len_times_rest)
    
    for i in range(len_times_acc):
        val = velocity * time_acc * (1.0 - times_acc[i] / (time_acc * 2.0)) * (times_acc[i] / time_acc)**3.0
        xs_acc[i] = val
    
    for i in range(len_times_ramp):
        xs_ramp[i] = velocity * times_ramp[i]
        
    xs_dec = xs_acc[::-1] * -1.0
    
    
    
    # Find the offsets and remove discontinuities
    times_acc = times_acc + time_idle
    times_ramp = times_ramp + time_idle + time_acc
    times_dec = times_dec + time_idle + time_acc + time_ramp
    times_rest = times_rest + time_idle + time_acc + time_ramp + time_acc
    times_tot = np.concatenate((times_idle, times_acc, times_ramp, times_dec, times_rest), axis=None)
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
    
    xs_acc = xs_acc + xs_idle[-1]
    xs_ramp = xs_ramp + xs_acc[-1]
    xs_dec = xs_dec + xs_ramp[-1] + xs_acc[-1]
    xs_rest = xs_rest + xs_dec[-1]
    xs_tot = np.concatenate((xs_idle, xs_acc, xs_ramp, xs_dec, xs_rest), axis=None)
    

    
    # Find the derivatives
    dx_idle = np.zeros(len_times_idle)
    dx_acc = np.gradient(xs_acc, dt)
    dx_ramp = np.gradient(xs_ramp, dt)
    dx_dec = dx_acc[::-1] * -1.0
    dx_rest = np.zeros(len_times_rest)
    dx = np.concatenate((dx_idle, dx_acc, dx_ramp, dx_dec, dx_rest), axis=None)
    
    # Find the double derviatives
    ddx_idle = dx_idle
    ddx_acc = np.gradient(dx_acc, dt)
    ddx_ramp = np.gradient(dx_ramp, dt)
    ddx_dec = ddx_acc[::-1] * -1.0
    ddx_rest = dx_rest
    ddx = np.concatenate((ddx_idle, ddx_acc, ddx_ramp, ddx_dec, ddx_rest), axis=None)
    
    
    # Evaluate acceleration, drag and position parameters
    twopi = 2.0 * np.pi
    twopidf = twopi * df
    twopif0 = twopi * f0
    
    dd = [twopidf * x for x in dx]
    pp = [(twopif0)**2.0 * x for x in xs_tot]
    alpha = (twopif0)**2.0 * k
    
    
    output = []
    for i in range(len(ddx)):
        output.append((ddx[i] + dd[i] + pp[i]) / alpha)
    profile = np.array(output, dtype=np.float64)
    
    
    # Normalise profile and scale to target drive
    val = profile[-1]
    profile = profile / val
    profile = profile * (drive_target - drive_current) + drive_current
    
    
    
    # Print to file
    if coil is None:
        path = f"{tmpfolder}ramp_profile"
    else:
        path = f"{tmpfolder}{coil}_ramp_profile"
    
    with open((path + ".csv"), "w") as f:
        f.write("Seconds, Profile\n")
        for i in range(len(times_tot)):
            f.write(f"{times_tot[i]}, {profile[i]}\n")
    
    path = path + ".png"
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(times_tot, profile)
    #plt.show()
    fig.savefig(path, bbox_inches="tight", dpi=600)
    plt.close()
    
    
    
    
    #np.ravel(times_tot)
    #np.ravel(profile)
    
    
    return profile



# Run
if __name__ == "__main__":
    eval_ramp()
