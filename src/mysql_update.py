# -*- coding: utf-8 -*-

# Import libraries
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
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

"""Flying balls"""


def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "mysql_update.log", encoding='utf-8', level=logging.DEBUG)
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
                

        # Define tables
        TABLES = {}
        TABLES['livedata'] = ("""CREATE TABLE livedata (
                            run INTEGER NOT NULL,
                            timestamp DOUBLE NOT NULL,
                            ai0 DOUBLE NOT NULL,
                            ai19 DOUBLE NOT NULL,
                            ai3 DOUBLE
                            ) ENGINE=InnoDB""")
        TABLES['force_profile'] = ("""CREATE TABLE force_profile (
                            run INTEGER NOT NULL,
                            seconds DOUBLE NOT NULL,
                            profile DOUBLE NOT NULL,
                            position DOUBLE NOT NULL
                            ) ENGINE=InnoDB""")
        
        
        # Drop all tables. This will wipe all saved data
        """
        query = "DROP TABLE IF EXISTS {};"
        for table_name in TABLES:
            try:
                cur.execute(query.format(table_name))
                logging.info("Table {} dropped".format(table_name))
            except mysql.connector.Error as err:
                logging.warning(err)
        """
        
      
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
        
        
        # Evaluate 'run' number
        query = "SELECT MAX(run) FROM livedata;"
        try:
            cur.execute(query)
            ans = cur.fetchone()
            if ans[0] is None:
                run = 1
            else:
                run = ans[0] + 1
        except:
            print("Error in fetching run number from database")
            logging.error("Error in fetching run number from database")
            pass
        
        msg = "Running"
        processlist = []
        processlist.append(Process(target=loading, args=(msg, )))
        for p in processlist:
            try:
                logging.info("Starting process {}".format(p))
                p.start()
                print(str(p))
            except:
                print("Error starting {}".format(p))
                logging.error("Error starting {}".format(p))
                
        
        
        
        
        # Define force_profile file path
        dir_path = os.path.dirname(os.getcwd())
        dir_path=dir_path.replace("\\","/")
        tmpfolder = "/tmp/"
        filename = "force_profile.csv"
        filedir = dir_path + tmpfolder + filename
        tablename = "force_profile"
        columns = "(seconds, profile, position)"
        
        # Insert force profile into database
        try:
            query = """LOAD DATA INFILE '{}'
                       INTO TABLE {}
                       FIELDS TERMINATED BY ','
                       IGNORE 1 ROWS
                       {}
                       SET run=%s;""".format(filedir, tablename, columns)
            values = run,
            cur.execute(query, values)
            con.commit()
        except mysql.connector.Error as err:
            print(err)
            input()
            
            
            
        # Define data file path
        filename = "data.csv"
        filedir = dir_path + tmpfolder + filename
        tablename = "livedata"
        columns = "(timestamp, ai0, ai19, ai3)"
        
        # Insert data into database
        try:
            query = """LOAD DATA INFILE '{}'
                       INTO TABLE {}
                       FIELDS TERMINATED BY ','
                       IGNORE 1 ROWS
                       {}
                       SET run=%s;""".format(filedir, tablename, columns)
            values = run,
            cur.execute(query, values)
            con.commit()
        except mysql.connector.Error as err:
            print(err)
            input()
            
        
        for p in processlist:
            logging.info("Killing process {}".format(p))
            p.kill()
        
        
        # Close the database and terminate the program    
        input("Program completed successfully")
    except:
        pass
    finally:
        try:
            con.close()
            print("main() SQL connection successfully closed")
            logging.info("main() SQL connection successfully closed")
        except:
            print("main() SQL failed to close")
            logging.error("main() SQL failed to close")
            
    
    

# Function does as it says on the tin
def create_database(cur, db_name):
    try:
        cur.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'UTF8MB4'".format(db_name))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        logging.error("Failed creating database: {}".format(err))
        exit(1)




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


  
