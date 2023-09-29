from .._base import RowComponent
from tkinter import *
from tkinter import ttk
import winsound

class FigiComponent(RowComponent):

  def __init__(self, frame, local_storage, row, status_api, tinkoff_api):
    '''
    FigiComponent constructor

    frame: tkinter.Frame
    local_storage: LocalStorage
    row: int
    status_api: StatusBarComponent
    tinkoff_api: TinkoffApi
    '''
    super().__init__(frame, row)
    self.local_storage = local_storage
    self.status_api = status_api
    self.tinkoff_api = tinkoff_api

  def update_figi(self,figi_entry):
    try:
      figi = figi_entry.get()

      if figi:
        figi_ = figi \
          .replace(' ', '') \
          .replace('\t', '') \
          .replace('\r', '') \
          .replace('\n', '')
          
        self.tinkoff_api.update_prices_by_figi(figi_)
    except Exception as e:
      print(e)
      self.status_api.set_text(f"Error: {e}")
      winsound.Beep(100, 600)

  def _draw(self):
    # Create label from ttk for figi
    figi_label = ttk.Label(self.frame, text="Choose figi", width=15)
    figi_label.grid(row=self.row, column=0, sticky=W)

    # Create figi entry
    figi_entry = ttk.Entry(self.frame, width=45)
    figi_entry.grid(row=self.row, column=1, sticky=W, columnspan=2)

    # Create figi choose button
    figi_choose_button = ttk.Button(self.frame, text="Update Figi", command=lambda: self.update_figi(figi_entry))
    figi_choose_button.grid(row=self.row, column=3, sticky=W)