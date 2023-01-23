
from decimal import Decimal
import sys
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QFrame,
                             QLabel,
                             QWidget,
                             QPushButton,
                             QGroupBox,
                             QCheckBox,
                             QComboBox,
                             QAction,
                             QLineEdit,
                             QMessageBox,
                             QHBoxLayout,
                             QVBoxLayout,
                             QGridLayout,
                             QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
import pyqtgraph as pg


import multiprocessing.connection
from multiprocessing import Process, Pipe



import time


class FileSettingsLayout(QGridLayout):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        
        #================================================================
        # Layout fsettings
        # Make default value be read from file
        # If path doesn't exist, make it
        
        
        path = "C:\\Users\\ultservi\\Desktop\\FlyingBalls"
        self.addWidget(QLineEdit(path), 0, 0, 1, 1)
        self.addWidget(QLabel("Path"), 1, 0, 1, 1)
       
        self.addWidget(QLineEdit(), 0, 1, 1, 1)
        self.addWidget(QLabel("DB Environment"), 1, 1, 1, 1)
        
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.checked)
        
        self.addWidget(self.checkbox, 0, 2, 1, 1)
        self.addWidget(QLabel("Save to File?"), 1, 2, 1, 1)
        
        
    def checked(self):
        val = self.checkbox.isChecked()
        if val:
            print("Checked")
        else:
            print("Not checked")


