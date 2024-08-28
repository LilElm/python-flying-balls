# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QLabel,
                             QGroupBox,
                             QLineEdit,
                             QGridLayout)



import time
from textbox_class import TextBox


class SharedGroupBox(QGroupBox):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setMaximumWidth(250)
        self.layout = QGridLayout()    
        self.setLayout(self.layout)
        self.textboxDict = {}
        
        
    
    
    def destroy_all_boxes(self):
        self.textboxDict = {}
        for i in reversed(range(self.layout.count())):
            if i>-1:
                self.layout.itemAt(i).widget().setParent(None)
    
    
    
    def make_srate_box(self):
        self.destroy_all_boxes()
        
        textbox_placeholders = ["Sampling Rate"]
        textbox_labels = ["Sampling Rate (Hz)"]
        textbox_vals = ["1000"]
        
        self.textboxDict = {}
        for i in range(len(textbox_placeholders)):
            self.textboxDict[textbox_placeholders[i]] = TextBox(
                                                    textbox_placeholders[i],
                                                    textbox_labels[i],
                                                    textbox_vals[i])

        # Add the labels and textboxes
        for textbox in self.textboxDict:
            self.layout.addWidget(self.textboxDict[textbox].textbox)
            self.layout.addWidget(self.textboxDict[textbox].label)
    
    
    
    
    def make_ramp_box(self):
        self.destroy_all_boxes()
          
        textbox_placeholders = ["Sampling Rate",
                                "Frequency",
                                "Line Width",
                                "Spring Constant"]
        
        textbox_labels = ["Sampling Rate (Hz)",
                          "Frequency (Hz)",
                          "Line Width (Hz)",
                          "Spring Constant (mm/V)"]
        
        textbox_vals = ["1000",
                        "7.300",
                        "0.090",
                        "0.465"]
            
                
        self.textboxDict = {}
        for i in range(len(textbox_placeholders)):
            self.textboxDict[textbox_placeholders[i]] = TextBox(
                                                    textbox_placeholders[i],
                                                    textbox_labels[i],
                                                    textbox_vals[i])

        # Add the labels and textboxes
        for textbox in self.textboxDict:
            self.layout.addWidget(self.textboxDict[textbox].textbox)
            self.layout.addWidget(self.textboxDict[textbox].label)
            
        
        
        
        
    def make_circular_box(self):
        self.destroy_all_boxes()
        
        
          
        textbox_placeholders = ["Sampling Rate",
                                "Ball Frequency",
                                "Orbits",
                                "Idle",
                                "Rest",
                                "Lag",
                                "Additional Kick Delay"]
        
        textbox_labels = ["Sampling Rate (Hz)",
                          "Ball Frequency  Hz)",
                          "Orbits",
                          "Time Idle (s)",
                          "Time Rest (s)",
                          "Lag (s)",
                          "Additional Kick Delay (s)"]
        
        self.textboxDict = {}
        for i in range(len(textbox_placeholders)):
            self.textboxDict[textbox_placeholders[i]] = TextBox(
                                                    textbox_placeholders[i],
                                                    textbox_labels[i])


        # Add the labels and textboxes
        for textbox in self.textboxDict:
            self.layout.addWidget(self.textboxDict[textbox].textbox)
            self.layout.addWidget(self.textboxDict[textbox].label)
            
        