# -*- coding: utf-8 -*-

# Import libraries
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
import multiprocessing.connection
from multiprocessing import Process, Pipe
import datetime
import time
import numpy as np
from itertools import cycle
import sys
import logging
import shutil


"""Flying balls
If errno13, add NETWORK SERVICE to folder permissions."""

class File():
    def __init__(self, root, forename, timestamp, extension):
        self.root = root
        self.forename = forename
        self.timestamp = timestamp
        self.extension = extension



def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    #tmpfolder = "../tmp/"
    #outfolder = "../out/"
#    os.makedirs(logfolder, exist_ok=True)
 #   os.makedirs(outfolder, exist_ok=True)
  #  os.makedirs(outfolder_post, exist_ok=True)
    logging.basicConfig(filename = logfolder + "resort_files.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))    


    outfolder = "../out/"
    folder = "out_processed_copy/"
    current_folder = outfolder + folder#"../out/out_processed_copy/"

    cwd = os.getcwd()
    cwd = cwd.rsplit('\\', 1)[0]
    cwd = cwd + "\\out\\out_processed_copy\\"
    input(str(cwd))

    leave = 0
    counter = 0
    timestamp = None
    # Load in .CSV file and header names
    for root, dirs, files in os.walk(current_folder, topdown=False):
        fileDict = {}
        
        # Sort by date, newest to oldest
        for name in sorted(files, key=lambda name:
                           -1*os.path.getmtime(os.path.join(root, name))):
            leave = 0
            
            if ".csv" in name:
                filename = name.strip(".csv")
                
                if "data" in name:
                    counter = 0
                    
                    
                    # Read file
                    # Read first timestamp
                    # Make folder called timestamp if not exists
                    # Move file into timestamp
                    # Rename file to be data_timestamp.csv
                    
                    
                    with open(os.path.join(root, name), "r") as f:
                        line = f.readline()
                        timestamp = f.readline().lower().strip("\n").split(", ")[0]
                        f.seek(0)
                    
                    
                    new_folder = f"{current_folder}{timestamp}/"
                    os.makedirs(new_folder, exist_ok=True)
                    path_old = f"{cwd}{name}".replace('\\', '/')
                    path_new = f"{cwd}{timestamp}/data_{timestamp}.csv"
                    shutil.copy(path_old, path_new)
                    
                    
                
                if "coils" in name:
                    counter = 0
                    
                    # Read file
                    # Read first timestamp
                    # Make folder called timestamp if not exists
                    # Move file into timestamp
                    # Rename file to be coils_timestamp.csv
                    
                    
                    
                    
                    with open(os.path.join(root, name), "r") as f:
                        line = f.readline()
                        timestamp = f.readline().lower().strip("\n").split(", ")[0]
                        f.seek(0)
                    
                    
                    new_folder = f"{current_folder}{timestamp}/"
                    os.makedirs(new_folder, exist_ok=True)
                    path_old = f"{cwd}{name}".replace('\\', '/')
                    path_new = f"{cwd}{timestamp}/coils_{timestamp}.csv"
                    shutil.copy(path_old, path_new)
                    
                    
                    
                
                if "profile" in name:
                    
                    # If previous was data or coils; or if previous was profile but not previous before:
                    # move into last created folder
                    # Rename to be timestamp_whichever profile
                
                    
                    counter = counter + 1
                    if counter > 2:
                        #input(str(counter))
                        #input(str(name))
                        #break
                        leave = 1
                    if timestamp == None:
                        #input(str(timestamp))
                        #input(str(name))
                        #break
                        leave = 1
                    if leave == 0:
                        
                        profile = filename.split("_", 2)[-1]
                        
                        
                        
                        #input(str(ooga))
                        
                        
                        new_folder = f"{current_folder}{timestamp}/"
                        os.makedirs(new_folder, exist_ok=True)
                        path_old = f"{cwd}{name}".replace('\\', '/')
                        path_new = f"{cwd}{timestamp}/{profile}_{timestamp}.csv"
                        shutil.copy(path_old, path_new)
                        
                
                
            
      
    

# Run
if __name__ == "__main__":
    main()



  
