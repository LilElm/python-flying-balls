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
#import pandas as pd
from itertools import cycle
import sys
#import pyvisa
import nidaqmx
import nidaqmx.system
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx import constants
import logging
from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

"""Flying balls"""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, pipe, *args, **kwargs):
        self.pipe = pipe
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel('left', 'Voltage (V)')
        self.graphWidget.setLabel('bottom', 'Elapsed Time (s)')
        self.setCentralWidget(self.graphWidget)

        self.ai0 = []
        self.ai1 = []
        self.ai3 = []
        self.elapsed_time = []
        
        self.graphWidget.addLegend()
        self.line_ai0 =  self.graphWidget.plot(self.elapsed_time, self.ai0, name="ai0", pen=pg.mkPen('b'))
        self.line_ai1 =  self.graphWidget.plot(self.elapsed_time, self.ai1, name="ai1", pen=pg.mkPen('r'))
        self.line_ai3 =  self.graphWidget.plot(self.elapsed_time, self.ai3, name="ai3", pen=pg.mkPen('y'))
        
        self.counter = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot)#_data)
        self.timer.start()
        self.update_plot()
    
    def update_plot(self):
        try:
            if True:
                data = self.pipe.recv()
                if self.counter == 0:
                    self.time_start = data[0]
                    self.counter = 1
                
                elapsed_time = data[0] - self.time_start
                ai0 = data[1]
                ai1 = data[2]
                ai3 = data[3]
                
                self.elapsed_time.append(elapsed_time)
                self.ai0.append(ai0)
                self.ai1.append(ai1)
                self.ai3.append(ai3)
                
                if len(self.ai0) > 200:
                    self.elapsed_time = self.elapsed_time[1:]
                    self.ai0 = self.ai0[1:]
                    self.ai1 = self.ai1[1:]
                    self.ai3 = self.ai3[1:]
                
                self.line_ai0.setData(self.elapsed_time, self.ai0)
                self.line_ai1.setData(self.elapsed_time, self.ai1)
                self.line_ai3.setData(self.elapsed_time, self.ai3)
            
        except:
            print("err")
            

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
                            ai0 DOUBLE NOT NULL,
                            ai1 DOUBLE NOT NULL,
                            ai3 DOUBLE,
                            ao0 DOUBLE
                            ) ENGINE=InnoDB""")
        


        # Drop tables ------------- this should only be temporary
        query = "DROP TABLE IF EXISTS {};"
        for table_name in TABLES:
            try:
                cur.execute(query.format(table_name))
                logging.info("Table {} dropped".format(table_name))
            except mysql.connector.Error as err:
                logging.warning(err)
      
        
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
        p_live_dev1_1, p_live_dev1_2 = Pipe()
        p_time0_1, p_time0_2 = Pipe()
        p_manip_dev1_1, p_manip_dev1_2 = Pipe()
        p_plot_dev1_1, p_plot_dev1_2 = Pipe()
        
                              
        #print(str(cur))       
        #print(str(con))
        
        msg = "Running"
        processlist = []
        
        
        # Add channel number, num_samples, rate
        #"Dev1/ai0"
        
        # Maybe create a task disctionary?
        
        #channels = ["Dev1/ai0", "Dev1/ai1"]
        
        #taskDict = {task for channel in channels}
        # Reset device
        system = nidaqmx.system.System.local()
        for device in system.devices:
            print("Resetting device {}".format(device))
            logging.info("Resetting device {}".format(device))
            try:
                device.reset_device()
                logging.info("Device {} successfully reset".format(device))
            except:
                print("Device {} failed to reset".format(device))
                logging.warning("Device {} failed to reset".format(device))
                
        
            
        ###### Cannot import tasks into processes - same error as with importing con and cur
                # I think the only option left is to have the two tasks within the same function
                # Define the task parameters in an object and import the object into the function
                
                

       
        
        processlist.append(Process(target=get_data, args=(p_live_dev1_1, p_time0_1, )))
        processlist.append(Process(target=manipulate_data, args=(p_live_dev1_2, p_time0_2, p_manip_dev1_1, p_plot_dev1_1, )))
        processlist.append(Process(target=store_manipulated_data, args=(p_manip_dev1_2, user, password, db_name, "livedata", )))
       
        
       
        # Process to plot livedata
        
        processlist.append(Process(target=plot_live_data, args=(p_plot_dev1_2, )))


        
        
        
        

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
def get_data(p_live0, p_time0):
    try:    
        with nidaqmx.Task() as task0:
            
            ## Configure tasks
            ## Task 0 (Dev1/ai0, Dev1/ai1)
            num_channels0 = 3
            rate0 = 500
            num_samples0 = 100#* 2 # 500000 # per channel
            task0.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task0.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            task0.ai_channels.add_ai_voltage_chan("Dev1/ai3")
            task0.ai_channels.all.ai_max = 10.0 #max_voltage
            task0.ai_channels.all.ai_min = -10.0 #min_voltage
            
            task0.timing.cfg_samp_clk_timing(rate0, sample_mode=constants.AcquisitionType.CONTINUOUS)
            
            reader0 = AnalogMultiChannelReader(task0.in_stream)
            buffer0 = np.zeros((num_channels0, num_samples0), dtype=np.float64)
            
            
            while True:
                try:
                    time_start0 = time.time()
                    reader0.read_many_sample(buffer0, num_samples0, timeout=constants.WAIT_INFINITELY)
                    time_end0 = time.time()
                    times = [time_start0, time_end0]
                    
                    data_live0 = buffer0.T.astype(np.float32)
                    #data_live0 = buffer0.T.astype(np.float64)
                    
                    # Tested for a buffer size of 5e6
                    # One pipe took ~0.081 s
                    # Two pipes took ~0.076 s
                    # Hence two pipes are about 5 one-thousandths of a second
                    # quicker for the aforementioned buffer size. This is
                    # because two pipes require less data manipulation
                    
                    p_live0.send(data_live0)
                    p_time0.send(times)
                    pipe_end = time.time()
                    
                except nidaqmx.errors.DaqError as err:
                    task0.close()
                    print(err)
                    logging.error(err)
                    break
    except KeyboardInterrupt:
        logging.warning("Data acquisition stopped via keyboard interruption")
    finally:
        pass
    




# Function recieves buffered data from get_data(), restructures it and pipes
# it to store_manipulated_data()
def manipulate_data(p_live, p_time, p_manip, p_plot):
    try:  
        buffer_rate = 0.1
        time_next = time.time() - buffer_rate
        while True:
            try:
                # Unpackage the data
                data_live = p_live.recv()
                time_data = p_time.recv()
                data_live_ai0 = data_live[:,0]
                data_live_ai1 = data_live[:,1]                
                data_live_ai3 = data_live[:,2]
                
                time_start = time_data[0]
                time_end = time_data[1]
                
                # Restructure the data
                data_manipulated = []
                size = len(data_live)
                
                time_int = (time_end - time_start) / size
               
                for i in range(size):
                    time_eval = time_start + time_int * i
                    data_manipulated.append([time_eval, float(data_live_ai0[i]), float(data_live_ai1[i]), float(data_live_ai3[i])])
                    
                    if time_eval >= time_next:
                        time_next = time_next + buffer_rate
                        p_plot.send(data_manipulated[i])
                
                p_manip.send(data_manipulated)
               
            except:
                print("Error in data manipulation")
                break
    except KeyboardInterrupt:
        logging.warning("Data manipulation stopped via keyboard interruption")
    finally:
        pass
"""
def update(val):
    global curve, ptr, Xm    
    Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    #value = ser.readline()                # read line (single value) from the serial port
