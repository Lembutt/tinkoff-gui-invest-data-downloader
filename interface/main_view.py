from tkinter import *
from tkinter import ttk, filedialog
from utils import LocalStorage, TinkoffApi
import winsound
from ._base import Component
from ._main_view import FolderPathComponent, \
  TokenInsertComponent, \
  StatusBarComponent, \
  TickerComponent, \
  FigiComponent, \
  FigiFileDownloaderComponent

class MainView(Component):
  '''
  MainView class
  
  This class is responsible for drawing all the components of the main view
  '''
  FOLDER_PATH_ROW = 0
  TOKEN_INSERT_ROW = 1
  STATUS_BAR_ROW = 2
  TICKER_ROW = 3
  FIGI_ROW = 4
  FIGI_FILE_DOWNLOADER_ROW = 5

  def __init__(self, frame, local_storage, tinkoff_api):
    '''
    MainView constructor

    frame: tkinter.Frame
    local_storage: LocalStorage
    tinkoff_api: TinkoffApi
    '''
    super().__init__(frame)
    self.local_storage = local_storage
    self.tinkoff_api = tinkoff_api

  def draw(self):
    '''
    Draw all the components of the main view
    
    return: None'''
    self.status_api = self.create_status_bar_component()
    self.create_folder_path_component()
    self.crate_token_insert_component()
    self.create_ticker_component()
    self.create_figi_component()
    self.create_figi_downloader_component()

  def create_folder_path_component(self):
    return FolderPathComponent(
      self.frame, 
      self.local_storage, 
      self.FOLDER_PATH_ROW
    ).draw()

  def crate_token_insert_component(self):
    return TokenInsertComponent(
      self.frame, 
      self.local_storage, 
      self.TOKEN_INSERT_ROW, 
      self.status_api, 
      self.tinkoff_api
    ).draw()

  def create_status_bar_component(self):
    return StatusBarComponent(
      self.frame, 
      self.STATUS_BAR_ROW
    ).draw()

  def create_ticker_component(self):
    return TickerComponent(
      self.frame,
      self.local_storage,
      self.TICKER_ROW, 
      self.status_api, 
      self.tinkoff_api
    ).draw()

  def create_figi_component(self):
    return FigiComponent(
      self.frame,
      self.local_storage,
      self.FIGI_ROW, 
      self.status_api, 
      self.tinkoff_api
    ).draw()

  def create_figi_downloader_component(self):
    return FigiFileDownloaderComponent(
      self.frame,
      self.local_storage,
      self.FIGI_FILE_DOWNLOADER_ROW, 
      self.status_api, 
      self.tinkoff_api
    ).draw()
  