# -*- coding: utf-8 -*-

# Import libraries
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
from multiprocessing import Process, Pipe
import datetime
import time
import numpy as np
import pandas as pd
from itertools import cycle
import sys
import pyvisa
import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx import constants
import logging

"""Flying balls"""



def main():

    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "main.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))    


    # Load in environmental parameters
    load_dotenv()
    user = os.environ.get('USERN')
    password = os.environ.get('PASSWORD')
    db_name = os.environ.get('DB_NAME')
    
    

    # Try to connect to the server
    try:
        con = mysql.connector.connect(
            #host="localhost",
            user=user,
            password=password,
            #database=db_name,
            raise_on_warnings=True)
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
    
    
    # Outer loop handles databse connection
    try:
        # Try to connect to the database
        # If the database does not exist, try to create it
        try:
            cur.execute("USE {};".format(db_name))
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
    
        # Define table 'livedata'
        TABLES = {}
        TABLES['livedata'] = ("""CREATE TABLE livedata (
                            timestamp DOUBLE NOT NULL,
                            value DOUBLE NOT NULL
                            ) ENGINE=InnoDB""")
        
        
        # Drop tables ------------- this should only be temporary
        query = "DROP TABLE IF EXISTS {};"
        for table_name in TABLES:
            cur.execute(query.format(table_name))
            logging.info("Table {} dropped".format(table_name))
        
        
        # Create tables if they do not exist
        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print("Creating table {}: ".format(table_name))
                logging.info("Creating table {}: ".format(table_name))
                cur.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("Table already exists")
                    logging.info("Table already exists")
                else:
                    print(err.msg)
                    logging.error(err.msg)
        
        
        
    
    
        # Queues are built on top of pipes
        # Queues can handle multiple endpoints, but are consequently slower
        # Pipes can only handle two endpoints, but are faster
        # p_live handles live data
        # p_manip handles manipulated data
        p_live1, p_live2 = Pipe()
        p_manip1, p_manip2 = Pipe()
        
                              
        #print(str(cur))       
        #print(str(con))
        
        msg = "Running"
        processlist = []
        processlist.append(Process(target=get_data, args=(p_live1, )))
        processlist.append(Process(target=manipulate_data, args=(p_live2, p_manip1, )))
        processlist.append(Process(target=store_manipulated_data, args=(p_manip2, user, password, db_name, )))
        processlist.append(Process(target=loading, args=(msg, )))
        
        
        for p in processlist:
            try:
                logging.info("Starting process {}".format(p))
                p.start()
                print(str(p))
            except:
                print("Error starting {}".format(p))
                logging.error("Error starting {}".format(p))
            
        
        try:
            input("Press RETURN to stop data acquisition\n")
            pass
        except KeyboardInterrupt:
            logging.warning("Data acquisition stopped via keyboard interruption")
            #for p in processlist:
            #    p.kill()
            pass
        finally:
            for p in processlist:
                logging.info("Killing process {}".format(p))
                p.kill()
         
    
        # Close database
    except:
        pass
    finally:
        con.close()

    
    
 
    

def create_database(cur, db_name):
    try:
        cur.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'UTF8MB4'".format(db_name))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        logging.error("Failed creating database: {}".format(err))
        exit(1)




# Function acquires and buffers live data from DAQ board and pipes it
# to manipualte_data()
def get_data(p_live):
    try:
        with nidaqmx.Task() as task:
            num_channels = 1
            num_samples = 100
            rate = 1000
           
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.ai_channels.all.ai_max = 10.0 #max_voltage
            task.ai_channels.all.ai_min = -10.0 #min_voltage
            task.timing.cfg_samp_clk_timing(rate, sample_mode=constants.AcquisitionType.CONTINUOUS)
            reader = AnalogMultiChannelReader(task.in_stream)
            buffer = np.zeros((num_channels, num_samples), dtype=np.float64)
            while True:
                try:
                    time_start = time.time()
                    reader.read_many_sample(buffer, num_samples, timeout=constants.WAIT_INFINITELY)
                    time_end = time.time()
                    data_live = buffer.T.astype(np.float32)
                    
                    data = [data_live, time_start, time_end]
                    p_live.send(data)
                     
                except:
                    task.close()
                    print("Error reading data from DAQ board.")
                    logging.error("Error reading data from DAQ board.")
                    break
    except KeyboardInterrupt:
        logging.warning("Data acquisition stopped via keyboard interruption")
    finally:
        pass




# Function recieves buffered data from get_data(), restructures it and pipes
# it to store_manipulated_data()
def manipulate_data(p_live, p_manip):
    try:
        while True:
            try:
                data = p_live.recv()
             
                # Unpackage the data
                data_live = data[0]
                time_start = data[1]
                time_end = data[2]
                
                # Restructure the data
                data_manipulated = []
                size = len(data_live)
                time_int = (time_end - time_start) / size
                for i in range(size):
                    time_eval = time_start + time_int * i
                    data_manipulated.append([time_eval, float(data_live[i])])
                    
                p_manip.send(data_manipulated)
            except:
                break
    except KeyboardInterrupt:
        logging.warning("Data manipulation stopped via keyboard interruption")
    finally:
        pass

        


# Function connects to the server, recieves manipualted data from 
# manipulated_data() and inserts it in the database
def store_manipulated_data(p_manip, user, password, db_name): 
    # Try to connect to the server
    try:
        con = mysql.connector.connect(
            #host="localhost",
            user=user,
            password=password,
            database=db_name,
            raise_on_warnings=True)
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
            logging.error(err)
            exit(1)
    
    try:
        query = "INSERT INTO livedata (timestamp, value) VALUES (%s, %s);"
        while True:
            try:
                data_manipulated = p_manip.recv()
                values = data_manipulated
                cur.executemany(query, values)
                con.commit()
            except KeyboardInterrupt:
                logging.warning("Data storage stopped via keyboard interruption")
    except:
        pass
    finally:
        try:
            con.close()
            print("store_manipulated_data() SQL connection successfully closed")
            logging.info("store_manipulated_data() SQL connection successfully closed")
        except:
            print("store_manipulated_data() SQL failed to close")
            logging.error("store_manipulated_data() SQL failed to close")
 




# Function shows a pretty pinwheel
def loading(msg):
    time.sleep(1)
    while True:
        try:
            for frame in cycle(["|","/","-","\\"]):
                sys.stdout.write("\r" + msg + " " + frame)
                sys.stdout.flush()
                time.sleep(0.15)
            sys.stdout.write("\r")
        except KeyboardInterrupt:
            logging.warning("Pinwheel stopped via keyboard interruption")
    








# Run
if __name__ == "__main__":
    main()


  
