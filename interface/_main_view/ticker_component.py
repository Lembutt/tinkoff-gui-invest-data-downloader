from .._base import RowComponent
from tkinter import *
from tkinter import ttk

class TickerComponent(RowComponent):
  def __init__(self, frame, local_storage, row, status_api, tinkoff_api):
    '''
    TickerComponent constructor
    
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

  def update_ticker(self, ticker_entry, ticker_type_combobox):
    '''
    Update ticker button handler. Updates ticker prices by ticker and ticker type
    
    ticker_entry: ttk.Entry
    ticker_type_combobox: ttk.Combobox
    
    return: None'''
    try:
      ticker = ticker_entry.get()
      ticker_type = ticker_type_combobox.get()
      if ticker and ticker_type:
        self.tinkoff_api.update_prices_by_ticker(ticker, ticker_type)
      else:
        print("Ticker or ticker type is empty")

      self.status_api.set_text(f"Ticker {ticker} of type {ticker_type} updated")
    except Exception as e:
      raise e

  def _draw(self):
    self.create_ticker_component()

  def create_ticker_component(self):
    '''
    Create ticker component. This component contains ticker label, ticker entry, ticker type combobox and update ticker button
    
    return: None'''
    # Create label from ttk
    self.ticker_label = ttk.Label(self.frame, text="Choose ticker", width=15)
    self.ticker_label.grid(row=self.row, column=0, sticky=W)

    # Create ticker entry
    self.ticker_entry = ttk.Entry(self.frame, width=20)  
    self.ticker_entry.grid(row=self.row, column=1, sticky=W)

    # Create ticker type combobox
    self.ticker_type_combobox = ttk.Combobox(self.frame, width=20, state="readonly")
    self.ticker_type_combobox["values"] = ("shares", "futures", "currencies", "bonds", "etfs")
    self.ticker_type_combobox.current(0)
    self.ticker_type_combobox.grid(row=self.row, column=2, sticky=W)

    # Create ticker choose button
    self.ticker_choose_button = ttk.Button(self.frame, text="Update Ticker", command=lambda: self.update_ticker(self.ticker_entry, self.ticker_type_combobox))
    self.ticker_choose_button.grid(row=self.row, column=3, sticky=W)