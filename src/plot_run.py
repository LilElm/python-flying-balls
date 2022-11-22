# -*- coding: utf-8 -*-

# Import libraries
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

#warnings.filterwarnings('error', category=MySQLdb.Warning)
import multiprocessing.connection
multiprocessing.connection.BUFSIZE = 2**32-1 # This is the absolute limit for this PC
from multiprocessing import Process, Pipe
import datetime
import time
import numpy as np
from itertools import cycle
import sys
import nidaqmx
import nidaqmx.system
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx import constants
import logging
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from force_profile import eval_force
import msvcrt
import matplotlib.pyplot as plt

import pandas as pd

"""Flying balls"""




# Read from database
# Plot relevant parameters



   

def main():
    logfolder = "../log/"
    outfolder = "../out/"
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(logfolder, exist_ok=True)
    currentDT = datetime.datetime.now()
    logging.basicConfig(filename = logfolder + "plot_run.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  


    # Load in environmental parameters
    load_dotenv()
    user = os.environ.get('USERN')
    password = os.environ.get('PASSWORD')
    db_name = os.environ.get('DB_NAME')


    # Try to connect to the server
    # Nota bene, raise_on_warnings=False
    # This is due to setting user variables within expressions
    # This will be deprecated in a future release
    try:
        con = mysql.connector.connect(
            #host="localhost",
            user=user,
            password=password,
            #database=db_name,
            raise_on_warnings=False)
        cur = con.cursor()
        print("Successfully connected to MySQL server")
        logging.info("Successfully connected to MySQL server")
    except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
            logging.error("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Server cannot be found")
            logging.error("Server cannot be found")
          else:
              print(err)
              exit(1)
    
    
    # Outer loop handles database connection
    try:
        # Try to connect to the database
        # If the database does not exist, try to create it
        try:
            cur.execute("USE {};".format(db_name))
            print("Successfully connected to database {}".format(db_name))
            logging.info("Successfully connected to database {}".format(db_name))
        except mysql.connector.Error as err:
            print("Database {} does not exists".format(db_name))
            logging.warning("Database {} does not exists".format(db_name))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                create_database(cur, db_name)
                print("Database {} created successfully".format(db_name))
                logging.error("Database {} created successfully".format(db_name))
            else:
                print(err)
                logging.error(err)
                exit(1)
    
        
    
        # Evaluate 'run' number
        query = "SELECT MAX(run) FROM livedata;"
        try:
            cur.execute(query)
            ans = cur.fetchone()
            if ans[0] is None:
                print("Error in fetching run number from database")
                logging.error("Error in fetching run number from database")
                exit()
            else:
                run = ans[0]
        except:
            print("Error in fetching run number from database")
            logging.error("Error in fetching run number from database")
            exit()
        




        # This method will be deprecated in a future release due to the
        # setting of user variables within an expression            
        query = """SELECT *
                   FROM ( 
                       SELECT 
                           @row := @row +1 AS rownum, {}
                       FROM ( 
                           SELECT @row :=0) r, {} 
                       WHERE (
                           run=%s)
                       ) filtered 
                   WHERE rownum % 1=0;
                """
        values = run,


        

        #query = "SELECT seconds, profile FROM force_profile WHERE run=%s;"
        
        # Get force profile
        try:
            cur.execute(query.format("seconds, profile", "force_profile"), values)
            data = cur.fetchall()
            df_profile = pd.DataFrame(data, columns=["rownum", "seconds", "profile"])
        except mysql.connector.Error as err:
            print(str(err))
            input()

        # Get livedata
        try:
            cur.execute(query.format("timestamp, ai0, ai19, ai3", "livedata"), values)
            data = cur.fetchall()
            df_live = pd.DataFrame(data, columns=["rownum", "timestamp", "ai0", "ai19", "ai3"])
        except mysql.connector.Error as err:
            print(str(err))
            input()
            
        # Adjust times to reflect elapsed time
        seconds0 = df_profile['seconds'][0]
        df_profile['t_elapsed'] = df_profile['seconds'] - seconds0
        
        timestamp0 = df_live['timestamp'][0]
        df_live['t_elapsed'] = df_live['timestamp'] - timestamp0
        
        
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(df_live['t_elapsed'], df_live['ai0'], label='ai0')
        ax.plot(df_live['t_elapsed'], df_live['ai19'], label='ai19')
        ax.plot(df_live['t_elapsed'], df_live['ai3'], label='ai3')
        ax.plot(df_profile['t_elapsed'], df_profile['profile'], label='profile')
        plt.legend()
        
        path = "{}data_{}_run{}.png".format(outfolder, str(timestamp0),str(run))
        fig.savefig(path, bbox_inches="tight", dpi=600)
        
        plt.show()
        
        input()
    
        #np.ravel(times_tot)
        #np.ravel(profile)
            
        
    
    
    except:
        pass
    
    
    
    
    

    
# Function does as it says on the tin
def create_database(cur, db_name):
    try:
        cur.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'UTF8MB4'".format(db_name))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        logging.error("Failed creating database: {}".format(err))
        exit(1)

    
    
    
    
    
# Run
if __name__ == "__main__":
    main()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    