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
    tmpfolder = "../tmp/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "mysql_update.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))    

    
    msg = "Loading data into database"
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


        # Load in .CSV file and header names
        filenames = []
        fileDict = {}
        for root, dirs, files in os.walk(tmpfolder, topdown=False):
            for name in files:
                if ".csv" in name:
                    filenames.append(name.strip(".csv"))
                    with open(os.path.join(root, name), "r") as f:
                        line = f.readline().lower().strip("\n")
                        headers = line.split(", ")
                        fileDict[filenames[-1]] = headers
                        f.seek(0)
        
        
        # Evaluate 'run' number
        run_list = []
        query = "SHOW TABLES;"
        cur.execute(query)
        tables = cur.fetchall()
        
        if len(tables) == 0:
            run = 1
        else:
            tables = [table[0] for table in tables]
    
            query1 = "DESCRIBE {}"
            query2 = "SELECT MAX(run) FROM {};"
            for table in tables:
                cur.execute(query1.format(table))
                columns = cur.fetchall()
                columns = [column[0] for column in columns]
                if "run" in columns:
                    try:
                        cur.execute(query2.format(table))
                        ans = cur.fetchone()
                        if ans[0] is None:
                            run_list.append(1)
                        else:
                            run_list.append(ans[0] + 1)
                    except:
                        print("Error in fetching run number from database")
                        print("Run assumed to be 1")
                        logging.error("Error in fetching run number from database")
                        print("Run assumed to be 1")
                        pass
            run = max(run_list)        
        
        # Define tables
        TABLES = {}
        for name in filenames:
            TABLES[name] = ("""CREATE TABLE {} (
                               run INTEGER NOT NULL
                               ) ENGINE=InnoDB""").format(name)
        
        
        query1 = "CALL sys.table_exists('{}', '{}', @exists);"
        query2 = "SELECT @exists;"
        query3 = """SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = '{}' AND table_name = '{}'
                    ORDER BY ordinal_position;"""
        query4 = """ALTER TABLE {} ADD COLUMN {} DOUBLE;"""
        query5 = """LOAD DATA INFILE '{}'
                    INTO TABLE {}
                    FIELDS TERMINATED BY ','
                    IGNORE 1 ROWS
                    ({})
                    SET run=%s;"""
                    
                    
        # Define force_profile file path
        dir_path = os.path.dirname(os.getcwd())
        dir_path=dir_path.replace("\\","/")
        tmpfolder = "/tmp/"
        
        for table_name in TABLES:
            # Check if the table exists
            cur.execute(query1.format(db_name, table_name))
            cur.execute(query2)
            val = cur.fetchone()
            
            if len(val[0]) == 0:
                # Create the table if it does not exist
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
            
  
            # Check if the necessary columns exist
            try:
                cur.execute(query3.format(db_name, table_name))
            except mysql.connector.Error as err:
                input(err)
            headers = cur.fetchall()
            headers = [elem[0] for elem in headers]            
            # result = all(elem in headers for elem in fileDict[table_name])
            # print(str(result))


            for elem in fileDict[table_name]:
                if elem not in headers:
                    # Add the necessary columns to the table if they do not exist
                    try:
                        cur.execute(query4.format(table_name, elem))
                    except mysql.connector.Error as err:
                        print(err)
                        input()
            con.commit()
            
            # Load data into the table
            columns = ", ".join(fileDict[table_name])
            filedir = dir_path + tmpfolder + table_name + ".csv"
            values = run,
            try:
                cur.execute(query5.format(filedir, table_name, columns), values)
            except mysql.connector.Error as err:
                print(str(err))
                input()
            con.commit()
        

        # Close the database and terminate the program  
        for p in processlist:
            if p:
                logging.info("Killing process {}".format(p))
                p.kill()
        input("\nProgram completed successfully")
    except:
        pass
    finally:
        for p in processlist:
            if p:
                logging.info("Killing process {}".format(p))
                p.kill()
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


  
