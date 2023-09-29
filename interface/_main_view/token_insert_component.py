from tkinter import *
from tkinter import ttk, filedialog
from .._base import RowComponent
import winsound

class TokenInsertComponent(RowComponent):
  '''
  TokenInsertComponent class. This class is responsible for drawing token insert menu
  '''
  def __init__(self, frame, local_storage, row, status_api, tinkoff_api):
    '''
    TokenInsertComponent constructor

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

  def _draw(self):
    self.create_token_insert_menu()
  
  def create_token_insert_menu(self):
    '''
    Create token insert menu. This menu contains token label, token entry and token save button
    
    return: None
    '''
    # Create token label
    token_label = ttk.Label(self.frame, text="Token: ")
    token_label.grid(row=self.row, column=0, sticky=W)

    # Create token entry
    token_entry = ttk.Entry(self.frame, width=45)
    token_entry.grid(row=self.row, column=1, sticky=W, columnspan=2)

    token_save_button = ttk.Button(
      self.frame, 
      text="Save token", 
      command=lambda: self.save_token(
        token_entry,
        self.local_storage,
        self.status_api,
        self.tinkoff_api
      ))
    token_save_button.grid(row=self.row, column=3, sticky=W)

  # Create token save button
  def save_token(self, token_entry, local_storage, status_api, tinkoff_api):
    try:
      token = token_entry.get()
      local_storage.set('token', token)
      status_api.set_text("Token saved")
      tinkoff_api.update_token()
    except Exception as e:
      print(e)
      status_api.set_text(f"Token Entry Error")
      winsound.Beep(100, 600)

