# -*- coding: utf-8 -*-

# Import libraries
import numpy as np
import sys
from decimal import Decimal
import matplotlib.pyplot as plt
import datetime
import logging
import os








def generate_circular_motion_profile(amp_primary_coil1=0.6,            #0.7 = big ball, superfluid
                                     amp_secondary_coil1=0.3,           #0.3 = big ball, superfluid  
                                     freq_primary_coil1=0.5,
                                     freq_secondary_coil1=1.0,
                                     
                                     #coil1_start_delay=10.25,
                                     coil2_start_delay=10.25,
                                     coil2_second_delay=5.4, # This will be worked out automatically from coil1_second_delay and ball_freq
                                     #coil2_second_delay=0.0,
                                     
                                     amp_primary_coil2=0.6,            #0.7 = big ball, superfluid
                                     amp_secondary_coil2=0.3,           #0.3 = big ball, superfluid  
                                     freq_primary_coil2=0.5,
                                     freq_secondary_coil2=1.0,
                                     
                                     time_idle=1.0,
                                     time_rest=10.0,
                                     
                                     ball_freq=0.25,
                                     orbits=10,
                                     sampling_rate=10000.0):
    
    

    
    coil1_start_delay=0
    time_idle_coil1 = time_idle + coil1_start_delay
    time_idle_coil2 = time_idle + coil2_start_delay
    
    
    
    
    
    #coil2_second_delay = 0#coil2_second_delay
    coil1_second_delay = coil2_second_delay + coil2_start_delay - 0.25/ball_freq
    
    
    
    
    profile_1 = generate_halfsine_pulses_profile(amp_primary_coil1,
                                                 amp_secondary_coil1,
                                                 freq_primary_coil1,
                                                 freq_secondary_coil1,
                                                 
                                                 time_idle_coil1,
                                                 time_rest,
                                                 coil1_second_delay,
                                                 
                                                 ball_freq,
                                                 orbits,
                                                 
                                                 sampling_rate,
                                                 negative=True)

    profile_2 = generate_halfsine_pulses_profile(amp_primary_coil2,
                                                 amp_secondary_coil2,
                                                 freq_primary_coil2,
                                                 freq_secondary_coil2,
                                                 
                                                 time_idle_coil2,
                                                 time_rest,
                                                 coil2_second_delay,
                                                 
                                                 ball_freq,
                                                 orbits,
                                                 
                                                 sampling_rate,
                                                 negative=True)


    


    
    """
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(profile_1, label="coil1")
    ax.plot(profile_2, label="coil2")
    ax.legend()
    plt.show()
    input()


    """
    return profile_1, profile_2





def generate_halfsine_pulses_profile(amp_primary=0.6,            #0.7 = big ball, superfluid
                                     amp_secondary=0.3,           #0.3 = big ball, superfluid  
                                     freq_primary=2.0,
                                     freq_secondary=1.8,
                                     
                                     time_idle=1.0,
                                     time_rest=10.0,
                                     time_delay=0.0,
                                     
                                     ball_freq=2,
                                     orbits=20,
                                     
                                     sampling_rate=10000.0,
                                     negative=True):

    orbits = int(orbits)


    # delay_primary is the time between the first and second pulses
    # delay_secondary is the time between every subsequent pulse
    dt = 1.0 / sampling_rate
    time_orbit = 0.5/ball_freq
    time_first_delay = time_orbit - (1.0/(4.0 * freq_primary)) - (1.0/(4.0*freq_secondary)) + time_delay
    time_second_delay = time_orbit - (1.0/(2.0 * freq_secondary))
    
    
    
    times_idle = np.arange(0.0, time_idle, dt)
    times_first_pulse = np.arange(0.0, 0.5/freq_primary, dt)
    times_first_delay = np.arange(0.0, time_first_delay, dt)
    times_second_pulse = np.arange(0.0, 0.5/freq_secondary, dt)
    times_second_delay = np.arange(0.0, time_second_delay, dt)
    times_rest = np.arange(0.0, time_rest, dt)
    
    
    
    
    
    
    
    omega_first = 2.0 * np.pi * freq_primary
    omega_second = 2.0 * np.pi * freq_secondary
    
    
    x_idle = [0 for time in times_idle]
    x_first_pulse = [amp_primary * np.sin(omega_first * time) for time in times_first_pulse]
    x_first_delay = [0 for time in times_first_delay]
    x_second_pulse = [amp_secondary * np.sin(omega_second * time) for time in times_second_pulse]
    x_second_delay = [0 for time in times_second_delay]
    x_rest = [0 for time in times_rest]
    
    
    
    
    if negative:
        x_second_pulse_negative = [-x for x in x_second_pulse]
        profile = x_idle + x_first_pulse + x_first_delay + x_second_pulse_negative
        
        for i in range(orbits-1):
            profile = profile + x_second_delay + x_second_pulse + x_second_delay + x_second_pulse_negative
    
    profile = profile + x_rest
    profile = np.array(profile, dtype=np.float64)
    
    
    
    
    
    
    """
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(profile)
    plt.show()
    """
    
    
    
    
    
    """
    
    
    first_pulse = generate_halfsine_profile(amp=amp_primary,
                                            freq=freq_primary,
                                            time_idle=time_idle,
                                            time_rest=delay_primary/2,
                                            sampling_rate=sampling_rate)


    second_pulse = generate_halfsine_profile(amp=amp_secondary,
                                             freq=freq_secondary,
                                             time_idle=delay_primary/2,
                                             time_rest=delay_secondary/2,
                                             sampling_rate=sampling_rate)

    subsequent_pulse = generate_halfsine_profile(amp=amp_secondary,
                                                 freq=freq_secondary,
                                                 time_idle=delay_secondary/2,
                                                 time_rest=delay_secondary/2,
                                                 sampling_rate=sampling_rate)

    if negative:
        profile = first_pulse + -1*second_pulse + subsequent_pulse + -1*subsequent_pulse

    """



    return profile










