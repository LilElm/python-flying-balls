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



def update_db(outfolder, outfolder_pre, outfolder_post, db_env):
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    #tmpfolder = "../tmp/"
    #outfolder = "../out/"
    os.makedirs(logfolder, exist_ok=True)
    os.makedirs(outfolder, exist_ok=True)
    os.makedirs(outfolder_pre, exist_ok=True)
    os.makedirs(outfolder_post, exist_ok=True)
    logging.basicConfig(filename = logfolder + "mysql_update.log", encoding='utf-8', level=logging.DEBUG)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))    


    # Change folder permissions so that the database (NETWORK SERVICE) can access the appropriate files
    os.system('icacls "C:\\Users\\ultservi\\Desktop\Elmy\\python-flying-balls" /T /grant "NETWORK SERVICE":F')
    
    msg = "Loading data into database"
    processlist = []
    #processlist.append(Process(target=loading, args=(msg, )))
    for p in processlist:
        try:
            logging.info("Starting process {}".format(p))
            p.start()
            print(str(p))
        except:
            print("Error starting {}".format(p))
            logging.error("Error starting {}".format(p))
                

    # Load in environmental parameters
    if db_env == None:
        load_dotenv()
    else:
        load_dotenv(db_env)
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



    
        # Evaluate 'run' number
        run_list = []
        query = "SHOW TABLES;"
        cur.execute(query)
        tables = cur.fetchall()
        
        if len(tables) == 0:
            run = 0
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
                            run_list.append(0)
                        else:
                            run_list.append(ans[0])
                    except:
                        print("Error in fetching run number from database")
                        print("Run assumed to be 0")
                        logging.error("Error in fetching run number from database")
                        logging.info("Run assumed to be 0")
                        pass
            run = max(run_list)  
        



        # Load in .CSV file and header names
        for root, dirs, files in os.walk(outfolder_pre, topdown=False):
            fileDict = {}
            # For each folder, run=+1 if folder contains *.csv
            if any(".csv" in file for file in files):
                run = run + 1
                
            for name in files:
                if ".csv" in name:
                    #filename = name.strip(".csv")
                    forename, timestamp = name.rsplit("_", 1)
                    timestamp = timestamp.strip(".csv")
                    # If timestamp is not a number, correct forename, timestamp
                    try:
                        test = float(timestamp)
                    except:
                        timestamp = None
                        forename = name.strip(".csv")
                    
                    with open(os.path.join(root, name), "r") as f:
                        line = f.readline().lower().strip("\n")
                        headers = line.split(", ")
                        headers = [scrub(elem) for elem in headers]
                        
                        #if "dat" in name:
                        #    timestamp = f.readline().lower().strip("\n").split(", ")[0]
                        f.seek(0)
                        
                        # Create fileDict object
                        fileDict[forename] = File(root=root, forename=forename, timestamp=timestamp, extension=".csv")
                        fileDict[forename].headers = headers
            
            
            # Define tables
            TABLES = {}
            for name in fileDict:
                forename = fileDict[name].forename
                
                TABLES[forename] = ("""CREATE TABLE {} (
                                   run INTEGER NOT NULL,
                                   INDEX index_run (run)
                                   ) ENGINE=InnoDB""").format(forename)
            
            
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
            #tmpfolder = "/tmp/"
            
            # Check if each table exists
            for table_name in TABLES:
                cur.execute(query1.format(db_name, table_name))
                cur.execute(query2)
                val = cur.fetchone()
                
                # Create the table if it does not exist
                if len(val[0]) == 0:
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
                # Add columns to the table if they do not exist
                for elem in fileDict[table_name].headers:
                    if elem not in headers:
                        try:
                            cur.execute(query4.format(table_name, elem))
                        except mysql.connector.Error as err:
                            input(err)
                con.commit()

                
            for file in fileDict:
                forename = fileDict[file].forename
                timestamp = fileDict[file].timestamp
                extension = fileDict[file].extension
                root = fileDict[file].root
    
                
                # Load data into the table
                columns = ", ".join(fileDict[file].headers)
                if timestamp == None:
                    name_old = f"{forename}{extension}"
                else:
                    name_old = f"{forename}_{timestamp}{extension}"
                root = root.strip("../")
                filedir = f"{root}/{name_old}"
                filedir = filedir.replace('\\', '/')
       
                
                values = run,
                try:
                    cur.execute(query5.format(filedir, forename, columns), values)
                    print(f"File {filedir} uploaded")
                except mysql.connector.Error as err:
                    input(str(err))
                
                con.commit()
                # Move files to ../outfolder_post/timestamp.csv
                
                if timestamp == None:
                    dt = ''
                else:
                    dt = datetime.datetime.fromtimestamp(float(timestamp)).strftime("%Y.%m.%d_%H%M%S")
                    
                name_new = "_".join([dt, forename])
                name_new = name_new + ".csv"
                path_old = filedir
                path_new = os.path.join(outfolder_post, name_new)
                shutil.move(path_old, path_new)
                
        # Close the database and terminate the program  
        for p in processlist:
            if p:
                logging.info("Killing process {}".format(p))
                p.kill()
        print("\nData successfully added to the database")
        time.sleep(2.0)
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


# Function scrubs input of invalid parameters
def scrub(text):
    return "".join( chr for chr in text if chr.isalnum() )

# Run
if __name__ == "__main__":
    val = sys.argv
    if len(val) > 1:
        
        outfolder = val[1]
        outfolder0 = val[2]
        outfolder1 = val[3]
        
        outfolder_pre = outfolder + outfolder0
        outfolder_post = outfolder + outfolder1
        
        
        
        db_env = val[4]
    else:
        outfolder = os.getcwd()
        outfolder = outfolder.rsplit('\\', 1)[0]
        outfolder = outfolder + "\\out\\"
        outfolder_pre = outfolder + "out_unprocessed\\"
        outfolder_post = outfolder + "out_processed\\"
        db_env = None
    update_db(outfolder, outfolder_pre, outfolder_post, db_env)
    


  
