# -*- coding: utf-8 -*-

# Import libraries
from decimal import *
getcontext().prec = 10
import numpy as np
import sys
import time
from itertools import cycle
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QSplashScreen,
                             QLabel,
                             QWidget,
                             QPushButton,
                             QGroupBox,
                             QCheckBox,
                             QComboBox,
                             QLineEdit,
                             QTextEdit,
                             QTabWidget,
                             QMenuBar,
                             QMenu,
                             QDialog,
                             QDialogButtonBox,
                             QAction,
                             QMessageBox,
                             QHBoxLayout,
                             QVBoxLayout,
                             QGridLayout,
                             QFormLayout)
from PyQt5.QtGui import QIcon, QColor, QPixmap, QPainter, QMovie
from PyQt5.QtCore import QTimer, QTextStream, QObject, pyqtSignal, QProcess, QRunnable, QThreadPool, QThread
import pyqtgraph as pg


import multiprocessing.connection
multiprocessing.connection.BUFSIZE = 2**32-1 # This is the absolute limit for this PC
from multiprocessing import Process, Pipe

from profiles import generate_halfsine_profile, generate_ramp_profile
from daq import daq_single

from coil_class import CoilChannel, CoilProfileLayout

class MenuLayout(QHBoxLayout):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


        # This doesn't seem like an ideal solution. There's a big gap at the top
        
        #================================================================
        # create menu
        menubar = QMenuBar()
        self.addWidget(menubar)#, 0, 0)
        actionFile = menubar.addMenu("File")
        actionFile.addAction("New")
        actionFile.addAction("Open")
        actionFile.addAction("Save")
        actionFile.addSeparator()
        actionFile.addAction("Quit")
        menubar.addMenu("Edit")
        menubar.addMenu("View")
        menubar.addMenu("Help")
        
        
       # self.addWidget(self.path_textbox, 0, 0, 1, 1)
        #self.addWidget(QLabel("Output Path"), 1, 0, 1, 1)
        
     #   self.addWidget(self.db_textbox, 0, 1, 1, 1)
      #  self.addWidget(QLabel("DB Environment"), 1, 1, 1, 1)
        
        
       # self.addWidget(self.checkbox, 0, 2, 1, 1)
        #self.addWidget(QLabel("Save to File?"), 1, 2, 1, 1)
        


class FileSettingsLayout(QGridLayout):
    def __init__(self, checkbox, path_textbox, db_textbox, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.checkbox = checkbox
        self.path_textbox = path_textbox
        self.db_textbox = db_textbox

        
        #================================================================
        # Layout fsettings
        # Make default value be read from file
        # If path doesn't exist, make it
        
        """
        path = "C:\\Users\\ultservi\\Desktop\\FlyingBalls\\"
        self.addWidget(QLineEdit(path), 0, 0, 1, 1)
        self.addWidget(QLabel("Path"), 1, 0, 1, 1)
       
        self.addWidget(QLineEdit(f"{path}.env"), 0, 1, 1, 1)
        self.addWidget(QLabel("DB Environment"), 1, 1, 1, 1)
        """
        
        
        self.addWidget(self.path_textbox, 0, 0, 1, 1)
        self.addWidget(QLabel("Output Path"), 1, 0, 1, 1)
        
        self.addWidget(self.db_textbox, 0, 1, 1, 1)
        self.addWidget(QLabel("DB Environment"), 1, 1, 1, 1)
        
        
        self.addWidget(self.checkbox, 0, 2, 1, 1)
        self.addWidget(QLabel("Save to File?"), 1, 2, 1, 1)
        

        


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)







