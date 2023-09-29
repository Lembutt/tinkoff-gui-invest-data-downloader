from tkinter import *

class Component:
  def __init__(self, frame):
    '''
    Component constructor

    frame: tkinter.Frame
    '''
    self.frame = frame

  def draw(self):
    self._draw()
    return self

  def _draw(self):
    raise NotImplementedError

class RowComponent(Component):
  def __init__(self, frame, row):
    '''
    RowComponent constructor

    frame: tkinter.Frame
    row: int
    '''
    super().__init__(frame)
    self.row = row
