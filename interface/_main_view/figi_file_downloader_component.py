from .._base import RowComponent
from tkinter import *
from tkinter import ttk, filedialog
import winsound

class FigiFileDownloaderComponent(RowComponent):
  '''
  FigiFileDownloaderComponent constructor. This component contains figi label, figi file entry and update figi button'''
  def __init__(self, frame, local_storage, row, status_api, tinkoff_api):
    '''
    FigiFileDownloaderComponent constructor

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
    self.create_figi_component()

  def choose_folder(self, figi_file_entry, local_storage):
    filename = filedialog.askopenfilename(
      initialdir = '/',
      title = "Select file",
      filetypes = (("txt files","*.txt"), ("all files","*.*")))
    figi_file_entry.delete(0, END)
    figi_file_entry.insert(0, filename)
    local_storage.set('figis_file', filename)
  
  def update_figis(self, figi_file_entry, local_storage):
    figis_file = figi_file_entry.get()
    if figis_file == '':
      self.status_api.set_text("Figi file is not chosen")
      winsound.Beep(1000, 1000)
      return
    # read figis from file line by line
    with open(figis_file, 'r') as f:
      figis = f.readlines()
    # remove \n from figis
    figis = [
      figi \
        .replace('\n', '') \
        .replace(' ', '') \
        .replace('\t', '') \
        .replace('\r', '') \
      for figi in figis]
    # update figis
    for figi in figis:
      self.tinkoff_api.update_prices_by_figi(figi)
    self.status_api.set_text("Figis are updated")
    winsound.Beep(1000, 1000)

  def create_figi_component(self):

    # Create label from ttk
    self.figi_label = ttk.Label(self.frame, text="Choose figi file", width=15)
    self.figi_label.grid(row=self.row, column=0, sticky=W)

    # Create figi file entry
    self.figi_file_entry = ttk.Entry(self.frame, width=20)
    self.figi_file_entry.grid(row=self.row, column=1, sticky=W, columnspan=2)

    # Create choose file button
    self.choose_file_button = ttk.Button(
      self.frame, 
      text="Choose File", 
      command= lambda: self.choose_folder(self.figi_file_entry, self.local_storage))
    self.choose_file_button.grid(row=self.row, column=2, sticky=W)

    # Create figi update button
    self.figi_update_button = ttk.Button(
      self.frame,
      text="Update Figis",
      command=lambda: self.update_figis(self.figi_file_entry, self.local_storage))
    self.figi_update_button.grid(row=self.row, column=3, sticky=W)
