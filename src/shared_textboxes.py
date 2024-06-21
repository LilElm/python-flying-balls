# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QLabel,
                             QGroupBox,
                             QLineEdit,
                             QGridLayout)



import time


class SharedGroupBox(QGroupBox):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.layout = QGridLayout()    
        self.setLayout(self.layout)
    
    
    def destroy_all_boxes(self):
        for i in reversed(range(self.layout.count())):
            if i>-1:
                self.layout.itemAt(i).widget().setParent(None)
    
    
    
    def make_srate_box(self):
        self.destroy_all_boxes()
        self.textbox_srate = QLineEdit("1000", placeholderText="Sampling Rate")
        self.label_srate = QLabel("Sampling Rate\n(Hz)")
        self.layout.addWidget(self.textbox_srate)
        self.layout.addWidget(self.label_srate)
    
    
    
    
    def make_ramp_box(self):
        self.destroy_all_boxes()
        self.textbox_srate = QLineEdit("1000", placeholderText="Sampling Rate")
        self.textbox_f0 = QLineEdit("7.300", placeholderText="Frequency")
        self.textbox_df = QLineEdit("0.090", placeholderText="Line Width")
        self.textbox_k = QLineEdit("0.465", placeholderText="Spring Constant")
        
        
        self.label_srate = QLabel("Sampling Rate\n(Hz)")
        self.label_f0 = QLabel("Frequency\n(Hz)")
        self.label_df = QLabel("Line Width\n(Hz)")
        self.label_k = QLabel("Spring Constant\n(mm/V)")
        
        
        self.layout.addWidget(self.textbox_srate)
        self.layout.addWidget(self.label_srate)
        
        self.layout.addWidget(self.textbox_f0)
        self.layout.addWidget(self.label_f0)
        
        
        self.layout.addWidget(self.textbox_df)
        self.layout.addWidget(self.label_df)
        
        
        self.layout.addWidget(self.textbox_k)
        self.layout.addWidget(self.label_k)
        
        
    def make_circular_box(self):
        self.destroy_all_boxes()
        
        self.textbox_srate = QLineEdit("1000", placeholderText="Sampling Rate")
        self.textbox_idle = QLineEdit("1.0", placeholderText="Idle")
        self.textbox_rest = QLineEdit("1.0", placeholderText="Rest")
        self.textbox_lag = QLineEdit("0.0", placeholderText="Lag")
        self.textbox_kick_delay = QLineEdit("0.0", placeholderText="AdditionAL Kick Delay")
        
        
        self.label_srate = QLabel("Sampling Rate\n(Hz)")
        self.label_idle = QLabel("Time Idle\n(s)")
        self.label_rest = QLabel("Time Rest\n(s)")
        self.label_lag = QLabel("Lag\n(s)")
        self.label_kick_delay = QLabel("Additional Kick Delay\n(s)")
        
        
        self.layout.addWidget(self.textbox_srate)
        self.layout.addWidget(self.label_srate)
        
        self.layout.addWidget(self.textbox_idle)
        self.layout.addWidget(self.label_idle)
        
        
        self.layout.addWidget(self.textbox_rest)
        self.layout.addWidget(self.label_rest)
        
        
        self.layout.addWidget(self.textbox_lag)
        self.layout.addWidget(self.label_lag)
        
        self.layout.addWidget(self.textbox_kick_delay)
        self.layout.addWidget(self.label_kick_delay)