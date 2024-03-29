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

def eval_ramp(f0=7.300, df=0.090, k=0.465, drive_target=1, drive_current=0, time_idle=1.0, time_acc=1.0, time_ramp=5.0, time_rest=1.0, sampling_rate=100.0, coil=None, outfolder="../out/", timestamp=None):
    # I think velocity is in mm/s, but all times are in seconds.
    # The program is now normalised and scaled with respect to drive, rendering the velocity parameter redundant
    
    logfolder = "../log/"
    #tmpfolder = "../tmp/"
    
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    #os.makedirs(tmpfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "ramp_profile.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    dt = 1.0 / sampling_rate
    velocity = 1.0 #mm/s
    #df = 0.019 # FWHM I think
    #f0 = 8.026#4.0#8.026 # Resonant frequency I think
    #k = 0.825 # Spring constant I think
    
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
    times_idle = np.arange(0.0, time_idle+dt, dt)
    times_acc = np.arange(dt, time_acc+dt, dt)
    times_ramp = np.arange(dt, time_ramp+2.0*dt, dt)
    #times_ramp = np.arange(dt, time_ramp+dt, dt)
    #times_dec = times_acc
    times_dec = np.arange(2.0*dt, time_acc, dt)
    times_rest = np.arange(0.0, time_rest, dt)
        
    len_times_idle = len(times_idle)
    len_times_acc = len(times_acc)
    len_times_ramp = len(times_ramp)
    len_times_rest = len(times_rest)
    
    len_times_dec = len(times_dec)
    
    
    # x is the evaluated position of equilibrium, x = F / (mw^2)    
    xs_idle = np.zeros(len_times_idle)
    xs_acc = np.zeros(len_times_acc)
    xs_ramp = np.zeros(len_times_ramp)
    xs_rest = np.zeros(len_times_rest)
    
    xs_dec = np.zeros(len_times_dec)
    
    for i in range(len_times_acc):
        val = velocity * time_acc * (1.0 - times_acc[i] / (time_acc * 2.0)) * (times_acc[i] / time_acc)**3.0
        xs_acc[i] = val
    
    for i in range(len_times_ramp):
        xs_ramp[i] = velocity * times_ramp[i]
        
    #xs_dec = xs_acc[::-1] * -1.0
    
    for i in range(len_times_dec):
        val = velocity * time_acc * (1.0 - times_dec[i] / (time_acc * 2.0)) * (times_dec[i] / time_acc)**3.0
        xs_dec[-(1+i)] = -1.0 * val
    
    
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
    #dx_dec = dx_acc[::-1] * -1.0
    
    dx_dec = np.gradient(xs_dec, dt)
    
    dx_rest = np.zeros(len_times_rest)
    dx = np.concatenate((dx_idle, dx_acc, dx_ramp, dx_dec, dx_rest), axis=None)
    
    # Find the double derviatives
    ddx_idle = dx_idle
    ddx_acc = np.gradient(dx_acc, dt)
    ddx_ramp = np.gradient(dx_ramp, dt)
    #ddx_dec = ddx_acc[::-1] * -1.0
    
    
    ddx_dec = np.gradient(dx_dec, dt)
    
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
        if timestamp is None:
            path = f"{outfolder}ramp_profile"
        else:
            path = f"{outfolder}ramp_profile_{timestamp}" 
    else:
        if timestamp is None:
            path = f"{outfolder}{coil}_ramp_profile"
        else:
            path = f"{outfolder}{coil}_ramp_profile_{timestamp}"
            
    
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
