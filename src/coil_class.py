# -*- coding: utf-8 -*-


from multiprocessing import Pipe
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

"""
Module contains class definitions for: CoilChannel,
                                       
                                       
"""
from textbox_class import TextBox
import time
        





class CoilChannel():
    def __init__(self, channel_output, channel, name, index, shared_box, pipe=False):
        self.channel_output = channel_output
        self.channel = channel
        self.name = name
        self.index = index
        self.shared_box = shared_box
        self.add_layout()
        self.add_box()
        self.coil_dict=None
        
        if pipe:
            self.pipe = Pipe(duplex=True)


    def add_layout(self):
        self.layout = CoilProfileLayout(self)


    def add_box(self):
        self.box = QGroupBox(self.name)
        self.box.setLayout(self.layout)
        self.box.setMaximumWidth(250)
        
        
        


    def give_access_to_dict(self, coil_dict):
        self.coil_dict = coil_dict








class CoilProfileLayout(QGridLayout):
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
        self.combo_box_list = ["Ramp Profile", "Sine Profile",
                               "Half-sine Profile", "Half-sine Pulses Profile",
                               "Circular Profile", "Upload Custom"]
        for item in self.combo_box_list:
            self.combo_box.addItem(item)
        self.combo_box.activated[str].connect(self.select_profile)
    
    def select_profile(self, profile=None):
        if profile == None:
            profile = self.combo_box.currentText()
        self.make_textboxes(profile)
    

    
    def make_textboxes(self, profile):
        self.profile = profile
        
        # Destroy all existing textboxes
        for i in reversed(range(self.count())):
            if i>0:
                self.itemAt(i).widget().setParent(None)
        
        
        
        
        
        # Make profile for "Ramp Profile"
        if profile == self.combo_box_list[0]:
            #self.coil.shared_box.destroy_all_boxes()
            self.coil.shared_box.make_ramp_box()
            
            
            
            
            textbox_placeholders = ["Drive", "Idle", "Acc", "Ramp", "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1],
                            [4, 1, 1, 1]]
            textbox_labels = ["Drive (V)",
                              "Time Idle (s)",
                              "Time Acc (s)",
                              "Time Ramp (s)",
                              "Time Rest (s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1],
                                 [5, 1, 1, 1]]
        
        
        # Make profile for Sine Profile
        elif profile == self.combo_box_list[1]:
            # Check if any other profiles are "Ramp Profile",
            # in which case the ramp shared box is needed
            if any(self.coil.coil_dict[coil].layout.profile == self.combo_box_list[0] for coil in self.coil.coil_dict):
               self.coil.shared_box.make_ramp_box()
            else:
                self.coil.shared_box.make_srate_box()
                
                
                
            textbox_placeholders = ["Amplitude", "Freq", "Phase", "Offset", "Cycles", "Idle", "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1],
                            [4, 1, 1, 1],
                            [6, 0, 1, 1],
                            [6, 1, 1, 1]]
            textbox_labels = ["Amplitude (V)",
                              "Frequency (Hz)",
                              "Phase (deg)",
                              "Offset (V)",
                              "Cycles",
                              "Time Idle (s)",
                              "Time Rest (s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1],
                                 [5, 1, 1, 1],
                                 [7, 0, 1, 1],
                                 [7, 1, 1, 1]]
        
        
        # Make profile for Half-sine Profile
        elif profile == self.combo_box_list[2]:
            # Check if any other profiles are "Ramp Profile",
            # in which case the ramp shared box is needed
            if any(self.coil.coil_dict[coil].layout.profile == self.combo_box_list[0] for coil in self.coil.coil_dict):
               self.coil.shared_box.make_ramp_box()
            else:
                self.coil.shared_box.make_srate_box()
            
            
            
            textbox_placeholders = ["Amplitude", "Freq", "Idle", "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1]]
            textbox_labels = ["Amplitude (V)",
                              "Frequency (Hz)",
                              "Time Idle (s)",
                              "Time Rest (s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1]]
        
            
        # Make profile for Half-sine Pulses Profile
        elif profile == self.combo_box_list[3]:
            textbox_placeholders = ["Initial Amp",
                                    "Subsequent Amplitude",
                                    "Initial Frequency",
                                    "Subsequent Frequency",
                                    "Ball Frequency",
                                    "Orbits",
                                    "Idle",
                                    "Delay",
                                    "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1],
                            [4, 1, 1, 1],
                            [6, 0, 1, 1],
                            [6, 1, 1, 1],
                            [8, 0, 1, 1],
                            [8, 1, 1, 1]]
            textbox_labels = ["Initial Amplitude (V)",
                              "Subsequent Amplitude (V)",
                              "Initial Frequency (Hz)",
                              "Subsequent Frequency (Hz)",
                              "Ball Frequency (Hz)",
                              "Orbits",
                              "Time Idle (s)",
                              "Ad. Delay between Kicks (s)",
                              "Time Rest (s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1],
                                 [5, 1, 1, 1],
                                 [7, 0, 1, 1],
                                 [7, 1, 1, 1],
                                 [9, 0, 1, 1],
                                 [9, 1, 1, 1]]
        
            
            
        # Make profile for Circular Profile
        elif profile == self.combo_box_list[4]:
            self.coil.shared_box.make_circular_box()
            
            for coil in self.coil.coil_dict:
                if self.coil.coil_dict[coil].layout.profile != self.combo_box_list[4]:
                
                    """ 
                for i in reversed(range(self.coil.coil_dict[coil].layout.count())):
                    if i>0:
                        self.coil.coil_dict[coil].layout.itemAt(i).widget().setParent(None)
                        """
                    self.coil.coil_dict[coil].layout.combo_box.setCurrentText(profile)
                    self.coil.coil_dict[coil].layout.select_profile(profile)
                




            
            
            textbox_placeholders = ["Initial Amp",
                                    "Subsequent Amplitude",
                                    "Initial Frequency",
                                    "Subsequent Frequency"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1]]
            textbox_labels = ["Initial Amplitude (V)",
                              "Subsequent Amplitude (V)",
                              "Initial Frequency (Hz)",
                              "Subsequent Frequency (Hz)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1]]
        
            
        
        
        
        
        
        # Make profile for Custom Profile
        elif profile == self.combo_box_list[5]:
            # Check if any other profiles are "Ramp Profile",
            # in which case the ramp shared box is needed
            if any(self.coil.coil_dict[coil].layout.profile == self.combo_box_list[0] for coil in self.coil.coil_dict):
               self.coil.shared_box.make_ramp_box()
            else:
                self.coil.shared_box.make_srate_box()
            
            
            textbox_placeholders = ["Directory"]
            textbox_locs = [[2, 0, 1, 1]]
            textbox_labels = ["Directory"]
            textbox_labellocs = [[3, 0, 1, 1]]
            
            
                
        self.textboxDict = {}
        for i in range(len(textbox_placeholders)):
            self.textboxDict[textbox_placeholders[i]] = TextBox(
                                                    textbox_placeholders[i],
                                                    textbox_labels[i],
                                                    None,
                                                    textbox_locs[i],
                                                    textbox_labellocs[i])


        # Add the labels and textboxes
        for textbox in self.textboxDict:
            a, b, c, d = self.textboxDict[textbox].loc
            self.addWidget(self.textboxDict[textbox].textbox, a, b, c, d)
            
            a, b, c, d = self.textboxDict[textbox].label_loc
            self.addWidget(self.textboxDict[textbox].label, a, b, c, d)
            


