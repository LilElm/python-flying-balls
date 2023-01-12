
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
#from PyQt5.QtCore import *####pyqtSlot
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
import pyqtgraph as pg

from force_profile_dummy import force_profile

#from main import main


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
        self.combo_box_list = ["Ramp Profile", "Sine Profile"]
        for item in self.combo_box_list:
            self.combo_box.addItem(item)
        self.combo_box.activated[str].connect(self.select_profile)
    
    def select_profile(self):
        content = self.combo_box.currentText()
        self.make_textboxes(content)
        
    def make_textboxes(self, content):
        self.content = content
        if content == self.combo_box_list[0]:
            # Make content for "Ramp Profile"
            
    
            for i in reversed(range(self.count())):
                if i>0:
                    self.itemAt(i).widget().setParent(None)   
            


            self.labelDict = {}
            self.labelDict[QLabel("Velocity\n(mm/s)")] = [1, 1, 1, 1]
            self.labelDict[QLabel("Time Idle\n(ms)")] = [3, 0, 1, 1]
            self.labelDict[QLabel("Time Acc\n(ms)")] = [3, 1, 1, 1]
            self.labelDict[QLabel("Time Ramp\n(ms)")] = [5, 0, 1, 1]
            self.labelDict[QLabel("Time Rest\n(ms)")] = [5, 1, 1, 1]
            
            
            self.textboxDict = {}
            self.textboxDict[QLineEdit(placeholderText="Velocity")] = [0, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Idle")] = [2, 0, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Acc")] = [2, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Ramp")] = [4, 0, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Rest")] = [4, 1, 1, 1]
            
            
            for label in self.labelDict:
                a, b, c, d = self.labelDict[label]
                self.addWidget(label, a, b, c, d)
            for textbox in self.textboxDict:
                a, b, c, d = self.textboxDict[textbox]
                self.addWidget(textbox, a, b, c, d)
            
            
            
        elif content == self.combo_box_list[1]:
            # Make content for Sine Profile
            for i in reversed(range(self.count())):
                if i>0:
                    self.itemAt(i).widget().setParent(None)   

            self.labelDict = {}
            self.labelDict[QLabel("Amplitude\n(mV ptp)")] = [1, 1, 1, 1]
            self.labelDict[QLabel("Frequency\n(Hz)")] = [3, 0, 1, 1]
            self.labelDict[QLabel("Phase\n(deg)")] = [3, 1, 1, 1]
            
            self.textboxDict = {}
            self.textboxDict[QLineEdit(placeholderText="Amp")] = [0, 1, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Freq")] = [2, 0, 1, 1]
            self.textboxDict[QLineEdit(placeholderText="Phase")] = [2, 1, 1, 1]
            
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
        self.sampling_rate = float(self.textbox_srate.text())
        
        # Read all textboxes and return the values
        for coil in self.coil_layout_dict:
            self.coil_layout_dict[coil].textboxValuesDict = {}
            for textbox in self.coil_layout_dict[coil].textboxDict:
                self.coil_layout_dict[coil].textboxValuesDict[str(coil) + " " + str(textbox.placeholderText())] = float(textbox.text())
            
        
        # Check the validity of each input value
        success = self.check_input()
        
        # If valid, send input parameters through pipe_params to main.py
        # From there, force_profile.py will be called with the parameters
        if success:
            self.pipe_param.send(self.sampling_rate)
            for coil in self.coil_layout_dict:
                val = list(self.coil_layout_dict[coil].textboxValuesDict.values())
                self.pipe_param.send(val)
                
                #for textbox in self.coil_layout_dict[coil].textboxDict:
                #    print(str(self.coil_layout_dict[coil].textboxValuesDict[str(coil) + " " + str(textbox.placeholderText())]))
                    
                 #   self.pipe_param.send(self.coil_layout_dict[coil].textboxValuesDict[str(coil) + " " + str(textbox.placeholderText())])
            #self.pipe_param.send(self.sampling_rate)
                    

        else:
            print("Do nothing")
            #for val in self.coil_layout_dict[coil].textboxDict:
             #   check_input(val)
            
        
        
    def check_input(self):
        # Modulo, whether via % of math.fmod() is completely broken
        # Decimal(str()) % Decimal(str()) offers a solution, even if clunky
        # Nota bene, this does not work with math.fmod(); only %
        
        error_code = 0
        error_message = []
        try:
            dt = 1.0 / float(self.sampling_rate)
        except:
            print("Please enter a valid sampling rate.")
            error_message.append("Please enter a valid sampling rate.")
            error_code = 1
            
        if error_code == 0:
            for coil in self.coil_layout_dict:
                for textbox in self.coil_layout_dict[coil].textboxValuesDict:
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
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        

        #======================================================
        # Layout output graphs
        
        self.addWidget(pg.PlotWidget(),1)
        self.addWidget(pg.PlotWidget(),1)
        #==============================================================


class InputGraphLayout(QVBoxLayout):
    def __init__(self, channelDict, pipe_plot, signal_start, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        

        self.pipe_plot = pipe_plot
        self.signal_start = signal_start
        self.channelDict = channelDict
        #==============================================================
        # Layout input graphs
        
        # input widget 1
        #self.inputWidget1 = pg.PlotWidget()
        
        
        
        
        
        
        #plotlist = ["inputWidget1", "inputWidget2", "inputWidget3", "inputWidget4", "inputWidget5"]
        #self.plotDict = {plot: pg.PlotWidget(plot=plot) for plot in plotlist}
        
        for channel in self.channelDict:
            self.channelDict[channel].plot = pg.PlotWidget()
            self.channelDict[channel].plot.setLabel('left', 'Voltage (V)')
            self.channelDict[channel].plot.setLabel('bottom', 'Elapsed Time (s)')
            self.channelDict[channel].plot.addLegend()
            self.channelDict[channel].plot.data = []
            self.elapsed_time = []
            self.channelDict[channel].plot.line = self.channelDict[channel].plot.plot(self.elapsed_time,
                                                                                      self.channelDict[channel].plot.data)
            self.addWidget(self.channelDict[channel].plot, 1)
            
        
        """
        
        index = 1
        for plot in self.plotDict:
            
            
            
            
            self.plotDict[plot].pipe = pipeDict[index]
            self.plotDict[plot].setLabel('left', 'Voltage (V)')
            self.plotDict[plot].setLabel('bottom', 'Elapsed Time (s)')
            self.plotDict[plot].addLegend()
            self.plotDict[plot].data = []
            self.plotDict[plot].line = self.plotDict[plot].plot(self.plotDict[plot].data)
            self.addWidget(self.plotDict[plot], 1)
            
            index = index + 1
        
        """
        
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(50) # 4 ms = 250 refreshes per sec
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()
    
    
    
    def update_plots(self):
        if self.signal_start.signal:
            #data = self.channelDict[channel].pipea.recv() # Put a timeout on this to prevent program not responding
          
            data = self.pipe_plot.recv()
            
           # print(str(data))
           # time.sleep(5)
            
            if self.counter == 0:
                self.time_start = data[0]
                self.counter = 1
            elapsed_time = data[0] - self.time_start
            self.elapsed_time.append(elapsed_time)
            
            
            for channel in self.channelDict:
                self.channelDict[channel].plot.data.append(data[self.channelDict[channel].index])
              
                if len(self.channelDict[channel].plot.data) > 2000:                    
                    self.elapsed_time = self.elapsed_time[1:]
                    self.channelDict[channel].plot.data = self.channelDict[channel].plot.data[1:]
                
                self.channelDict[channel].plot.line.setData(self.elapsed_time, self.channelDict[channel].plot.data)
    
    """
    def update_plot(self, channel):
        try:
            #data = self.plotDict[plot].pipe.recv()
            data = self.channelDict[channel].pipeb.recv()
            #self.plotDict[plot].data.extend(data)
            self.channelDict[channel].data.extend(data)
            self.plotDict[plot].line.setData(self.plotDict[plot].data)
                
        except Exception as e:
            print(str(e))
            print("Error in update_plot()")
    """    
        
        
        
 
               
class SignalStart():
    def __init__(self, signal=False):
        self.signal = signal        
        
        
        
        #==============================================================



class Layout(QGridLayout):
    def __init__(self, channelDict, pipe_param, pipe_plot, signal_start, pipe_signal, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.channelDict = channelDict
        self.pipe_param = pipe_param
        self.signal_start = signal_start
        self.pipe_signal = pipe_signal
        self.pipe_plot = pipe_plot
        
        
        layout_fsettings = FileSettingsLayout()
        layout_ramp = RampSettingsLayout(self.pipe_param, self.signal_start, self.pipe_signal)
        layout_output = OutputGraphLayout()
        layout_input = InputGraphLayout(self.channelDict, self.pipe_plot, self.signal_start)
        
        
        
        
        #"""
        self.addLayout(layout_fsettings, 0, 0, 1, 3)
        self.addLayout(layout_ramp, 1, 0, 1, 1)
        self.addLayout(layout_output, 1, 1, 1, 1)
        self.addLayout(layout_input, 1, 2, 1, 1)
        """
        self.addLayout(layout_fsettings, 0, 0, 1, 5)
        self.addLayout(layout_ramp, 1, 0, 1, 1)
        self.addLayout(layout_output, 1, 1, 1, 2)
        self.addLayout(layout_input, 1, 3, 1, 2)
        """
        
        



class MainWindow(QMainWindow):
    def __init__(self, channelDict, pipe_param, pipe_plot, signal_start, pipe_signal, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.channelDict = channelDict
        self.pipe_param = pipe_param
        #self.signal_start = SignalStart()
        self.signal_start = signal_start
        self.pipe_signal = pipe_signal
        self.pipe_plot = pipe_plot
        self.title = "GUI Demo"
        self.setGeometry(40, 40, 1200, 625)
        self.initUI()
    
    
    def initUI(self):
        self.setWindowTitle(self.title)
        grid_layout = Layout(self.channelDict, self.pipe_param, self.pipe_plot, self.signal_start, self.pipe_signal)
        
        
        widget = QWidget()
        widget.setLayout(grid_layout)
        self.setCentralWidget(widget)
        self.show()
#        while True:
 #           data = self.pipe.recv()
  #          print(str(data))
        
    """
        
        # Create a button in the window
        self.button = QPushButton('Show text', self)
        self.button.move(20,80)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()
    
    @pyqtSlot()
    def on_click(self):
       # textboxValue = self.textboxDict["lat0_vol"].text()
        #QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        #self.textboxDict["lat0_vol"].setText("")
        #main(textboxValue)
        pass




            
    """


def start_gui(pipeDict, pipe_param, pipe_plot, signal_start, pipe_signal):
    #print(str(msg))
    app = QApplication(sys.argv)
    ex = MainWindow(pipeDict, pipe_param, pipe_plot, signal_start, pipe_signal)
    sys.exit(app.exec_())

if __name__ == '__main__':
    start_gui()
