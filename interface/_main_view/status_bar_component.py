from tkinter import *
from tkinter import ttk
from .._base import RowComponent

class StatusBarComponent(RowComponent):
  '''
  StatusBarComponent class
  
  This class is responsible for drawing the status bar'''

  def __init__(self, frame, row):
    '''
    StatusBarComponent constructor
    
    frame: tkinter.Frame
    row: int
    '''
    super().__init__(frame, row)

  def _draw(self):
    self.create_status_bar()

  def create_status_bar(self):
    '''
    Create status bar. It will be used to show the current status of the application
    
    return: None'''
    # Create status label
    self.status_label = ttk.Label(self.frame, text="Status: ")
    self.status_label.grid(row=self.row, column=0, sticky=W)

    # Create current status
    self.current_status_label = ttk.Label(self.frame, text="Waiting for action")
    self.current_status_label.grid(row=self.row, column=1, sticky=W, columnspan=3)

  def set_text(self, text):
    '''
    Set text to the status bar
    
    text: str
    
    return: None'''
    self.current_status_label.configure(text=f"Status: {text}")

  def get_text(self):
    '''
    Get text from the status bar
    
    return: str
    '''
    return self.current_status_label.cget('text')  