def generate_halfsine_profile(amp=1.0, freq=3.0,
                              time_idle=1.0, time_rest=4.0,
                              sampling_rate=100.0, coil=None,
                              outfolder="../out/", timestamp=None,
                              figure=False):
    
    logfolder = "../log/"
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "halfsine_profile.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    
    dt = 1.0 / sampling_rate
    time_half = 0.5 / freq
    
    
    times_idle = np.arange(0.0, time_idle, dt)
    times_half = np.arange(0.0, time_half, dt)
    times_rest = np.arange(0.0, time_rest, dt)
    
    
    omega = 2.0 * np.pi * freq
    x_idle = [0 for time in times_idle]
    x_half = [amp * np.sin(omega * time) for time in times_half]
    x_rest = [0 for time in times_rest]
    profile = x_idle + x_half + x_rest
    profile = np.array(profile, dtype=np.float64)
    
    
    times_half = times_half + time_idle
    times_rest = times_rest + time_idle + time_half
    
        
    times_tot = np.concatenate((times_idle, times_half, times_rest), axis=None)
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
    
    
    # Print to file
    if coil is None:
        if timestamp is None:
            path = f"{outfolder}halfsine_profile"
        else:
            path = f"{outfolder}halfsine_profile_{timestamp}" 
    else:
        if timestamp is None:
            path = f"{outfolder}{coil}_halfsine_profile"
        else:
            path = f"{outfolder}{coil}_halfsine_profile_{timestamp}"
            
    
    with open((path + ".csv"), "w") as f:
        f.write("Seconds, Profile\n")
        for i in range(len(times_tot)):
            f.write(f"{times_tot[i]}, {profile[i]}\n")
        

    if figure:
        path = path + ".png"
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(times_tot, profile)
        #plt.show()
        fig.savefig(path, bbox_inches="tight", dpi=600)
        plt.close()
    
    
    return profile





























def generate_sine_profile(amp=1.0, freq=2.0,
                          phase=0.0, offset=0.0,
                          cycles=10, time_idle=1.0,
                          time_rest=4.0, sampling_rate=10000.0,
                          coil=None, outfolder="../out/",
                          timestamp=None, figure=False):
    
    logfolder = "../log/"
    outfolder = "../out/"
    tmpfolder = "../tmp/"
            
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    os.makedirs(tmpfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "sine_profile.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    
    dt = 1.0 / sampling_rate
    time_sine = cycles / freq
    
    """
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
    """
    
    times_idle = np.arange(0.0, time_idle, dt)
    times_sine = np.arange(0.0, time_sine, dt)
    times_rest = np.arange(0.0, time_rest, dt)
    
    # Convert from degrees to radians
    phase = phase / (2.0 * np.arccos(-1.0))
    
    omega = 2.0 * np.pi * freq
    x_idle = [offset for time in times_idle]
    #x_half = [amp * np.sin(omega * time) for time in times_half]
    x_sine = [offset + amp * np.sin(omega * time + phase) for time in times_sine] #A sin (wt + phi)
    x_rest = [offset for time in times_rest]
    profile = x_idle + x_sine + x_rest
    
    
    times_sine = times_sine + time_idle
    times_rest = times_rest + time_idle + time_sine
    
        
    times_tot = np.concatenate((times_idle, times_sine, times_rest), axis=None)
    dec = Decimal(str(dt)).as_tuple().exponent * -1
    times_tot = np.round(times_tot, dec)
    
    
    # Print to file
    with open((tmpfolder + "sine_profile.csv"), "w") as f:
        f.write("Seconds, Profile\n")
        for i in range(len(times_tot)):
            f.write(f"{times_tot[i]}, {profile[i]}\n")
    
    

    if coil is None:
        path = f"{tmpfolder}sine_profile.png"
    else:
        path = f"{tmpfolder}{coil}_sine_profile.png"
    
        
    
    
    if figure:
        path = path + ".png"
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(times_tot, profile)
        #plt.show()
        fig.savefig(path, bbox_inches="tight", dpi=600)
        plt.close()
    
  
    
    return profile

























"""
Flopper ramp current - Python translation for flying balls
"""

def generate_ramp_profile(f0=7.300, df=0.090,
                          k=0.465, drive_current=0,
                          drive_target=1, time_idle=1.0,
                          time_acc=1.0, time_ramp=5.0,
                          time_rest=1.0, sampling_rate=100.0,
                          coil=None, outfolder="../out/",
                          timestamp=None, figure=False):
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
    
    if figure:
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
    #generate_ramp_profile()
    #generate_halfsine_pulses_profile()
    generate_circular_motion_profile()




























    
    
if __name__ == "__main__":
    pass