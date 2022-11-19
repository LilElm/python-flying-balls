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
import time

def eval_force(time_idle=1.0, time_acc=0.05, time_ramp=0.2, sampling_rate=100000):
    logfolder = "../log/"
    outfolder = "../out/"
    tmpfolder = "../tmp/"
    if os.path.exists(tmpfolder) and os.path.isdir(tmpfolder):
        shutil.rmtree(tmpfolder)
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    os.makedirs(tmpfolder, exist_ok=True)
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
        
    
    time1 = time.time()
    # Times start at 0, but will be corrected later to reflect the true times
    times_idle = np.arange(0.0, time_idle+dt, dt)
    times_acc = np.arange(0.0, time_acc+dt, dt)
    times_ramp = np.arange(0.0, time_ramp+dt, dt)
    times_dec = times_acc
    times_rest = times_idle
    
    time2 = time.time()
    
    len_times_idle = len(times_idle)
    len_times_acc = len(times_acc)
    len_times_ramp = len(times_ramp)
    
    time3 = time.time()
    # x is the evaluated position of equilibrium, x = F / (mw^2)    
    xs_idle = np.zeros(len_times_idle)
    xs_acc = np.zeros(len_times_acc)
    xs_ramp = np.zeros(len_times_ramp)
    xs_dec = xs_acc
    xs_rest = xs_idle
    time4 = time.time()
      
    for i in range(len_times_acc):
        val = velocity * time_acc * (1.0 - times_acc[i] / (time_acc * 2.0)) * (times_acc[i] / time_acc)**3.0
        xs_acc[i] = val
    
    time5 = time.time()
    for i in range(len_times_ramp):
        xs_ramp[i] = velocity * times_ramp[i]
    
        time6 = time.time()
    xs_dec = xs_acc[::-1]
    xs_dec = xs_dec * -1.0


    time7 = time.time()    
    # Find the offsets and remove discontinuities
    xs_idle, xs_acc = ArrayLink(xs_idle, xs_acc)
    xs_acc, xs_ramp = ArrayLink(xs_acc, xs_ramp)
    xs_ramp, xs_dec = ArrayLink(xs_ramp, xs_dec)
    xs_dec, xs_rest = ArrayLink(xs_dec, xs_rest)
    xs_tot = np.concatenate((xs_idle, xs_acc, xs_ramp, xs_dec, xs_rest), axis=None)
     
    time8 = time.time()
    
    times_idle, times_acc = ArrayLink(times_idle, times_acc)
    times_acc, times_ramp = ArrayLink(times_acc, times_ramp)
    times_ramp, times_dec = ArrayLink(times_ramp, times_dec)
    times_dec, times_rest = ArrayLink(times_dec, times_rest)
    times_tot = np.concatenate((times_idle, times_acc, times_ramp, times_dec, times_rest), axis=None)
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
 
    time9 = time.time()
    # Find the derivatives    
    dx = derivative(xs_tot, dt)
    ddx = derivative(dx, dt)
    
    time10 = time.time()
    
    dd = [2.0 * np.pi * df * x for x in dx]
    pp = [(2.0 * np.pi * f0)**2.0 * x for x in xs_tot]
    alpha = (2.0 * np.pi * f0)**2.0 * k
 
    time11 = time.time()   
 
    output = []    
    for i in range(len(ddx)):
        output.append((ddx[i] + dd[i] + pp[i]) / alpha)
    np.set_printoptions(threshold=sys.maxsize)
    profile = np.array(output, dtype=np.float64)
    
    time12 = time.time()
#    print("time11"+str(time11))
 #   print("time12"+str(time12))
    
    # Print to file
    with open((tmpfolder + "position"), "w") as f:
        for i in range(len(xs_tot)):
            f.write(str(times_tot[i]) + ", " + str(xs_tot[i]) + "\n")

    with open((tmpfolder + "force_profile"), "w") as f:
        for i in range(len(profile)):
            f.write(str(times_tot[i]) + ", " + str(profile[i]) + "\n")

    time13 = time.time()
    
    time12 = time2 - time1
    time23 = time3 - time2
    time34 = time4 - time3
    time45 = time5 - time4
    time56 = time6 - time5
    time67 = time7 - time6
    time78 = time8 - time7
    time89 = time9 - time8
    time910 = time10 - time9
    time1011 = time11 - time10
    time1112 = time12 - time11
    time1213 = time13 - time12
    """
    print("time12 = " + str(time12))
    print("time23 = " + str(time23))
    print("time34 = " + str(time34))
    print("time45 = " + str(time45))
    print("time56 = " + str(time56))
    print("time67 = " + str(time67))
    print("time78 = " + str(time78))
    print("time89 = " + str(time89))
    print("time910 = " + str(time910))
    print("time1011 = " + str(time1011))
    print("time1112 = " + str(time1112))
    print("time1213 = " + str(time1213))
    
    input()
    
    """
    
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


  