#    Xm[-1] = float(value)                 # vector containing the instantaneous values  
    Xm[-1] = val
    
    ptr += 1                              # update x position for displaying the curve
    curve.setData(Xm)                     # set the curve with this data
    curve.setPos(ptr,0)                   # set x position in the graph to 0
    QtGui.QApplication.processEvents()    # you MUST process the plot now

"""





def plot_live_data(p_plot):
    #app = QtGui.QApplication([])
    #win = pg.GraphicsWindow(title="Window Title")
    #p = win.addPlot(title="Plot Title")
    #fig = p.plot()
    
    #windowWidth = 500
    #time_plot = np.linspace(0,0,windowWidth)
    #ai0_plot = np.linspace(0,0,windowWidth)
    #ptr = -windowWidth
    
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(p_plot)
    w.show()
#    w.add_pipe(p_plot)
    sys.exit(app.exec_())
    """
    counter = 0
    try:
        while True:
           # time_plot[:-1] = time_plot[1:]
           # ai0_plot[:-1] = ai0_plot[1:]
            
            # Recieve data
            data = p_plot.recv()
            if counter == 0:
                time_start = data[0]
                counter = 1
            
            elapsed_time = data[0] - time_start
            ai0 = data[1]
            ai1 = data[2]
            ai3 = data[3]
            
            print("alk")
            w.data_line.setData(elapsed_time, ai0)
           # time_plot[-1] = elapsed_time
           # ai0_plot[-1] = ai0
            

            #w.update_plot_data(elapsed_time, ai0)
            #w.x.append(elapsed_time)
            #w.y.append(ai0)
            
           # Xm[-1] = ai0
          #  ptr += 1
           # fig.setData(time_plot, ai0_plot)
           # fig.setPos(ptr,0)
           # QtGui.QApplication.processEvents()
           
            
            
    except:
        pass
        #pg.QtGui.QApplication.exec_()
        
    """
    """        
        # update
        plt.scatter(timestamp, ai0)
        plt.scatter(timestamp, ai1)
        #plt.pause(0.05)
        
        plt.show()
        plt.pause(0.005)
    """
        
        


# Function connects to the server, recieves manipualted data from 
# manipulated_data() and inserts it in the database
def store_manipulated_data(p_manip, user, password, db_name, table_name):
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
        #query = "INSERT INTO livedata (timestamp, value) VALUES (%s, %s);"
        query = "INSERT INTO {} (timestamp, ai0, ai1, ai3) VALUES (%s, %s, %s, %s);".format(table_name)
        while True:
            try:
                data_manipulated = p_manip.recv()
                values = data_manipulated
                
                cur.executemany(query, values)
                con.commit()
            except mysql.connector.Error as err:
                print(err)
    except KeyboardInterrupt:
        logging.warning("Data storage stopped via keyboard interruption")
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


  