class Worker(QRunnable):
    def __init__(self, fn, **kwargs):
        super().__init__()
        self.fn = fn
        self.setAutoDelete(False)
        #self.args = args
        
        self.kwargs = kwargs['kwargs']
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            result = self.fn(self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()
            










class RampSettingsLayout(QVBoxLayout):
    def __init__(self,
                 coil_dict,
                 parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.coil_dict = coil_dict
        
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(250) #ms
        self.timer.timeout.connect(self.update_console)
        self.timer.start()
    
    
    



        
        #self.coil_names = ["Lateral Coils", "Longitudinal Coils"]
        
        
        #for coil in self.coil_dict:
         #   self.coil_dict[coil].add_layout()
        
        
        #self.coil_layout_dict = {coil: CoilProfileLayout(coil=coil) for coil in self.coil_names}
        #self.coil_box_dict = {coil: QGroupBox(coil) for coil in self.coil_names}
        
        for coil in self.coil_dict:
            self.addWidget(self.coil_dict[coil].box)
        
        
        
        layout_start = QGridLayout()
        
        
        self.textbox_srate = QLineEdit(placeholderText="Sampling Rate")
        self.textbox_f0 = QLineEdit("7.300", placeholderText="Frequency")
        self.textbox_df = QLineEdit("0.090", placeholderText="Line Width")
        self.textbox_k = QLineEdit("0.465", placeholderText="Spring Constant")
        self.led = QPixmap('../fig/LED_red.png').scaled(20,20)
        self.led_label = QLabel()
        self.led_label.setPixmap(self.led)
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.clicked.connect(self.start_on_click)
        self.stop_button.clicked.connect(self.stop_on_click)
    
        layout_start.addWidget(self.textbox_srate)
        layout_start.addWidget(QLabel("Sampling Rate\n(Hz)"))
        
        layout_start.addWidget(self.textbox_f0)
        layout_start.addWidget(QLabel("Frequency\n(Hz)"))
        layout_start.addWidget(self.textbox_df)
        layout_start.addWidget(QLabel("Line Width\n(Hz)"))
        layout_start.addWidget(self.textbox_k)
        layout_start.addWidget(QLabel("Spring Constant\n(mm/V)"))
        layout_start.addWidget(self.led_label)
        
        
        layout_start.addWidget(self.start_button)
        layout_start.addWidget(self.stop_button)
       
        """
        layout_start.addWidget(self.console)
        """
        
        box_start = QGroupBox()
        box_start.setLayout(layout_start)
        box_start.setMaximumWidth(250)
        self.addWidget(box_start)
        
        
        """
        
                 pipe_param,
                 pipe_signal,
                 checkbox,
                 path_textbox,
                 db_textbox,
                 console,
                 pipe_console,
                 pipe_outputplotb,
                 pipe_inputplotb,
                 textbox_ni,
                 checkbox_ni,
                 textbox_guiresolution,
                 #textbox_guirefresh,
                 pipe_buffer,
                 pipe_getdatab,
                 textbox_cameratimeout,
                 checkbox_camera,
        
        """
        
        #============================================================
        # Layout of Ramp Settings
        # 
        # RampSettingsLayout = Parent
        # QGroupBox = Child
        # layout.addWidget(Widgets)
        # QGroupBox.setLayout(layout)
        """
        self.pipe_param = pipe_param
        self.pipe_signal = pipe_signal
        self.checkbox = checkbox
        self.path_textbox = path_textbox
        self.db_textbox = db_textbox
        self.console = console
        self.pipe_console = pipe_console
        self.pipe_outputplotb = pipe_outputplotb
        self.pipe_inputplotb = pipe_inputplotb
        
        self.textbox_ni = textbox_ni
        self.checkbox_ni = checkbox_ni
        self.textbox_guiresolution = textbox_guiresolution
        #self.textbox_guirefresh = textbox_guirefresh
        self.pipe_buffer = pipe_buffer
        
        self.pipe_getdatab = pipe_getdatab
        
        
        
        
        self.textbox_cameratimeout = textbox_cameratimeout
        self.checkbox_camera = checkbox_camera
        """
        
        #self.consoleprocess.write("fnlkfnalsk")
        #self.consoleprocess.setProcessChannelMode(QProcess.MergedChannels)
        #self.consoleprocess.readyRead.connect(self.update_console)
        
        #self.consoleprocess.write("fnlkfnalsk")
        #connect(self.console)
        
        self.init_thread_pool()
        
        
        
        
    
    def init_thread_pool(self):
        self.pool = QThreadPool()
        self.create_check_input_thread()
        self.create_force_profile_thread()
        self.create_daq_thread()
    
    
    
    
    def create_check_input_thread(self):
        pass
        """
        self.thread_check_input = Worker(self.check_input,
                                         kwargs=None)
        self.thread_check_input.signals.error.connect(self.thread_error)
        self.thread_check_input.signals.result.connect()
        self.thread_check_input.signals.finished.connect()
        """
        
    
    
    
    def create_force_profile_thread(self):
        pass
        """
        self.thread_force_profile = Worker(generate_force_profile,
                                           kwargs=None)
        self.thread_force_profile.signals.error.connect(self.thread_error)
        self.thread_force_profile.signals.result.connect()
        self.thread_force_profile.signals.finished.connect()
        """
        
    
    def create_daq_thread(self):
        pass
        """
        self.thread_daq = Worker(daq,
                                 kwargs=None)
        self.thread_force_profile.signals.error.connect(self.thread_error)
        self.thread_force_profile.signals.result.connect()
        self.thread_force_profile.signals.finished.connect()
        """
        
    def thread_error(self, exctype, value, traceback):
        self.console_plot.append("Error!")
        
    def thread_complete(self):
        self.console_plot.append("Finished!")
        
        
    def generate_force_profile(self):
        
        #self.check_preferences()
        success = self.check_input()
        
        if success:
            for coil in self.coil_layout_dict:
                profile =  self.coil_layout_dict[coil].profile
                self.coil_layout_dict[coil].vals = []
                for textbox in self.coil_layout_dict[coil].textboxDict:
                    self.coil_layout_dict[coil].vals.append(self.coil_layout_dict[coil].textboxDict[textbox].val)
                vals = self.coil_layout_dict[coil].vals
                print("vals_________\n\n")
                print(f"{vals}")     
                
                
                if profile == "Ramp Profile":
                    # f0, df, k, drive_target, drive_current, time_idle, time_acc, time_ramp, time_rest, sampling_rate
                    
                    # Measure current drive
                    
                    
                    generate_ramp_profile(self.f0, self.df, self.k, vals, self.sampling_rate)
                    
                    #drive_current = np.average(daq_single(sampling_rate=1000, num_samples=10, input_channels=))
                    
                    
                elif profile == "Sine Profile":
                    pass
                
                
                elif profile == "Half-sine Profile":
                    # amp, freq, time_idle, time_rest, sampling_rate
                    

                    
                    generate_halfsine_profile(vals, self.sampling_rate)
                    
                    
                
                
                elif profile == "Upload Custom":
                    pass
                
                
            # get profile
            # get parameters
            
            
        




    def update_console(self):
        pass
        """
        if self.pipe_console.poll():
            while self.pipe_console.poll():
                msg = self.pipe_console.recv()
                self.console.append(msg)
        """            
                    
                    
        



    
    def stop_on_click(self):
        #self.pipe_signal.send(False) # Send signal to main.py to restart
        self.pipe_inputplotb.send(False) ######12/06/2023
        self.pipe_outputplotb.send(False) ######12/06/2023
        self.pipe_getdatab.send(False)


    def start_on_click(self):
        
        
        
        # Get 'save to file' and sampling rate
        #self.path = self.path_textbox.text()
        #self.db_env = self.db_textbox.text()
        
        #self.save = self.checkbox.isChecked()
        self.sampling_rate = self.textbox_srate.text()
        
        self.f0 = self.textbox_f0.text()
        self.df = self.textbox_df.text()
        self.k = self.textbox_k.text()
        
        
 
        
        
        self.generate_force_profile()
        
        
        # Send start signal to graphs
        """
        self.pipe_inputplotb.send(False) ######12/06/2023
        self.pipe_outputplotb.send(False) ######12/06/2023
        
        
        
        self.pipe_inputplotb.send(True) ######12/06/2023
        self.pipe_outputplotb.send(True) ######12/06/2023
        """

        # Get all parameters from preferences menu
        #self.textbox_ni_val = int(self.textbox_ni.text())
        #self.checkbox_ni_val = self.checkbox_ni.isChecked()
        #self.textbox_guiresolution_val = float(self.textbox_guiresolution.text())
        





        
        
        """
        # Read all textboxes and return the values
        for coil in self.coil_layout_dict:
            self.coil_layout_dict[coil].textboxValuesDict = {}
            for textbox in self.coil_layout_dict[coil].textboxDict:
                self.coil_layout_dict[coil].textboxValuesDict[str(coil) + " " + str(textbox.placeholderText())] = textbox.text()
        """
        """
        for coil in self.coil_layout_dict:
            for textbox in self.coil_layout_dict[coil].textboxDict:
                val = self.coil_layout_dict[coil].textboxDict[textbox].textbox.text()
        """    
        
        """
        # Check the validity of each input value
        success = self.check_input()
        
        # If valid, send input parameters through pipe_params to main.py
        # From there, force_profile.py will be called with the parameters
        
        if success:
            
            # Send preferences data
            self.pipe_buffer.send([self.textbox_ni_val,
                                   self.checkbox_ni_val,
                                   self.textbox_guiresolution_val,
                                   self.cameratimeout_val,
                                   self.cameracheckbox_val])#,
                                   #self.textbox_guirefresh_val])
            
            
            
            
            self.pipe_param.send(self.path)
            self.pipe_param.send(self.db_env)
            
            self.pipe_param.send(self.save)
            self.pipe_param.send(self.sampling_rate)
            
            self.pipe_param.send(self.f0)
            self.pipe_param.send(self.df)
            self.pipe_param.send(self.k)
            
            
            
            for coil in self.coil_layout_dict:
                # Send profile (ramp, sine, half-sine, custom)
                self.pipe_param.send(self.coil_layout_dict[coil].profile)
                
                
                # Send input parameters
                self.coil_layout_dict[coil].vals = []
                for textbox in self.coil_layout_dict[coil].textboxDict:
                    self.coil_layout_dict[coil].vals.append(self.coil_layout_dict[coil].textboxDict[textbox].val)
                
                
                #val = list(self.coil_layout_dict[coil].textboxValuesDict.values())
                vals = self.coil_layout_dict[coil].vals
                self.pipe_param.send(vals)

        else:
            print("Input parameters invalid")
            #for val in self.coil_layout_dict[coil].textboxDict:
             #   check_input(val)
            
        
        """
    
    
    def check_preferences(self):
        # Check preferences data
        try:
            self.textbox_ni_val = int(self.textbox_ni.text())
            self.checkbox_ni_val = self.checkbox_ni.isChecked()
        except:
            self.textbox_ni_val = 0
            self.checkbox_ni_val = False
            self.textbox_ni.setText("")
            self.checkbox_ni.setChecked(False)
    
        try:
            self.textbox_guiresolution_val = float(self.textbox_guiresolution.text())
        except:
            self.textbox_guiresolution_val = 20.0
            self.textbox_guiresolution.setText("100")
        
        
        try:
            self.cameratimeout_val = float(self.textbox_cameratimeout.text())
            self.cameracheckbox_val = self.checkbox_camera.isChecked()
        except:
            self.cameratimeout_val = 4
            self.cameracheckbox_val = True
        
        
    
    
    
    
    def check_input(self):
        error_code = 0
        error_message = []
        tot_times = []
        
        """
        # Check preferences data
        try:
            self.textbox_ni_val = int(self.textbox_ni.text())
            self.checkbox_ni_val = self.checkbox_ni.isChecked()
        except:
            self.textbox_ni_val = 0
            self.checkbox_ni_val = False
            self.textbox_ni.setText("")
            self.checkbox_ni.setChecked(False)

        try:
            self.textbox_guiresolution_val = float(self.textbox_guiresolution.text())
        except:
            self.textbox_guiresolution_val = 20.0
            self.textbox_guiresolution.setText("100")
        
        
        try:
            self.cameratimeout_val = float(self.textbox_cameratimeout.text())
            self.cameracheckbox_val = self.checkbox_camera.isChecked()
        except:
            self.cameratimeout_val = 4
            self.cameracheckbox_val = True
        
        
        """
        
        
        
        
        
        # Check if sampling rate is a float
        try:
            self.sampling_rate = float(self.sampling_rate)
            dt = 1.0 / self.sampling_rate
        except:
            print("Please enter a valid sampling rate.")
            error_message.append("Please enter a valid sampling rate.")
            error_code = 1
        
        
        # Check if sampling_rate is negative
        if error_code == 0:
            if self.sampling_rate < 0.0:
                print("Please enter a valid sampling rate.")
                error_message.append("Please enter a valid sampling rate.")
                error_code = 1
        
        
        # Check if f0 is a float
        try:
            self.f0 = float(self.f0)
        except:
            print("Please enter a valid frequency.")
            error_message.append("Please enter a valid frequency.")
            error_code = 1

        
        # Check if df is a float
        try:
            self.df = float(self.df)
        except:
            print("Please enter a valid line width.")
            error_message.append("Please enter a valid line width.")
            error_code = 1

        
        # Check if k is a float
        try:
            self.k = float(self.k)
        except:
            print("Please enter a valid spring constant.")
            error_message.append("Please enter a valid spring constant.")
            error_code = 1
        
        
        
        
        
        
        # Check if input is a custom profile
        if error_code == 0:
            for coil in self.coil_layout_dict:
                if "Custom" in self.coil_layout_dict[coil].profile:
                    for textbox in self.coil_layout_dict[coil].textboxDict:
                        val = self.coil_layout_dict[coil].textboxDict[textbox].textbox.text()
                        self.coil_layout_dict[coil].textboxDict[textbox].val = val
                else:
                    # Check if values are floats
                    if error_code == 0:
                        for textbox in self.coil_layout_dict[coil].textboxDict:
                            if error_code == 0:
                                val = self.coil_layout_dict[coil].textboxDict[textbox].textbox.text()
                                try:
                                    self.coil_layout_dict[coil].textboxDict[textbox].val = float(val)
                                except:
                                    print("Please enter a valid " + str(textbox))
                                    error_message.append("Please enter a valid " + str(textbox))
                                    error_code = 1
                                        
                                        
                    # Check if values are positive    
                    if error_code == 0:
                        for textbox in self.coil_layout_dict[coil].textboxDict:
                            if error_code == 0:
                                if "Velo" not in textbox and "Amp" not in textbox and "Phase" not in textbox and "Drive" not in textbox:  
                                    if self.coil_layout_dict[coil].textboxDict[textbox].val < 0.0:
                                        print(str(textbox) + " is negative")
                                        error_message.append(str(textbox) + " is negative")
                                        error_code = 1
                    
                    
                    
                    """
        # Check if coil times are the same and multiples of dt
        if error_code == 0:
            tot_times = []    
            for coil in self.coil_layout_dict:
                time_sum = 0
                for textbox in self.coil_layout_dict[coil].textboxDict:
                    val = self.coil_layout_dict[coil].textboxDict[textbox].val
                    dec = Decimal(str(dt)).as_tuple().exponent * -1
                    freq = val
                    t = 0
                    if "Freq" in textbox:
                        if self.coil_layout_dict[coil].profile == "Half-sine Profile":
                            t = Decimal("0.5") / Decimal(val)
                            if Decimal(str(t)) % Decimal(str(dt)) != 0:
                                freq = 1.0 / (2.0 * np.round((0.5 / val), dec))
                                self.coil_layout_dict[coil].textboxDict[textbox].textbox.setText(str(freq))
                                print("Half-sine frequency has been rounded to match the sampling rate")
                                print(f"freq: {freq}")
                                t = Decimal("0.5") / Decimal(str(freq))
                            
                        elif self.coil_layout_dict[coil].profile == "Sine Profile":
                            t = Decimal("1.0") / Decimal(val)
                            if Decimal(str(t)) % Decimal(str(dt)) != 0:
                                freq = 1.0 / (np.round((1.0 / val), dec))
                                self.coil_layout_dict[coil].textboxDict[textbox].textbox.setText(str(freq))
                                print("Half-sine frequency has been rounded to match the sampling rate")
                                print(f"freq: {freq}")
                                t = Decimal("1.0") / Decimal(str(freq))
                            
                            
                            
                    elif "Velo" not in textbox and "Amp" not in textbox and "Freq" not in textbox and "Phase" not in textbox:
                        if "Acc" in textbox:
                            t = val * 2.0
                        else:
                            t = val
                    t = float(t)
                    time_sum = time_sum + t
                tot_times.append(time_sum)
                    """
                    
                    # Check if coil times are the same and adjust accordingly
                    if error_code == 0:
                        time_sum = 0
                        t = 0
                        for textbox in self.coil_layout_dict[coil].textboxDict:
                            val = self.coil_layout_dict[coil].textboxDict[textbox].val
                            if "Freq" in textbox:
                                if self.coil_layout_dict[coil].profile == "Half-sine Profile":
                                    t = 0.5 / val
                                elif self.coil_layout_dict[coil].profile == "Sine Profile":
                                    t = 1.0 / val
                            elif "Velo" not in textbox and "Amp" not in textbox and "Freq" not in textbox and "Phase" not in textbox and "Drive" not in textbox:
                                if "Acc" in textbox:
                                    t = val * 2.0
                                else:
                                    t = val
                            t = float(t)
                            time_sum = time_sum + t
                        tot_times.append(time_sum)
                                
                            
                # Check if coil times are equal                
                res = all(t == tot_times[0] for t in tot_times)
                if not res:
                    print("The total coil times are not equal. The 'rest' times will be changed automatically")
                    print(str(tot_times))
                    #error_code = 1
                    
                    index = 0
                    # Evaluate difference between time and total time, add difference to current time rest
                    for coil in self.coil_layout_dict:
                        dif = max(tot_times) - tot_times[index]
                        if dif != 0.0:
                            for textbox in self.coil_layout_dict[coil].textboxDict:
                                if "Rest" in textbox:
                                    val = self.coil_layout_dict[coil].textboxDict[textbox].val
                                    rest = val + dif
                                    self.coil_layout_dict[coil].textboxDict[textbox].textbox.setText(str(rest))
                                    print(f"{coil} Rest time has been increased to equate the total times")
                                    #error_message.append("Rest time has been increased to equate the total times")
                        index = index + 1
                              
        
    
        if error_code == 1:
            success = False
            if len(error_message) > 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText(str(error_message[0]))
                msg.setWindowTitle("Error")
                msg.exec_()
        else:
            success = True
        return success

      



class GraphLayout(QVBoxLayout):
    def __init__(self, channelDict, parent=None, *args, **kwargs): #channelDict, pipe_input, pipe_plota, guirefresh, pipe_guirefresha,
        super().__init__(parent, *args, **kwargs)
        self.channelDict = channelDict
        """
        self.pipe_input = pipe_input
        self.channelDict = channelDict
        self.pipe_plota = pipe_plota
        self.guirefresh = guirefresh
        self.pipe_guirefresha = pipe_guirefresha
        """
        
        # Create a plot for each input channel
        for channel in self.channelDict:
            self.channelDict[channel].plot = pg.PlotWidget(title=self.channelDict[channel].name)
            self.channelDict[channel].plot.setLabel('left', 'Voltage (V)')
            self.channelDict[channel].plot.setLabel('bottom', 'Elapsed Time (s)')
            self.channelDict[channel].plot.addLegend()
            self.channelDict[channel].plot.data = []
            self.elapsed_time = []
            self.channelDict[channel].plot.line = self.channelDict[channel].plot.plot(self.elapsed_time,
                                                                                      self.channelDict[channel].plot.data)
            self.addWidget(self.channelDict[channel].plot, 1)
            
            # Annotation for the x and y coordinates
            self.channelDict[channel].label = pg.LabelItem()
            self.channelDict[channel].label.setParentItem(self.channelDict[channel].plot.getPlotItem())
            self.channelDict[channel].label.anchor(itemPos=(1,0), parentPos=(1,0), offset=(-10,10))
        
        
        self.on = False
        self.counter = 0
        
        
        
        self.timer_refresh = QTimer()
        self.timer_refresh.setInterval(100) #ms
        self.timer_refresh.timeout.connect(self.update_refresh_rate)
        self.timer_refresh.start()
        
        
        
        
        
        
        self.timer = QTimer()
        #self.timer.setInterval(self.guirefresh) #ms
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()
    
    
    
    
    
    def update_refresh_rate(self):
        pass
        """
        if self.pipe_guirefresha.poll():
            while self.pipe_guirefresha.poll():
                self.guirefresh = self.pipe_guirefresha.recv()
            try:
                self.guirefresh = float(self.guirefresh)
            except:
                pass
            self.timer.setInterval(self.guirefresh)
        """
    
    
    def update_plots(self):
        pass
        """
        if self.pipe_plota.poll():                 # If start/stop button pressed
            
            if not self.on:                        # If not already on, counter = 0
                self.counter = 0
            while self.pipe_plota.poll():          # Receive start/stop signal
                self.on = self.pipe_plota.recv()
        
        if self.on:
            # Receive data
            if self.pipe_input.poll():
                
                # Check if input is 'done' signal sent from 'manipulate_data' process from main.py
                data = self.pipe_input.recv()
                if data == False:
                    self.on = False
                else:
                    
                    # Clear all data if start button press just pressed
                    if self.counter == 0:
                        self.time_start = data[0]
                        self.elapsed_time = []
                        for channel in self.channelDict:
                            self.channelDict[channel].plot.data = []
                            self.channelDict[channel].plot.line.setData(self.elapsed_time, self.channelDict[channel].plot.data)
                            #self.channelDict[channel].plot.line.setData([5], [1])
                        self.counter = 1
                    elapsed_time = data[0] - self.time_start
                    self.elapsed_time.append(elapsed_time)
                    
                    
                    # Plot data
                    for channel in self.channelDict:
                        
                        time_now = time.time()
                        time_delay = time_now - data[0]
                        #print(str(time_delay))
                        
                        self.channelDict[channel].plot.data.append(data[self.channelDict[channel].index])
                        if len(self.elapsed_time) > 2500:
                            self.elapsed_time = self.elapsed_time[1:]
                        if len(self.channelDict[channel].plot.data) > 2500:
                            self.channelDict[channel].plot.data = self.channelDict[channel].plot.data[1:]
                        self.channelDict[channel].plot.line.setData(self.elapsed_time, self.channelDict[channel].plot.data)
                        
                        # Update label
                        self.channelDict[channel].label.setText(f"x: {elapsed_time:5.2f}, y: {data[self.channelDict[channel].index]:5.2f}")
                
        
        
        else:
            self.counter = 0
            if self.pipe_input.poll():
                while self.pipe_input.poll():
                    self.pipe_input.recv()
        
        
                    
        """


class Layout(QGridLayout):
    def __init__(self,
                 input_channelDict,
                # output_channelDict,
                 coil_dict,
                 parent=None,
                 *args,
                 **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.input_channelDict = input_channelDict
       # self.output_channelDict = output_channelDict
        self.coil_dict = coil_dict
        
        """
                 input_channelDict,
                 output_channelDict,
                 pipe_param,
                 pipe_input,
                 pipe_output,
                 pipe_signal,
                 pipe_console,
                 guirefresh,
                 pipe_guirefresha_output,
                 pipe_guirefresha_input,
                 textbox_ni,
                 checkbox_ni,
                 textbox_guiresolution,
                 #textbox_guirefresh,
                 pipe_buffer,
                 pipe_getdatab,
                 pipe_inputplota,
                 pipe_inputplotb,
                 pipe_outputplota,
                 pipe_outputplotb,
                 textbox_cameratimeout,
                 checkbox_camera,
        """
        
        """
        self.input_channelDict = input_channelDict
        self.output_channelDict = output_channelDict
        self.pipe_param = pipe_param
        self.pipe_signal = pipe_signal
        self.pipe_input = pipe_input
        self.pipe_output = pipe_output
        """
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        """
        self.pipe_console = pipe_console
        self.guirefresh = guirefresh
        self.pipe_guirefresha_output = pipe_guirefresha_output
        self.pipe_guirefresha_input = pipe_guirefresha_input
        self.pipe_getdatab = pipe_getdatab
        
        
        
        self.pipe_inputplota = pipe_inputplota
        self.pipe_inputplotb = pipe_inputplotb
        self.pipe_outputplota = pipe_outputplota
        self.pipe_outputplotb = pipe_outputplotb
        
        #self.pipe_inputplota, self.pipe_inputplotb = Pipe(duplex=False)
        #self.pipe_outputplota, self.pipe_outputplotb = Pipe(duplex=False)
        
        
        self.textbox_ni = textbox_ni
        self.checkbox_ni = checkbox_ni
        self.textbox_guiresolution = textbox_guiresolution
        #self.textbox_guirefresh = textbox_guirefresh
        self.pipe_buffer = pipe_buffer
        
        
        self.textbox_cameratimeout = textbox_cameratimeout
        self.checkbox_camera = checkbox_camera
        
        """
        
        path = "C:\\Users\\ultservi\\Desktop\\Elmy\\python-flying-balls\\"
        self.path_textbox = QLineEdit(f"{path}out\\")
        self.db_textbox = QLineEdit(f"{path}.env")
        

        self.console = QTextEdit()
        self.console.setStyleSheet("background-color:black; color:lightgray")
        
        
        layout_fsettings = FileSettingsLayout(self.checkbox, self.path_textbox, self.db_textbox)
        layout_ramp = RampSettingsLayout(self.coil_dict)
        """    
                                         self.pipe_param,
                                         self.pipe_signal,
                                         self.checkbox,
                                         self.path_textbox,
                                         self.db_textbox,
                                         self.console,
                                         self.pipe_console,
                                         self.pipe_outputplotb,
                                         self.pipe_inputplotb,
                                         self.textbox_ni,
                                         self.checkbox_ni,
                                         self.textbox_guiresolution,
                                         #self.textbox_guirefresh,
                                         self.pipe_buffer,
                                         self.pipe_getdatab,
                                         self.textbox_cameratimeout,
                                         self.checkbox_camera)
        """
        #layout_output = OutputGraphLayout(self.output_channelDict, self.pipe_output, self.pipe_outputplota)
        #layout_input = InputGraphLayout(self.input_channelDict, self.pipe_input, self.pipe_inputplota, self.guirefresh)


        #layout_output = GraphLayout(self.output_channelDict)#self.output_channelDict, self.pipe_output, self.pipe_outputplota, self.guirefresh, self.pipe_guirefresha_output)
        layout_output = GraphLayout(self.coil_dict)#self.output_channelDict, self.pipe_output, self.pipe_outputplota, self.guirefresh, self.pipe_guirefresha_output)
        layout_input = GraphLayout(self.input_channelDict)#self.input_channelDict, self.pipe_input, self.pipe_inputplota, self.guirefresh, self.pipe_guirefresha_input)
        




    #def __init__(self, channelDict, pipe_input, pipe_plota, guirefresh, pipe_guirefresha, parent=None, *args, **kwargs):


        self.addLayout(layout_fsettings, 0, 0, 1, 3)
        self.addLayout(layout_ramp, 1, 0, 1, 1)
        self.addLayout(layout_output, 1, 1, 1, 1)
        self.addLayout(layout_input, 1, 2, 1, 1)
        





class PreferencesTab(QWidget):
    def __init__(self):
        """
                 guirefresh,
                 pipe_guirefresh_output,
                 pipe_guirefresh_input,
                 textbox_ni,
                 checkbox_ni,
                 textbox_guiresolution,
                 textbox_guirefresh,
                 ##############################################################
                 checkbox_camera,
                 textbox_cameratimeout,
                 camera_button_connect,
                 camera_button_disconnect,
                 camera_button_start,
                 camera_button_stop):
        """
        super().__init__()
        """
        self.pipe_guirefresh_output = pipe_guirefresh_output
        self.pipe_guirefresh_input = pipe_guirefresh_input
        self.val_guirefresh = guirefresh
        #self.pipe_buffer = pipe_buffer
        self.textbox_ni = textbox_ni
        self.checkbox_ni = checkbox_ni
        self.textbox_guiresolution = textbox_guiresolution
        self.textbox_guirefresh = textbox_guirefresh
        
        
        self.checkbox_camera = checkbox_camera
        self.textbox_cameratimeout = textbox_cameratimeout
        self.camera_button_connect = camera_button_connect
        self.camera_button_disconnect = camera_button_disconnect
        self.camera_button_start = camera_button_start
        self.camera_button_stop = camera_button_stop
        """
        
        
        
        
        # Create a tab widget
        self.setWindowTitle("Preferences")
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        tabwidget = QTabWidget()
        
        
        # Create and populate the buffer page
        page_buffer = QWidget()
        layout_buffer = QGridLayout()
        page_buffer.setLayout(layout_buffer)
        
        #self.textbox_ni = QLineEdit(placeholderText="NIDAQmx buffer size per channel")
        label_ni = QLabel("NIDAQmx buffer size per channel")
        layout_buffer.addWidget(label_ni, 1, 0, 1, 1)
        layout_buffer.addWidget(self.textbox_ni, 1, 1, 1, 1)
        
        #self.checkbox_ni = QCheckBox()
        #self.checkbox_ni.setChecked(False)
        label_checkbox_ni = QLabel("Override automatic values?")
        layout_buffer.addWidget(label_checkbox_ni, 1, 2, 1, 1)
        layout_buffer.addWidget(self.checkbox_ni, 1, 3, 1, 1)
        
        #self.textbox_guiresolution = QLineEdit(placeholderText="GUI resolution (ms)")
        label_guiresolution = QLabel("GUI resolution (points per sec)")
        layout_buffer.addWidget(label_guiresolution, 2, 0, 1, 1)
        layout_buffer.addWidget(self.textbox_guiresolution, 2, 1, 1, 1)
        
        #self.textbox_guirefresh = QLineEdit(str(self.val_guirefresh), placeholderText="GUI refresh rate (ms)")
        label_guirefresh = QLabel("GUI refresh rate (ms)")
        layout_buffer.addWidget(label_guirefresh, 3, 0, 1, 1)
        layout_buffer.addWidget(self.textbox_guirefresh, 3, 1, 1, 1)

        
        
        # Add the buffer page to the tab widget
        tabwidget.addTab(page_buffer, "Buffer")
        
        
        ######################################################################
        
        # Create and populate the camera page
        page_camera = QWidget()
        layout_camera = QGridLayout()
        page_camera.setLayout(layout_camera)
        
        #self.textbox_ni = QLineEdit(placeholderText="NIDAQmx buffer size per channel")
        label_camera_use = QLabel("Record via the camera?")
        layout_camera.addWidget(label_camera_use, 1, 0, 1, 1)
        layout_camera.addWidget(self.checkbox_camera, 1, 1, 1, 1)
        
        
        label_camera_use = QLabel("Camera timeout (s)")
        layout_camera.addWidget(label_camera_use, 2, 0, 1, 1)
        layout_camera.addWidget(self.textbox_cameratimeout, 2, 1, 1, 1)
        
        
        #layout_camera.addWidget(self.textbox_ni, 1, 1, 1, 1)
        
        
        layout_camera.addWidget(self.camera_button_connect, 3, 0, 1, 1)
        layout_camera.addWidget(self.camera_button_disconnect, 3, 1, 1, 1)
        layout_camera.addWidget(self.camera_button_start, 3, 2, 1, 1)
        layout_camera.addWidget(self.camera_button_stop, 3, 3, 1, 1)
        
                 #checkbox_camera,
                # textbox_cameratimeout,
              #   camera_button_connect,
               #  camera_button_disconnect
        
        
        # Add the camera page to the tab widget
        tabwidget.addTab(page_camera, "Camera")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # Add the tab widget to the main layout
        layout_main.addWidget(tabwidget, 0, 0, 1, 6)
        
        # Add buttons to the tab widget
        button_buffer_ok = QPushButton('OK')
        button_buffer_cancel = QPushButton('Cancel')
        button_buffer_apply = QPushButton('Apply')
        
        button_buffer_ok.clicked.connect(self.click_okay)
        button_buffer_cancel.clicked.connect(self.click_cancel)
        button_buffer_apply.clicked.connect(self.click_apply)
        
        
        layout_main.addWidget(button_buffer_ok, 2, 3, 1, 1)
        layout_main.addWidget(button_buffer_cancel, 2, 4, 1, 1)
        layout_main.addWidget(button_buffer_apply, 2, 5, 1, 1)
        


    
    def click_okay(self):
        # Get values, then close
        self.val_ni = self.textbox_ni.text()
        self.val_ni_checkbox = self.checkbox_ni.isChecked()
        self.val_guiresolution = self.textbox_guiresolution.text()
        self.val_guirefresh = self.textbox_guirefresh.text()
        
        self.val_cameratimeout = self.textbox_cameratimeout.text()
        self.val_camera_checkbox = self.checkbox_camera.isChecked()
        
        # Pipe these somewhere
        print(f"{self.val_ni} {self.val_ni_checkbox} {self.val_guiresolution} {self.val_guirefresh}")
        print(f"{self.val_cameratimeout} {self.val_camera_checkbox}")
        self.pipe_guirefresh_output.send(self.val_guirefresh)
        self.pipe_guirefresh_input.send(self.val_guirefresh)
        
        #self.pipe_buffer.send([self.val_ni, self.val_ni_checkbox, self.val_guiresolution])
        
        self.hide()


    def click_cancel(self):
        # Reset textbox values and hide the preferences window
        self.textbox_guirefresh.setText(str(self.val_guirefresh))
        #self.textbox_guiresolution.setText(str(self.val_guiresolution))
        #self.textbox_ni.setText(str(self.val_ni))
        self.textbox_ni.setText("")
        #self.checkbox_ni.setChecked(self.val_ni_checkbox)
        self.hide()       
        
 

    def click_apply(self):
        # Get values
        self.val_ni = self.textbox_ni.text()
        self.val_ni_checkbox = self.checkbox_ni.isChecked()
        self.val_guiresolution = self.textbox_guiresolution.text()
        self.val_guirefresh = self.textbox_guirefresh.text()
        
        self.val_cameratimeout = self.textbox_cameratimeout.text()
        self.val_camera_checkbox = self.checkbox_camera.isChecked()
        
        # Pipe these somewhere
        print(f"{self.val_ni} {self.val_ni_checkbox} {self.val_guiresolution} {self.val_guirefresh}")
        print(f"{self.val_cameratimeout} {self.val_camera_checkbox}")
        self.pipe_guirefresh_output.send(self.val_guirefresh)
        self.pipe_guirefresh_input.send(self.val_guirefresh)
        
        #self.pipe_buffer.send([self.val_ni, self.val_ni_checkbox, self.val_guiresolution])
        
        
        
        
class InputChannel():
    def __init__(self, channel, name, pipe=Pipe(duplex=True)):
        self.channel = channel
        self.name = name
        self.pipe = pipe
"""
class OutputChannel():
    def __init__(self, channel, channel_measured, name, pipe=Pipe(duplex=True)):
        self.channel = channel
        self.channel_measured = channel_measured
        self.name = name
        self.pipe = pipe
"""
        

class MainWindow(QMainWindow):
    def __init__(self,
                 parent=None,
                 *args,
                 **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        
        self.title = "Flying Balls"
        self.icon = "../fig/icon.png"
        self.setGeometry(40, 40, 1200, 625)
        
        
        # Parameters for GUI refresh rate
        self.guirefresh = 10 #ms
        self.pipe_guirefresha_output, self.pipe_guirefreshb_output = Pipe(duplex=False)
        self.pipe_guirefresha_input, self.pipe_guirefreshb_input = Pipe(duplex=False)
        
        
        
        
        
        self.init_coils()
        self.init_channels()
        self.init_UI()
        self._createMenuBar()

        
   
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        """
                     input_channelDict,
                     output_channelDict,
                     pipe_param,
                     pipe_input,
                     pipe_output,
                     pipe_signal,
                     pipe_console,
                     pipe_buffer,
                     pipe_camb,
                     pipe_getdatab,
                     pipe_inputplota,
                     pipe_inputplotb,
                     pipe_outputplota,
                     pipe_outputplotb,
        """
        
        """        
        self.input_channelDict = input_channelDict
        self.output_channelDict = output_channelDict
        self.pipe_param = pipe_param
        self.pipe_signal = pipe_signal
        self.pipe_input = pipe_input
        self.pipe_output = pipe_output
        self.pipe_console = pipe_console
        self.pipe_buffer = pipe_buffer
        self.pipe_camb = pipe_camb
        self.pipe_getdatab = pipe_getdatab
        """
     
        
        
        """
        # Pipes for clearing the GUI
        self.pipe_inputplota = pipe_inputplota
        self.pipe_inputplotb = pipe_inputplotb
        self.pipe_outputplota = pipe_outputplota
        self.pipe_outputplotb = pipe_outputplotb
        """
        
        
        
        # Create all textboxes for the Preferences menu (Buffer)
        self.textbox_ni = QLineEdit(placeholderText="NIDAQmx buffer size per channel")
        self.checkbox_ni = QCheckBox()
        self.checkbox_ni.setChecked(False)
        self.textbox_guiresolution = QLineEdit(placeholderText="GUI resolution (points per sec)")
        self.textbox_guirefresh = QLineEdit(str(self.guirefresh), placeholderText="GUI refresh rate (ms)")
        
        
        
        
        # Create all textboxes for the Preferences menu (Camera)
        self.cameratimeout = 4.0 #sec
        self.checkbox_camera = QCheckBox()
        self.checkbox_camera.setChecked(True)
        self.textbox_cameratimeout = QLineEdit(str(self.cameratimeout), placeholderText="Camera timeout (sec)")
        self.camera_button_connect = QPushButton("Connect")
        self.camera_button_disconnect = QPushButton("Disconnect")
        self.camera_button_start = QPushButton("Start")
        self.camera_button_stop = QPushButton("Stop")
                
        
        
        self.camera_button_connect.clicked.connect(self.camera_connect_on_click)
        self.camera_button_disconnect.clicked.connect(self.camera_disconnect_on_click)
        self.camera_button_start.clicked.connect(self.camera_start_on_click)
        self.camera_button_stop.clicked.connect(self.camera_stop_on_click)
        
        
        
        
        
        
        # Create the preferences menu
        #self.menu_preferences = PreferencesTab()
        """
                                               self.guirefresh,
                                               self.pipe_guirefreshb_output,
                                               self.pipe_guirefreshb_input,
                                               self.textbox_ni,
                                               self.checkbox_ni,
                                               self.textbox_guiresolution,
                                               self.textbox_guirefresh,
                                               ###############################
                                               self.checkbox_camera,
                                               self.textbox_cameratimeout,
                                               self.camera_button_connect,
                                               self.camera_button_disconnect,
                                               self.camera_button_start,
                                               self.camera_button_stop)
        """
        
        
        
        

    
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        helpMenu = menuBar.addMenu("&Help")
        toolsMenu = menuBar.addMenu("&Tools")
        fileMenu.addAction("Ooga Booga")
        helpMenu.addAction("Documentation")
        #toolsMenu.addAction("Buffer Properties")

        self.preferencesAction = QAction(self)
        self.preferencesAction.setText("Preferences")
        self.preferencesAction.triggered.connect(self.preferences_on_click)
        toolsMenu.addAction(self.preferencesAction)
        


    def camera_connect_on_click(self):
        self.pipe_camb.send(False)
        self.pipe_camb.send(4)
#        self.pipe_cam_reconnectb.send(True)
 #       print("Trying to reconnect to the camera...")
        
    def camera_disconnect_on_click(self):
        self.pipe_camb.send(False)
        self.pipe_camb.send(3)
        


    def camera_start_on_click(self):
        self.pipe_camb.send(True)


    def camera_stop_on_click(self):
        self.pipe_camb.send(False)


    def preferences_on_click(self):
        # Show the preferences menu
        self.menu_preferences.show()
        
    
    
    
    
    
    
    
    def init_coils(self):
        coils = [("Dev1/ao3", "Dev1/ai3", "Lateral Coils\nao3/ai3"),
                 ("Dev1/ao1", "Dev1/ai0", "Longitudinal Coils\nao1/ai0")]
        self.coil_dict = {name: CoilChannel(channel=channel,
                                                    channel_measured=channel_measured,
                                                    name=name) for channel,
                                                                   channel_measured,
                                                                   name in coils}
        
       
        
        
        
        
        
        
        print(str(self.coil_dict))
        print("=========================\n==========================")
        
        """
        self.coil_layout_dict = {coil: CoilProfileLayout(coil=coil) for coil in self.coil_names}
        self.coil_box_dict = {coil: QGroupBox(coil) for coil in self.coil_names}
        
        for coil in self.coil_names:
            self.coil_box_dict[coil].setLayout(self.coil_layout_dict[coil])
            self.coil_box_dict[coil].setMaximumWidth(250)
            self.addWidget(self.coil_box_dict[coil])
        """
    
    
          
    def init_channels(self):
        # Define all input channels
        #                   Channel      name      
        input_channels = [("Dev1/ai17", "ai17"),
                          ("Dev1/ai18", "ai18"),
                          ("Dev1/ai19", "ai19"),
                          ("Dev1/ai20", "ai20"),
                          ("Dev1/ai21", "ai21"),
                          ("Dev1/ai6", "ai6"),
                          ("Dev1/ai7", "ai7")]

        # Define all output channels
#        output_channels = [("Dev1/ao3", "Dev1/ai3", "Lateral Coils\nao3/ai3"),
 #                          ("Dev1/ao1", "Dev1/ai0", "Longitudinal Coils\nao1/ai0")]
        
        self.input_channelDict = {channel: InputChannel(channel=channel, name=name) for channel, name in input_channels}
  #      self.output_channelDict = {channel: OutputChannel(channel=channel, channel_measured=channel_measured, name=name) for channel, channel_measured, name in output_channels}
      
        
        
       
    
    
    def init_UI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon))
        #grid_layout = Layout(self.input_channelDict, self.output_channelDict, self.coil_dict)
        grid_layout = Layout(self.input_channelDict, self.coil_dict)
        """
                             self.input_channelDict,
                             self.output_channelDict,
                             self.pipe_param,
                             self.pipe_input,
                             self.pipe_output,
                             self.pipe_signal,
                             self.pipe_console,
                             self.guirefresh,
                             self.pipe_guirefresha_output,
                             self.pipe_guirefresha_input,
                             self.textbox_ni,
                             self.checkbox_ni,
                             self.textbox_guiresolution,
                             #self.textbox_guirefresh,
                             self.pipe_buffer,
                             self.pipe_getdatab,
                             self.pipe_inputplota,
                             self.pipe_inputplotb,
                             self.pipe_outputplota,
                             self.pipe_outputplotb,
                             self.textbox_cameratimeout,
                             self.checkbox_camera)
        """
        widget = QWidget()
        widget.setLayout(grid_layout)
        self.setCentralWidget(widget)
    #    self.createMenuBar
        #self.show()
        



class MovieSplashScreen(QSplashScreen):

	def __init__(self, pathToGIF):
		self.movie = QMovie(pathToGIF)
		self.movie.jumpToFrame(0)
		pixmap = QPixmap(self.movie.frameRect().size())
		QSplashScreen.__init__(self, pixmap)
		self.movie.frameChanged.connect(self.repaint)

	def showEvent(self, event):
		self.movie.start()

	def hideEvent(self, event):
		self.movie.stop()

	def paintEvent(self, event):
		painter = QPainter(self)
		pixmap = self.movie.currentPixmap()
		self.setMask(pixmap.mask())
		painter.drawPixmap(0, 0, pixmap)



        

def start_gui():
    """
              input_channelDict,
              output_channelDict,
              pipe_param,
              pipe_input,
              pipe_output,
              pipe_signal,
              pipe_console,
              pipe_buffer,
              pipe_camb,
              pipe_getdatab,
              pipe_inputplota,
              pipe_inputplotb,
              pipe_outputplota,
              pipe_outputplotb):
    """
    # Splash screen
    app = QApplication(sys.argv)
    pathToGIF = "../fig/loading/loading.gif"
    splash = MovieSplashScreen(pathToGIF)
    splash.show()

    def showWindow():        
        splash.close()
        ex.show()

    QTimer.singleShot(1000, showWindow)
    ex = MainWindow()
    """
                    input_channelDict,
                    output_channelDict,
                    pipe_param,
                    pipe_input,
                    pipe_output,
                    pipe_signal,
                    pipe_console,
                    pipe_buffer,
                    pipe_camb,
                    pipe_getdatab,
                    pipe_inputplota,
                    pipe_inputplotb,
                    pipe_outputplota,
                    pipe_outputplotb)
    """
    app.exec_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    start_gui()
    
    
    
    
    
    
    
    
    
    