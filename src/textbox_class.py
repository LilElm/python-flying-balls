# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QLabel,
                             QLineEdit)

class TextBox():
    def __init__(self,
                 placeholder,
                 label_text,
                 val=None,
                 loc=None,
                 label_loc=None,
                 parent=None,
                 *args,
                 **kwargs):
        self.placeholder = placeholder
        self.loc = loc
        self.label_text = label_text
        self.label_loc = label_loc
        
        self.textbox = QLineEdit(val, placeholderText=str(placeholder))
        self.label = QLabel(str(label_text))
        
