# -*- coding: utf-8 -*-

# Import libraries
import asyncio
from bleak import BleakScanner, BleakClient
import logging
import datetime
import os
import sys


async def main(pipe_in, pipe_out):
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "camera.log", encoding='utf-8', level=logging.INFO)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S")) 
    
    # Clear the pipe
    if pipe_in.poll():
        while pipe_in.poll():
            pipe_in.recv()
    
    # Define the camera
    address = "CC:86:EC:72:D2:54"
    MODEL_NBR_UUID = "5DD3465F-1AEE-4299-8493-D2ECA2F8E1BB"
    
    # Connect to the camera
    logging.info("Attempting to connect to camera with:")
    logging.info(f"Address: {address}")
    logging.info(f"MODEL_NBR_UUID: {MODEL_NBR_UUID}")
    print("Attempting to connect to the camera")
    
    try:
        async with BleakClient(address) as client:
            if client.is_connected:
                print("Connected to the camera")
                logging.info("Connected to the camera")                            
                # Send signal for rest of program to begin
                #pipe_out.send(True)
                

            while True:
                if pipe_in.poll():
                    while pipe_in.poll():
                        val = pipe_in.recv()

            
                    # Start recording
                    if val == True:
                        data1 = bytearray([1,5,0,0,10,1,1,0,2,0,0,0])
                        logging.info("Sending 'START RECORDING' bytearray")
                        print("Sending 'START RECORDING' bytearray")
                        try:
                            await client.write_gatt_char(MODEL_NBR_UUID, data1, response=True)
                            print("Recording started")
                            logging.info("Recording started")
                            pipe_out.send(True)

                        except:
                            pipe_out.send(False)
                            print("Failed to communicate with the camera")
                            logging.info("Failed to communicate with the camera")
                    
                    
                    # Stop recording 
                    elif val == False:
                        data2 = bytearray([1,5,0,0,10,1,1,0,0,0,0,0])
                        logging.info("Sending 'START RECORDING' bytearray")
                        print("Sending 'STOP RECORDING' bytearray")
                        try:
                            await client.write_gatt_char(MODEL_NBR_UUID, data2, response=True)
                            print("Recording stopped")
                            logging.info("Recording stopped")
                        except:
                            pipe_out.send(False)
                            print("Failed to communicate with the camera")
                            logging.info("Failed to communicate with the camera")
     
                
                    # Disconnect
                    elif val == 0:
                        print("Closing Bluetooth connection")
                        logging.info("Closing Bluetooth connection")
                        logging.info("Exiting camera.py")
                        pipe_out.send(True)
                        break
                
        print("Connection closed")
    except:
        logging.info("Failed to connect to the camera")
        print("Failed to connect to the camera")
        sys.exit(1)
                    
                    
        
        
        

def start_camera(pipe_in, pipe_out):
    asyncio.run(main(pipe_in, pipe_out))
    

    
    #CC:86:EC:72:D2:54: A:91A496D3
    
    #https://pypi.org/project/bleak/
    #https://bleak.readthedocs.io/en/latest/
    #https://bleak.readthedocs.io/en/latest/usage.html