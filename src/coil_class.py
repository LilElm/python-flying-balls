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

      
        





class CoilChannel():
    def __init__(self, channel_output, channel, name, index, pipe=False):
        self.channel_output = channel_output
        self.channel = channel
        self.name = name
        self.index = index
        self.add_layout()
        self.add_box()
        
        if pipe:
            self.pipe = Pipe(duplex=True)


    def add_layout(self):
        self.layout = CoilProfileLayout()


    def add_box(self):
        self.box = QGroupBox(self.name)
        self.box.setLayout(self.layout)
        self.box.setMaximumWidth(250)
        
        
        













class CoilProfileLayout(QGridLayout):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.make_layout()
        
        

    def make_layout(self):
        self.define_combo_box()
        self.addWidget(self.combo_box, 0, 0, 1, 1)
        self.make_textboxes(self.combo_box_list[0])
        
        

    def define_combo_box(self):
        self.combo_box = QComboBox()
#        self.combo_box_list = ["Ramp Profile", "Sine Profile", "Half-sine Profile", "Half-sine Pulses Profile", "Upload Custom"]
        self.combo_box_list = ["Ramp Profile", "Sine Profile", "Half-sine Profile", "Half-sine Pulses Profile", "Upload Custom"]
        for item in self.combo_box_list:
            self.combo_box.addItem(item)
        self.combo_box.activated[str].connect(self.select_profile)
    
    def select_profile(self):
        profile = self.combo_box.currentText()
        self.make_textboxes(profile)
    

    
    def make_textboxes(self, profile):
        # Destroy all existing textboxes
        for i in reversed(range(self.count())):
            if i>0:
                self.itemAt(i).widget().setParent(None)
        self.profile = profile
        
        
        # Make profile for "Ramp Profile"
        if profile == self.combo_box_list[0]:
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
        
        
        # Make profile for Sine Profile
        elif profile == self.combo_box_list[1]:
            textbox_placeholders = ["Amplitude", "Freq", "Phase", "Offset", "Cycles", "Idle", "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1],
                            [4, 1, 1, 1],
                            [6, 0, 1, 1],
                            [6, 1, 1, 1]]
            textbox_labels = ["Amplitude\n(V)",
                              "Frequency\n(Hz)",
                              "Phase\n(deg)",
                              "Offset\n(V)",
                              "Cycles",
                              "Time Idle\n(s)",
                              "Time Rest\n(s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1],
                                 [5, 1, 1, 1],
                                 [7, 0, 1, 1],
                                 [7, 1, 1, 1]]
        
        
        # Make profile for Half-sine Profile
        elif profile == self.combo_box_list[2]:
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
        
            
        # Make profile for Half-sine Pulses Profile
        elif profile == self.combo_box_list[3]:
            textbox_placeholders = ["Initial Amp",
                                    "Initial Frequency",
                                    "Subsequent Amplitude",
                                    "Subsequent Frequency",
                                    "Ball Frequency",
                                    "Orbits",
                                    "Idle",
                                    "Rest"]
            textbox_locs = [[0, 1, 1, 1],
                            [2, 0, 1, 1],
                            [2, 1, 1, 1],
                            [4, 0, 1, 1],
                            [4, 1, 1, 1],
                            [6, 0, 1, 1],
                            [6, 1, 1, 1],
                            [8, 0, 1, 1]]#,
                            #[8, 1, 1, 1]]
            textbox_labels = ["Initial Amplitude\n(V)",
                              "Initial Frequency\n(Hz)",
                              "Subsequent Amplitude\n(V)",
                              "Subsequent Frequency\n(Hz)",
                              "Ball Frequency\n(Hz)",
                              "Orbits",
                              "Time Idle\n(s)",
                              "Time Rest\n(s)"]
            textbox_labellocs = [[1, 1, 1, 1],
                                 [3, 0, 1, 1],
                                 [3, 1, 1, 1],
                                 [5, 0, 1, 1],
                                 [5, 1, 1, 1],
                                 [7, 0, 1, 1],
                                 [7, 1, 1, 1],
                                 [9, 0, 1, 1]]#,
                                 #[9, 1, 1, 1]]
        
            
        
        
        
        
        
        # Make profile for Custom Profile
        elif profile == self.combo_box_list[4]:
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
            


class TextBox():
    def __init__(self, placeholder, loc, label_text, label_loc, parent=None, *args, **kwargs):
        self.placeholder = placeholder
        self.loc = loc
        self.label_text = label_text
        self.label_loc = label_loc
        
        self.textbox = QLineEdit(placeholderText=str(placeholder))
        self.label = QLabel(str(label_text))
        
