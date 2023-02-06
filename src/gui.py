# -*- coding: utf-8 -*-

# Import libraries
from decimal import *
getcontext().prec = 10
import numpy as np
import sys
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QLabel,
                             QWidget,
                             QPushButton,
                             QGroupBox,
                             QCheckBox,
                             QComboBox,
                             QLineEdit,
                             QMessageBox,
                             QVBoxLayout,
                             QGridLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import pyqtgraph as pg





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
        


class TextBox():
    def __init__(self, placeholder, loc, label_text, label_loc, parent=None, *args, **kwargs):
        self.placeholder = placeholder
        self.loc = loc
        self.label_text = label_text
        self.label_loc = label_loc
        
        self.textbox = QLineEdit(placeholderText=str(placeholder))
        self.label = QLabel(str(label_text))
        
        
        

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
        
        
        # Make content for "Ramp Profile"
        if content == self.combo_box_list[0]:
            textbox_placeholders = ["Drive", "Idle", "Acc", "Ramp", "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1],
                            [4, 1, 1, 1]]
            textbox_labels = ["Drive\n(V)",
                              "Time Idle\n(s)",
                              "Time Acc\n(s)",
                              "Time Ramp\n(s)",
                              "Time Rest\n(s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1],
                                 [5, 1, 1, 1]]
        
        
        # Make content for Sine Profile
        elif content == self.combo_box_list[1]:
            textbox_placeholders = ["Amplitude", "Freq", "Phase"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1]]
            textbox_labels = ["Amplitude\n(V)",
                              "Frequency\n(Hz)",
                              "Phase\n(deg)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1]]
        
        
        # Make content for Sine Profile
        elif content == self.combo_box_list[2]:
            textbox_placeholders = ["Amplitude", "Freq", "Idle", "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1]]
            textbox_labels = ["Amplitude\n(V)",
                              "Frequency\n(Hz)",
                              "Time Idle\n(s)",
                              "Time Rest\n(s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1]]
        
        
        # Make content for Custom Profile
        elif content == self.combo_box_list[3]:
            textbox_placeholders = ["Directory"]
            textbox_locs = [[2, 0, 1, 1]]
            textbox_labels = ["Directory"]
            textbox_labellocs = [[3, 0, 1, 1]]
            
            
                
        self.textboxDict = {}
        for i in range(len(textbox_placeholders)):
            self.textboxDict[textbox_placeholders[i]] = TextBox(
                                                    textbox_placeholders[i],
                                                    textbox_locs[i],
                                                    textbox_labels[i],
                                                    textbox_labellocs[i])


        # Add the labels and textboxes
        for textbox in self.textboxDict:
            a, b, c, d = self.textboxDict[textbox].loc
            self.addWidget(self.textboxDict[textbox].textbox, a, b, c, d)
            
            a, b, c, d = self.textboxDict[textbox].label_loc
            self.addWidget(self.textboxDict[textbox].label, a, b, c, d)
            
        

class RampSettingsLayout(QVBoxLayout):
    def __init__(self, pipe_param, signal_start, pipe_signal, checkbox, path_textbox, db_textbox, parent=None, *args, **kwargs):
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
        self.checkbox = checkbox
        self.path_textbox = path_textbox
        self.db_textbox = db_textbox


        
        self.coil_names = ["Lateral Coils", "Longitudinal Coils"]
        self.coil_layout_dict = {coil: CoilLayout(coil=coil) for coil in self.coil_names}
        self.coil_box_dict = {coil: QGroupBox(coil) for coil in self.coil_names}
        
        for coil in self.coil_names:
            self.coil_box_dict[coil].setLayout(self.coil_layout_dict[coil])
            self.coil_box_dict[coil].setMaximumWidth(250)
            self.addWidget(self.coil_box_dict[coil])
        
        
        
        layout_start = QGridLayout()
        
        
        self.textbox_srate = QLineEdit(placeholderText="Sampling Rate")
        self.textbox_f0 = QLineEdit("7.300", placeholderText="Frequency")
        self.textbox_df = QLineEdit("0.090", placeholderText="Line Width")
        self.textbox_k = QLineEdit("0.465", placeholderText="Spring Constant")
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

        # Get 'save to file' and sampling rate
        self.path = self.path_textbox.text()
        self.db_env = self.db_textbox.text()
        
        self.save = self.checkbox.isChecked()
        self.sampling_rate = self.textbox_srate.text()
        
        self.f0 = self.textbox_f0.text()
        self.df = self.textbox_df.text()
        self.k = self.textbox_k.text()
        
        
        
        
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
        
        
        # Check the validity of each input value
        success = self.check_input()
        
        # If valid, send input parameters through pipe_params to main.py
        # From there, force_profile.py will be called with the parameters
        if success:
            
            
            self.pipe_param.send(self.path)
            self.pipe_param.send(self.db_env)
            
            self.pipe_param.send(self.save)
            self.pipe_param.send(self.sampling_rate)
            
            self.pipe_param.send(self.f0)
            self.pipe_param.send(self.df)
            self.pipe_param.send(self.k)
            
            
            
            for coil in self.coil_layout_dict:
                # Send profile (ramp, sine, half-sine, custom)
                self.pipe_param.send(self.coil_layout_dict[coil].content)
                
                
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
            
        
        
    def check_input(self):
        error_code = 0
        error_message = []
        tot_times = []
        
        
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
                if "Custom" in self.coil_layout_dict[coil].content:
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
                        if self.coil_layout_dict[coil].content == "Half-sine Profile":
                            t = Decimal("0.5") / Decimal(val)
                            if Decimal(str(t)) % Decimal(str(dt)) != 0:
                                freq = 1.0 / (2.0 * np.round((0.5 / val), dec))
                                self.coil_layout_dict[coil].textboxDict[textbox].textbox.setText(str(freq))
                                print("Half-sine frequency has been rounded to match the sampling rate")
                                print(f"freq: {freq}")
                                t = Decimal("0.5") / Decimal(str(freq))
                            
                        elif self.coil_layout_dict[coil].content == "Sine Profile":
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
                                if self.coil_layout_dict[coil].content == "Half-sine Profile":
                                    t = 0.5 / val
                                elif self.coil_layout_dict[coil].content == "Sine Profile":
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
            
            # Annotation for the x and y coordinates
            self.output_channelDict[channel].label = pg.LabelItem()
            self.output_channelDict[channel].label.setParentItem(self.output_channelDict[channel].plot.getPlotItem())
            self.output_channelDict[channel].label.anchor(itemPos=(1,0), parentPos=(1,0), offset=(-10,10))
        
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(10) #ms
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()
    
    
    
    def update_plots(self):
        if not self.signal_start.signal:
            self.counter = 0
            if self.pipe_output.poll():
                while self.pipe_output.poll():
                    self.pipe_output.recv()
        
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
                    
                    
                    if len(self.elapsed_time) > 2500:
                        self.elapsed_time = self.elapsed_time[1:]
                    
                    if len(self.output_channelDict[channel].plot.data) > 2500:
                        self.output_channelDict[channel].plot.data = self.output_channelDict[channel].plot.data[1:]
                    self.output_channelDict[channel].plot.line.setData(self.elapsed_time, self.output_channelDict[channel].plot.data)
                    
                    # Update label
                    self.output_channelDict[channel].label.setText(f"x: {elapsed_time:5.2f}, y: {data[self.output_channelDict[channel].index]:5.2f}")
                    

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
            
            # Annotation for the x and y coordinates
            self.input_channelDict[channel].label = pg.LabelItem()
            self.input_channelDict[channel].label.setParentItem(self.input_channelDict[channel].plot.getPlotItem())
            self.input_channelDict[channel].label.anchor(itemPos=(1,0), parentPos=(1,0), offset=(-10,10))
        
        
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(10) #ms
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()
    
    
    
    def update_plots(self):
        if not self.signal_start.signal:
            self.counter = 0
            if self.pipe_input.poll():
                while self.pipe_input.poll():
                    self.pipe_input.recv()
    
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
                    
                    if len(self.elapsed_time) > 2500:
                        self.elapsed_time = self.elapsed_time[1:]
                    
                    if len(self.input_channelDict[channel].plot.data) > 2500:
                        self.input_channelDict[channel].plot.data = self.input_channelDict[channel].plot.data[1:]
                    self.input_channelDict[channel].plot.line.setData(self.elapsed_time, self.input_channelDict[channel].plot.data)
        
                    # Update label
                    self.input_channelDict[channel].label.setText(f"x: {elapsed_time:5.2f}, y: {data[self.input_channelDict[channel].index]:5.2f}")
                    
               
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
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        
        
        path = "C:\\Users\\ultservi\\Desktop\\Elmy\\python-flying-balls\\"
        self.path_textbox = QLineEdit(f"{path}out\\")
        self.db_textbox = QLineEdit(f"{path}.env")
        

        
        
        layout_fsettings = FileSettingsLayout(self.checkbox, self.path_textbox, self.db_textbox)
        layout_ramp = RampSettingsLayout(self.pipe_param, self.signal_start, self.pipe_signal, self.checkbox, self.path_textbox, self.db_textbox)
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
        self.title = "Flying Balls"
        self.icon = "../fig/icon.png"
        self.setGeometry(40, 40, 1200, 625)
        self.initUI()
    
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon))
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