class CoilLayout(QGridLayout):
    def __init__(self, coil, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.coil = coil
        self.make_layout()
        
        

    def make_layout(self):
        self.define_combo_box()
        self.addWidget(self.combo_box, 0, 0, 1, 1)
        self.make_textboxes(self.combo_box_list[0])
        
        

    def define_combo_box(self):
        self.combo_box = QComboBox()
        self.combo_box_list = ["Ramp Profile", "Sine Profile", "Half-sine Profile", "Upload Custom"]
        for item in self.combo_box_list:
            self.combo_box.addItem(item)
        self.combo_box.activated[str].connect(self.select_profile)
    
    def select_profile(self):
        content = self.combo_box.currentText()
        self.make_textboxes(content)
        
    def make_textboxes(self, content):
        # Destroy all existing textboxes
        for i in reversed(range(self.count())):
            if i>0:
                self.itemAt(i).widget().setParent(None)
        
        
        self.content = content
        if content == self.combo_box_list[0]:
            # Make content for "Ramp Profile"
            self.labelDict = {}
            self.labelDict[QLabel("Velocity\n(mm/s)")] = [1, 1, 1, 1]
            self.labelDict[QLabel("Time Idle\n(s)")] = [3, 0, 1, 1]
            self.labelDict[QLabel("Time Acc\n(s)")] = [3, 1, 1, 1]
            self.labelDict[QLabel("Time Ramp\n(s)")] = [5, 0, 1, 1]
            self.labelDict[QLabel("Time Rest\n(s)")] = [5, 1, 1, 1]
            
            self.textboxDict = {}
            self.textboxDict[QLineEdit(placeholderText="Velocity")] = [0, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Idle")] = [2, 0, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Acc")] = [2, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Ramp")] = [4, 0, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Rest")] = [4, 1, 1, 1]
            
            
            
        elif content == self.combo_box_list[1]:
            # Make content for Sine Profile
            self.labelDict = {}
            self.labelDict[QLabel("Amplitude\n(V)")] = [1, 1, 1, 1]
            self.labelDict[QLabel("Frequency\n(Hz)")] = [3, 0, 1, 1]
            self.labelDict[QLabel("Phase\n(deg)")] = [3, 1, 1, 1]
            
            self.textboxDict = {}
            self.textboxDict[QLineEdit(placeholderText="Amp")] = [0, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Freq")] = [2, 0, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Phase")] = [2, 1, 1, 1]
            
            
            
        elif content == self.combo_box_list[2]:
            # Make content for Half Sine Profile
            self.labelDict = {}
            self.labelDict[QLabel("Amplitude\n(V)")] = [1, 1, 1, 1]
            self.labelDict[QLabel("Frequency\n(Hz)")] = [3, 0, 1, 1]
            self.labelDict[QLabel("Time Idle\n(s)")] = [3, 1, 1, 1]
            self.labelDict[QLabel("Time Rest\n(s)")] = [5, 0, 1, 1]
            
            self.textboxDict = {}
            self.textboxDict[QLineEdit(placeholderText="Amp")] = [0, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Freq")] = [2, 0, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Idle")] = [2, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Rest")] = [4, 0, 1, 1]        
                
                
                
        elif content == self.combo_box_list[3]:
            # Make content for Custom Profile
            self.labelDict = {}
            self.labelDict[QLabel("Directory")] = [3, 0, 1, 1]
            
            self.textboxDict = {}
            self.textboxDict[QLineEdit(placeholderText="Directory")] = [2, 0, 1, 1]  



        # Add the labels and textboxes
        for label in self.labelDict:
            a, b, c, d = self.labelDict[label]
            self.addWidget(label, a, b, c, d)
      
        for textbox in self.textboxDict:
            a, b, c, d = self.textboxDict[textbox]
            self.addWidget(textbox, a, b, c, d)
                         
            
        

class RampSettingsLayout(QVBoxLayout):
    def __init__(self, pipe_param, signal_start, pipe_signal, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #============================================================
        # Layout of Ramp Settings
        # 
        # RampSettingsLayout = Parent
        # QGroupBox = Child
        # layout.addWidget(Widgets)
        # QGroupBox.setLayout(layout)
        
        self.pipe_param = pipe_param
        self.signal_start = signal_start
        self.pipe_signal = pipe_signal


        
        self.coil_names = ["Lateral Coils", "Longitudinal Coils"]
        self.coil_layout_dict = {coil: CoilLayout(coil=coil) for coil in self.coil_names}
        self.coil_box_dict = {coil: QGroupBox(coil) for coil in self.coil_names}
        
        for coil in self.coil_names:
            self.coil_box_dict[coil].setLayout(self.coil_layout_dict[coil])
            self.coil_box_dict[coil].setMaximumWidth(250)
            self.addWidget(self.coil_box_dict[coil])
        
        
        
        layout_start = QGridLayout()
        
        
        self.textbox_srate = QLineEdit(placeholderText="Sampling Rate")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.clicked.connect(self.start_on_click)
        self.stop_button.clicked.connect(self.stop_on_click)
    
        layout_start.addWidget(self.textbox_srate)
        layout_start.addWidget(QLabel("Sampling Rate\n(Hz)"))
        
        layout_start.addWidget(self.start_button)
        layout_start.addWidget(self.stop_button)
       
  
        
        box_start = QGroupBox()
        box_start.setLayout(layout_start)
        box_start.setMaximumWidth(250)
        self.addWidget(box_start)

    
    def stop_on_click(self):
        self.signal_start.signal = False # Tell GUI plot to stop
        self.pipe_signal.send(False) # Send signal to main.py to restart


    def start_on_click(self):
        # Send start signal to graphs
        self.signal_start.signal = True

        # Get sampling rate
        self.sampling_rate = self.textbox_srate.text()
        
        # Read all textboxes and return the values
        for coil in self.coil_layout_dict:
            self.coil_layout_dict[coil].textboxValuesDict = {}
            for textbox in self.coil_layout_dict[coil].textboxDict:
                self.coil_layout_dict[coil].textboxValuesDict[str(coil) + " " + str(textbox.placeholderText())] = textbox.text()
        
        
        # Check the validity of each input value
        success = self.check_input()
        
        # If valid, send input parameters through pipe_params to main.py
        # From there, force_profile.py will be called with the parameters
        if success:
            self.pipe_param.send(self.sampling_rate)
            for coil in self.coil_layout_dict:
                # Send profile (ramp, sine, half-sine, custom)
                self.pipe_param.send(self.coil_layout_dict[coil].content)
                
                
                # Send input parameters
                val = list(self.coil_layout_dict[coil].textboxValuesDict.values())
                self.pipe_param.send(val)
                
                

        else:
            print("Input parameters invalid")
            #for val in self.coil_layout_dict[coil].textboxDict:
             #   check_input(val)
            
        
        
    def check_input(self):
        # Modulo, whether via % of math.fmod() is completely broken
        # Decimal(str()) % Decimal(str()) offers a solution, even if clunky
        # Nota bene, this does not work with math.fmod(); only %
        
        error_code = 0
        error_message = []
        
        
        
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
              
        
        
        # Check if values are floats
        if error_code == 0:
            for coil in self.coil_layout_dict:
                for textbox in self.coil_layout_dict[coil].textboxValuesDict:
                    if error_code == 0:
                        val = self.coil_layout_dict[coil].textboxValuesDict[textbox]
                        try:
                            self.coil_layout_dict[coil].textboxValuesDict[textbox] = float(val)
                        except:
                            print("Please enter a valid " + str(textbox))
                            error_message.append("Please enter a valid " + str(textbox))
                            error_code = 1
                    
        
        
        # Check if values are positive    
        if error_code == 0:
            for coil in self.coil_layout_dict:
                for textbox in self.coil_layout_dict[coil].textboxValuesDict:
                    if error_code == 0:
                        val = self.coil_layout_dict[coil].textboxValuesDict[textbox]
                        if "Velo" not in textbox and "Amp" not in textbox and "Phase" not in textbox:  
                            if val < 0.0:
                                print(str(textbox) + " is negative")
                                error_message.append(str(textbox) + " is negative")
                                error_code = 1
                      
                        
        # Check if coil times are the same
        if error_code == 0:
            tot_times = []
            for coil in self.coil_layout_dict:
                time_sum = 0
                for textbox in self.coil_layout_dict[coil].textboxValuesDict:
                    
                    if "Freq" in textbox:
                        #Work out associated time
                        # This depends on sine vs half-sine
                        
                        val = self.coil_layout_dict[coil].textboxValuesDict[textbox]
                        if self.coil_layout_dict[coil].content == "Half-sine Profile":
                            val = 0.5 / val
                            time_sum = time_sum + val
                            
                        elif self.coil_layout_dict[coil].content == "Sine Profile":
                            val = 1.0 / val
                            time_sum = time_sum + val
                            
                    
                    
                    
                    if "Velo" not in textbox and "Amp" not in textbox and "Freq" not in textbox and "Phase" not in textbox:
                            print("========")
                            print(str(textbox))
                        
                            val = self.coil_layout_dict[coil].textboxValuesDict[textbox]
                            if "Acc" in textbox:
                                val = val * 2.0
                            time_sum = time_sum + val
                tot_times.append(time_sum)
            
            res = all(t == tot_times[0] for t in tot_times)
            if not res:
                print("The total coil times are not equal. Consider changing the 'rest' times")
                print(str(tot_times))
                error_message.append("The total coil times are not equal. Consider changing the 'rest' times")
                error_code = 1
                
            
        # Check if times are compatible with the sampling rate
        if error_code == 0:
            for coil in self.coil_layout_dict:
                for textbox in self.coil_layout_dict[coil].textboxValuesDict:
                    if "Velocity" not in textbox:
                        val = self.coil_layout_dict[coil].textboxValuesDict[textbox]
                        try:
                            if Decimal(str(val)) % Decimal(str(dt)) != 0:
                                print(str(textbox) + " is not a multiple of dt")
                                error_message.append(str(textbox) + " is not a multiple of dt")
                                error_code = 1
                        except:
                            print("Please enter a valid " + str(textbox))
                            error_message.append("Please enter a valid " + str(textbox))
                            error_code = 1
                        
                        
    
        if error_code == 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
#            msg.setInformativeText(str(error_message))
            msg.setInformativeText(str(error_message[0]))
            msg.setWindowTitle("Error")
            msg.exec_()
            success = False
        else:
            success = True
        return success

                        
        
class OutputGraphLayout(QVBoxLayout):
    def __init__(self, output_channelDict, pipe_output, signal_start, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.output_channelDict = output_channelDict
        self.pipe_output = pipe_output
        self.signal_start = signal_start

        # Create a plot for each input channel
        for channel in self.output_channelDict:
            self.output_channelDict[channel].plot = pg.PlotWidget(title=self.output_channelDict[channel].name)
            self.output_channelDict[channel].plot.setLabel('left', 'Voltage (V)')
            self.output_channelDict[channel].plot.setLabel('bottom', 'Elapsed Time (s)')
            self.output_channelDict[channel].plot.addLegend()
            self.output_channelDict[channel].plot.data = []
            self.elapsed_time = []
            self.output_channelDict[channel].plot.line = self.output_channelDict[channel].plot.plot(self.elapsed_time,
                                                                                                    self.output_channelDict[channel].plot.data)
                                                                                                    #name=self.output_channelDict[channel].name)
            self.addWidget(self.output_channelDict[channel].plot, 1)
            
            
        
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(10) # 5 ms = 200 refreshes per sec
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()
    
    
    
    def update_plots(self):
        if not self.signal_start.signal:
            self.counter = 0
        
        else:
            if self.pipe_output.poll():
                data = self.pipe_output.recv()
                # Clear all data on start button press
                if self.counter == 0:
                    self.time_start = data[0]
                    self.elapsed_time = []
                    for channel in self.output_channelDict:
                        self.output_channelDict[channel].plot.data = []
                        self.output_channelDict[channel].plot.line.setData(self.elapsed_time, self.output_channelDict[channel].plot.data)
                    self.counter = 1
                elapsed_time = data[0] - self.time_start
                self.elapsed_time.append(elapsed_time)
                
                
                for channel in self.output_channelDict:
                    self.output_channelDict[channel].plot.data.append(data[self.output_channelDict[channel].index])
                    
                    
                    if len(self.elapsed_time) > 200:
                        self.elapsed_time = self.elapsed_time[1:]
                    
                    if len(self.output_channelDict[channel].plot.data) > 200:
                        self.output_channelDict[channel].plot.data = self.output_channelDict[channel].plot.data[1:]
                    self.output_channelDict[channel].plot.line.setData(self.elapsed_time, self.output_channelDict[channel].plot.data)
                    
                    # Update label
                    # This probably isn't the best way to do this
                    self.output_channelDict[channel].plot.setLabel('top', f"x: {elapsed_time:5.2f}, y: {data[self.output_channelDict[channel].index]:5.2f}")

                    

class InputGraphLayout(QVBoxLayout):
    def __init__(self, input_channelDict, pipe_input, signal_start, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pipe_input = pipe_input
        self.signal_start = signal_start
        self.input_channelDict = input_channelDict
        
        
        # Create a plot for each input channel
        for channel in self.input_channelDict:
            self.input_channelDict[channel].plot = pg.PlotWidget(title=self.input_channelDict[channel].name)
            self.input_channelDict[channel].plot.setLabel('left', 'Voltage (V)')
            self.input_channelDict[channel].plot.setLabel('bottom', 'Elapsed Time (s)')
            self.input_channelDict[channel].plot.addLegend()
            self.input_channelDict[channel].plot.data = []
            self.elapsed_time = []
            self.input_channelDict[channel].plot.line = self.input_channelDict[channel].plot.plot(self.elapsed_time,
                                                                                      self.input_channelDict[channel].plot.data)
            self.addWidget(self.input_channelDict[channel].plot, 1)
            
        
        
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(10) # 5 ms = 200 refreshes per sec
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()
    
    
    
    def update_plots(self):
        if not self.signal_start.signal:
            self.counter = 0
        
        else:
            if self.pipe_input.poll():
                data = self.pipe_input.recv()
                # Clear all data on start button press
                if self.counter == 0:
                    self.time_start = data[0]
                    self.elapsed_time = []
                    for channel in self.input_channelDict:
                        self.input_channelDict[channel].plot.data = []
                        self.input_channelDict[channel].plot.line.setData(self.elapsed_time, self.input_channelDict[channel].plot.data)
                    self.counter = 1
                elapsed_time = data[0] - self.time_start
                self.elapsed_time.append(elapsed_time)
        
                
                for channel in self.input_channelDict:
                    self.input_channelDict[channel].plot.data.append(data[self.input_channelDict[channel].index])
                    
                    if len(self.elapsed_time) > 200:
                        self.elapsed_time = self.elapsed_time[1:]
                    
                    if len(self.input_channelDict[channel].plot.data) > 200:
                        self.input_channelDict[channel].plot.data = self.input_channelDict[channel].plot.data[1:]
                    self.input_channelDict[channel].plot.line.setData(self.elapsed_time, self.input_channelDict[channel].plot.data)
        
                    # Update label
                    # This probably isn't the best way to do this
                    self.input_channelDict[channel].plot.setLabel('top', f"x: {elapsed_time:5.2f}, y: {data[self.input_channelDict[channel].index]:5.2f}")

               
class SignalStart():
    def __init__(self, signal=False):
        self.signal = signal        
        
        


class Layout(QGridLayout):
    def __init__(self, input_channelDict, output_channelDict, pipe_param, pipe_input, pipe_output, signal_start, pipe_signal, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.input_channelDict = input_channelDict
        self.output_channelDict = output_channelDict
        self.pipe_param = pipe_param
        self.signal_start = signal_start
        self.pipe_signal = pipe_signal
        self.pipe_input = pipe_input
        self.pipe_output = pipe_output
        
        
        layout_fsettings = FileSettingsLayout()
        layout_ramp = RampSettingsLayout(self.pipe_param, self.signal_start, self.pipe_signal)
        layout_output = OutputGraphLayout(self.output_channelDict, self.pipe_output, self.signal_start)
        layout_input = InputGraphLayout(self.input_channelDict, self.pipe_input, self.signal_start)
        
                
        
        self.addLayout(layout_fsettings, 0, 0, 1, 3)
        self.addLayout(layout_ramp, 1, 0, 1, 1)
        self.addLayout(layout_output, 1, 1, 1, 1)
        self.addLayout(layout_input, 1, 2, 1, 1)
        



class MainWindow(QMainWindow):
    def __init__(self, input_channelDict, output_channelDict, pipe_param, pipe_input, pipe_output, signal_start, pipe_signal, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.input_channelDict = input_channelDict
        self.output_channelDict = output_channelDict
        self.pipe_param = pipe_param
        self.signal_start = signal_start
        self.pipe_signal = pipe_signal
        self.pipe_input = pipe_input
        self.pipe_output = pipe_output
        self.title = "GUI Demo"
        self.setGeometry(40, 40, 1200, 625)
        self.initUI()
    
    
    def initUI(self):
        self.setWindowTitle(self.title)
        grid_layout = Layout(self.input_channelDict, self.output_channelDict, self.pipe_param, self.pipe_input, self.pipe_output, self.signal_start, self.pipe_signal)        
        widget = QWidget()
        widget.setLayout(grid_layout)
        self.setCentralWidget(widget)
        self.show()
        
        

def start_gui(input_channelDict, output_channelDict, pipe_param, pipe_input, pipe_output, signal_start, pipe_signal):
    app = QApplication(sys.argv)
    ex = MainWindow(input_channelDict, output_channelDict, pipe_param, pipe_input, pipe_output, signal_start, pipe_signal)
    sys.exit(app.exec_())

if __name__ == '__main__':
    start_gui()
