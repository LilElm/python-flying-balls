# -*- coding: utf-8 -*-
"""
Flopper ramp current - Python translation for flying balls
"""
import numpy as np
import sys
from decimal import Decimal
import matplotlib.pyplot as plt
import datetime
import logging
import os
import shutil

def eval_force(time_idle=1.0, time_acc=0.05, time_ramp=0.2, sampling_rate=1000):
    logfolder = "../log/"
    outfolder = "../out/"
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "force_profile.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    dt = 1.0 / sampling_rate
    velocity = 1.0 #mm/s?
    df = 0.019 # FWHM I think
    f0 = 4.0#8.026 # Resonant frequency I think
    k = 0.825 # Spring constant I think
    
    # Modulo, whether via % of math.fmod() is completely broken
    # Decimal(str()) % Decimal(str()) offers a solution, even if clunky
    # Nota bene, this does not work with math.fmod(); only %
    if Decimal(str(time_idle)) % Decimal(str(dt)) != 0:
        print("time_idle is not a multiple of dt")
        input()
        exit()
        
    if Decimal(str(time_acc)) % Decimal(str(dt)) != 0:
        print("time_acc is not a multiple of dt")
        exit()
        
    if Decimal(str(time_ramp)) % Decimal(str(dt)) != 0:
        print("time_ramp is not a multiple of dt")
        exit()
        
    
    
    # Times start at 0, but will be corrected later to reflect the true times
    times_idle = np.arange(0.0, time_idle+dt, dt)
    times_acc = np.arange(0.0, time_acc+dt, dt)
    times_ramp = np.arange(0.0, time_ramp+dt, dt)
    times_dec = times_acc
    times_rest = times_idle
    
    len_times_idle = len(times_idle)
    len_times_acc = len(times_acc)
    len_times_ramp = len(times_ramp)
    
    
    # x is the evaluated position of equilibrium, x = F / (mw^2)    
    xs_idle = np.zeros(len_times_idle)
    xs_acc = np.zeros(len_times_acc)
    xs_ramp = np.zeros(len_times_ramp)
    xs_dec = xs_acc
    xs_rest = xs_idle
    
      
    for i in range(len_times_acc):
        val = velocity * time_acc * (1.0 - times_acc[i] / (time_acc * 2.0)) * (times_acc[i] / time_acc)**3.0
        xs_acc[i] = val
        
    for i in range(len_times_ramp):
        xs_ramp[i] = velocity * times_ramp[i]
        
    xs_dec = xs_acc[::-1]
    xs_dec = xs_dec * -1.0


    
    # Find the offsets and remove discontinuities
    xs_idle, xs_acc = ArrayLink(xs_idle, xs_acc)
    xs_acc, xs_ramp = ArrayLink(xs_acc, xs_ramp)
    xs_ramp, xs_dec = ArrayLink(xs_ramp, xs_dec)
    xs_dec, xs_rest = ArrayLink(xs_dec, xs_rest)
    xs_tot = np.concatenate((xs_idle, xs_acc, xs_ramp, xs_dec, xs_rest), axis=None)
     
    
    times_idle, times_acc = ArrayLink(times_idle, times_acc)
    times_acc, times_ramp = ArrayLink(times_acc, times_ramp)
    times_ramp, times_dec = ArrayLink(times_ramp, times_dec)
    times_dec, times_rest = ArrayLink(times_dec, times_rest)
    times_tot = np.concatenate((times_idle, times_acc, times_ramp, times_dec, times_rest), axis=None)
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
 
    
    # Find the derivatives    
    dx = derivative(xs_tot, dt)
    ddx = derivative(dx, dt)
    
    dd = [2.0 * np.pi * df * x for x in dx]
    pp = [(2.0 * np.pi * f0)**2.0 * x for x in xs_tot]
    alpha = (2.0 * np.pi * f0)**2.0 * k
 
    output = []    
    for i in range(len(ddx)):
        output.append((ddx[i] + dd[i] + pp[i]) / alpha)
    np.set_printoptions(threshold=sys.maxsize)
    profile = np.array(output, dtype=np.float64)
    
    
    # Print to file
    with open(("../position"), "w") as f:
        for i in range(len(xs_tot)):
            f.write(str(times_tot[i]) + ", " + str(xs_tot[i]) + "\n")

    with open(("../force_profile"), "w") as f:
        for i in range(len(profile)):
            f.write(str(times_tot[i]) + ", " + str(profile[i]) + "\n")

    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(times_tot, profile)
    ax.plot(times_tot, xs_tot)
    #plt.show()
    path = outfolder + "force_profile.png"
    fig.savefig(path, bbox_inches="tight", dpi=900)
    #input()

    #np.ravel(times_tot)
    #np.ravel(profile)

    return times_tot, profile, xs_tot



def ArrayLink(array1, array2):
    # Drop final entry in array1
    # array2 = array2 - array2[first] + array1[final]
    
    array1_val = array1[-1]
    array1_new = array1[:-1]
    array2_val = array2[0]
    array2 = array2 - array2_val + array1_val
    return array1_new, array2
    





def derivative(xs, h):
    # Evaluate the derivative at a constant step value, h
    dx = []
    fin = len(xs) - 1
    
    for i in range(len(xs)):
        if i == 0:
            val = (xs[i+1] - xs[i]) / h
        elif i==fin:
            val = (xs[i] - xs[i-1]) / h
        else:
            val = (xs[i+1] - xs[i-1]) / (2.0 * h)
        dx.append(val)
    return dx
    


# Run
if __name__ == "__main__":
    eval_force()


  