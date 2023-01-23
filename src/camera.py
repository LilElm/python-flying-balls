import asyncio
from bleak import BleakScanner, BleakClient


import numpy as np
import time
import logging
import datetime
import os

import multiprocessing.connection
from multiprocessing import Process, Pipe

async def main(pipe_in, pipe_out):
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "camera.log", encoding='utf-8', level=logging.INFO)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S")) 
    

    
    # Define the camera
    address = "CC:86:EC:72:D2:54"
    MODEL_NBR_UUID = "5DD3465F-1AEE-4299-8493-D2ECA2F8E1BB"
    
    # Connect to the camera
    logging.info("Attempting to connect to camera with:")
    logging.info(f"Address: {address}")
    logging.info(f"MODEL_NBR_UUID: {MODEL_NBR_UUID}")
    async with BleakClient(address) as client:
        if client.is_connected:
            print("Connected to the camera")
            logging.info("Connected to the camera")
        
        # Start recording
        data1 = bytearray([1,5,0,0,10,1,1,0,2,0,0,0])
        logging.info("Sending 'START RECORDING' bytearray")
        await client.write_gatt_char(MODEL_NBR_UUID, data1, response=True)
        print("Recording started")
        logging.info("Recording started")
        
        # Send signal for rest of program to begin
        pipe_out.send(True)
        
        
        stop = False
        while not stop:
            if pipe_in.poll():
                stop = pipe_in.recv()
                logging.info("Received stop signal")
        
        
        # Stop recording
        data2 = bytearray([1,5,0,0,10,1,1,0,0,0,0,0])
        logging.info("Sending 'STOP RECORDING' bytearray")
        await client.write_gatt_char(MODEL_NBR_UUID, data2, response=True)
        print("Recording stopped")
        print("Closing Bluetooth connection")
    print("Connection closed")
    

        

def camera(pipe_in, pipe_out):
    asyncio.run(main(pipe_in, pipe_out))
    




    
    
    #CC:86:EC:72:D2:54: A:91A496D3
    
    #https://pypi.org/project/bleak/
    #https://bleak.readthedocs.io/en/latest/
    #https://bleak.readthedocs.io/en/latest/usage.html