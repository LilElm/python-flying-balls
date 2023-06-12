# -*- coding: utf-8 -*-

# Import libraries
import numpy as np
import sys
from decimal import Decimal
import matplotlib.pyplot as plt
import datetime
import logging
import os


def main(double=True, doubledelay=0.075):
    
    time_idle = 1.0
    time_idle2 = time_idle + doubledelay
    
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    
    if double:
        times_tot1, profile1 = eval_halfsinepulses(time_idle=time_idle, double=False, negative=True)#, ax=ax)
        times_tot2, profile2 = eval_halfsinepulses(time_idle=time_idle2, double=True, negative=True)#, ax=ax)
        
   #     ax.plot(times_tot1, profile1)
   #     ax.plot(times_tot2, profile2)
        
    else:
        times_tot1, profile1 = eval_halfsinepulses(time_idle=time_idle)
   #     ax.plot(times_tot1, profile1)
        
   # plt.show()    
    
    path = "../out/halfsinepulses_profile.png"
    fig.savefig(path, bbox_inches="tight", dpi=600)
   # plt.show()
   # input()
    plt.close()
    
    
    

def eval_halfsinepulses(amp=0.4,
                        amp2=0.4,
                        freq=4.0,
                        freq2=20.0,
                        delay=0.0,
                        ballfreq=3.5,
                        #time_idle=1.175,
                        time_idle=1.1,
                        orbits=25,
                        time_rest=10.0,
                        sampling_rate=5000.0, # DonIf lowered beneath 100, lengths won't match
                        coil=None,
                        outfolder="../out/",
                        timestamp=None,
                        negative=False,
                        double=False):
 
    logfolder = "../log/"
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "halfsinepulses_profile.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    
    
    dt = 1.0 / sampling_rate
    time_half = 0.5 / freq
    time_boost = 0.5 / freq2
    time_orbit = 1.0 / ballfreq
    
    if negative:
        time_orbit = time_orbit / 2.0
        orbits = orbits * 2
    
    
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    time_idle = np.round(time_idle, dec)
    delay = np.round(delay, dec)
    time_half = np.round(time_half, dec)
    time_boost = np.round(time_boost, dec)
    time_orbit = np.round(time_orbit, dec)
    
    logging.info(f"time_idle = {time_idle}")
    logging.info(f"delay = {delay}")
    logging.info(f"time_half = {time_half}")
    logging.info(f"time_boost = {time_boost}")
    logging.info(f"time_orbit = {time_orbit}")
    logging.info(f"dt = {dt}")
    

    times_idle = np.arange(0.0, time_idle, dt)
    times_half = np.arange(0.0, time_half, dt)
    time_orbit_first = time_orbit + delay - 0.5 * (time_half + time_boost)
    times_orbit_first = np.arange(0.0, time_orbit_first, dt)
    times_orbit = np.arange(0.0, (time_orbit - time_boost), dt)
    times_boost = np.arange(0.0, time_boost, dt)
    times_rest = np.arange(0.0, time_rest, dt)
    
    
    
    
    omega = 2.0 * np.pi * freq
    omega2 = 2.0 * np.pi * freq2
    x_idle = [0 for time in times_idle]
    x_half = [amp * np.sin(omega * time) for time in times_half]
    x_orbit_first = [0 for time in times_orbit_first]
    x_boost = [amp2 * np.sin(omega2 * time) for time in times_boost]
    x_orbit = [0 for time in times_orbit]
    x_rest = [0 for time in times_rest]
    
    
    
    x_loop = []
    x_boost_nve = [-x for x in x_boost]
    for i in range(orbits-1):
        if negative and i%2==0:
                x_loop = x_loop + x_boost_nve + x_orbit
        else:
            x_loop = x_loop + x_boost + x_orbit
            
            
            
    time_loop = time_orbit * (orbits-1)
    times_loop = np.arange(0.0, time_loop, dt)
    

    profile = x_idle + x_half + x_orbit_first + x_loop + x_rest
    profile = np.array(profile, dtype=np.float64)
    
    
    times_half = times_half + time_idle
    times_orbit_first = times_orbit_first + time_idle + time_half
    times_loop = times_loop + time_idle + time_half + time_orbit_first
    times_rest = times_rest + time_idle + time_half + time_orbit_first + time_loop
    times_tot = np.concatenate((times_idle, times_half, times_orbit_first, times_loop, times_rest), axis=None)
    
    
    
    
    
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
    
    
       
    if double:
        num = 2
    else:
        num = 1
    
    # Print to file
    if coil is None:
        if timestamp is None:
            path = f"{outfolder}halfsinepulses_profile{num}"
        else:
            path = f"{outfolder}halfsinepulses_profile{num}_{timestamp}" 
    else:
        if timestamp is None:
            path = f"{outfolder}{coil}_halfsinepulses_profile{num}"
        else:
            path = f"{outfolder}{coil}_halfsinepulses_profile{num}_{timestamp}"
            
    
    
    with open((path + ".csv"), "w") as f:
        for i in range(len(profile)):
            f.write(f"{profile[i]}\n")
    
    
    return times_tot, profile


    
    
if __name__ == "__main__":
    main()