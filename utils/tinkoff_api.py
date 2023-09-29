from tinkoff.invest import Client, InstrumentStatus
from tinkoff.invest.constants import INVEST_GRPC_API
from . import LocalStorage
import pandas as pd
from datetime import datetime
import os, json, requests as req, zipfile, gzip
import time

class TickerDataDataframe:
  def __init__(self, path):
    self.path = path
    self._df = None

  @property
  def df(self):
    if self._df is None:
      return self.load_df_from_file()
    return self._df

  @df.setter
  def df(self, df):
    self._df = df

  def load_df_from_file(self):
    self._df = pd.read_csv(
      self.path,
      names=['date', 'time', 'open', 'close', 'high', 'low', 'volume']
    )
    return self.df

  def update_df(self, df):
    self.df = pd.concat([self.df, df])
    self.df = self.df.drop_duplicates( 
      subset=['date', 'time'], 
      keep='last')
    self.df = self.remove_non_trading_days()

    self.delete_df_file()
    return self.save_df_to_file()
    
  def delete_df_file(self):
    os.remove(self.path)

  def save_df_to_file(self, df=None):
    if df is not None:
      df_to_save = df
    else:
      df_to_save = self.df
    df_to_save.to_csv(
      self.path, 
      index=False,
      columns=['date', 'time', 'open', 'close', 'high', 'low', 'volume'],
      header=False
    )

    return self.load_df_from_file()

  @property
  def trade_calendar(self):
    calendar =  pd.read_csv(
      os.path.join(
        os.path.dirname(
          os.path.abspath(__file__)
        ), '../util-data/trade-calendar.csv'
      ), names=['date', 'is_holiday'])

    calendar['date'] = calendar['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

    return calendar

  def remove_non_trading_days(self):
    calendar = self.trade_calendar
    # remove non trading days
    df = self.df[self.df['date'].isin(calendar[calendar['is_holiday'] == 0]['date'])]
    # get types of dataframe
    df_types = df.dtypes
    print(df_types)
    
    return df

  @property
  def last_candle(self):
    return self.df.iloc[-1]

  @property
  def last_candle_date(self):
    return self.last_candle['date']

class TickerData:
  def __init__(self, ticker=None, ticker_type=None, figi=None):
    self._ticker = ticker
    self._ticker_type = ticker_type
    self._figi = figi
    self._df = None

  def __str__(self):
    return f'{self.ticker} {self.ticker_type} {self.figi}'

  @property
  def figi(self):
    return self._figi

  @figi.setter
  def figi(self, figis: list[str]):
    '''
    Set figi from list of figis. If there is no figi with BBG in it, then set the first figi from the list
    
    figis: list[str]
    
    return: None'''
    self._figi = None
    for figi in figis:
      if 'BBG' in figi:
        self._figi = figi
        break
    if not self._figi:
      self._figi = figis[0]
  
  @property
  def ticker(self):
    return self._ticker

  @ticker.setter
  def ticker(self, ticker: str):
    self._ticker = ticker

  @property
  def ticker_type(self):
    return self._ticker_type

  @ticker_type.setter
  def ticker_type(self, ticker_type: str):
    self._ticker_type = ticker_type

  @property
  def file_name(self):
    if not self.ticker or not self.figi:
      raise Exception('Ticker and figi must be set')
    return f'{self.ticker}_{self.figi}'

  @property
  def csv_name(self):
    return f'{self.file_name}.csv'

  @property
  def zip_name(self):
    return f'{self.file_name}.zip'

  @property
  def path(self):
    if not self.ticker or not self.figi or not self.ticker_type:
      raise Exception('Ticker, figi and ticker_type must be set')
    if not os.path.exists(self.parent_folder_path):
      os.mkdir(self.parent_folder_path)
    return os.path.join(
      LocalStorage.get_local_storage().get('folder_path'), 
      self.ticker_type, 
      self.csv_name)

  @property
  def parent_folder_path(self):
    if not self.ticker_type:
      raise Exception('ticker_type must be set')
    return os.path.join(
      LocalStorage.get_local_storage().get('folder_path'), 
      self.ticker_type)

  @property
  def csv_file_exists(self):
    return os.path.exists(self.path)
  
  @property
  def df(self):
    if not self.csv_file_exists:
      raise Exception('csv file does not exist')
    if not self._df:
      self.load_df()
    return self._df
  
  def load_df(self):
    self._df = TickerDataDataframe(self.path)

  @property
  def last_candle(self):
    return self.df.last_candle

  @property
  def last_candle_date(self):
    return self.df.last_candle_date

  @property
  def last_candle_year(self):
    return int(self.last_candle_date.split('/')[2])

  def update_dataframe(self, df):
    return self.df.update_df(df)

  def save_new_dataframe(self, df):
    _df = TickerDataDataframe(self.path)
    _df.save_df_to_file(df)
    self.load_df()
 
class InstrumentsService:
  def __init__(self, token):
    self.token = token
    self.instruments: pd.DataFrame = None
    self.load()
  
  def load(self):
    with Client(self.token, target=INVEST_GRPC_API) as cl:
      instruments = cl.instruments
 
      l = []
      for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
        for item in getattr(instruments, method)(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments:
        #for item in getattr(instruments, method)().instruments: #instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL
          l.append({
            'ticker': item.ticker,
            'figi': item.figi,
            'type': method,
            'name': item.name,
            'lot': item.lot,
          })
 
      df = pd.DataFrame(l)

      self.instruments = df

  def find_figi_by_ticker(self, ticker_obj: TickerData):
    # get figis by ticker and type
    figis = self.instruments[(self.instruments["ticker"] == ticker_obj.ticker) & (self.instruments["type"] == ticker_obj.ticker_type)]["figi"].tolist()
    if len(figis) == 0:
      return None
    ticker_obj.figi = figis
    return ticker_obj

  def find_ticker_by_figi(self, ticker_obj):
    # get ticker by figi
    tickers = self.instruments[self.instruments["figi"] == ticker_obj.figi]["ticker"].tolist()
    if len(tickers) == 0:
      return None
    ticker_obj.ticker = tickers[0]
    # get ticker type by figi
    ticker_types =  self.instruments[self.instruments["figi"] == ticker_obj.figi]["type"].tolist()
    if len(ticker_types) == 0:
      return None
    ticker_obj.ticker_type = ticker_types[0]
    return ticker_obj

  def find_lot_by_figi(self, figi):
    # get lot by figi
    lots = self.instruments[self.instruments["figi"] == figi]["lot"].tolist()
    if len(lots) == 0:
      return None
    return lots[0]

class DataLoader:
  def __init__(self, token):
    self.token = token

  def load_by_figi(self, ticker_obj: TickerData, instrument_service: InstrumentsService):
    print(f'Load by figi {ticker_obj.figi}')
    ticker_obj = instrument_service.find_ticker_by_figi(ticker_obj)
    if ticker_obj is not None:
      self.update_data(ticker_obj)
    else:
      print(f'Figi not found')

  def load_by_ticker(self, ticker_obj: TickerData, instrument_service: InstrumentsService):
    print(f'Load by ticker {ticker_obj.ticker}')
    # get figi
    ticker_obj = instrument_service.find_figi_by_ticker(ticker_obj)

    if ticker_obj is not None:
      self.update_data(ticker_obj)
    else:
      print(f'Ticker not found')

  def update_data(self, ticker_obj: TickerData):
    '''
    Update data for ticker_obj. If csv file exists, then update it, else download all data
    
    ticker_obj: TickerData
    
    return: None'''
    if ticker_obj.csv_file_exists:
      self.update_ticker(ticker_obj)
    else:
      self.download_all_data(ticker_obj)

  def get_standard_prices_form(self, df):
    # set moscow timezone for datetime column
    df['datetime'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert('Europe/Moscow')

    # split datetime column to date and time columns
    df['date'] = df['datetime'].dt.strftime('%m/%d/%Y')
    df['time'] = df['datetime'].dt.strftime('%H:%M:%S')

    # remove datetime column
    df = df.drop(columns=['datetime'])
    return df

  def download_all_data(self, ticker_obj: TickerData):
    start_year = LocalStorage.get_config().get('start_year')
    current_year = datetime.now().year

    datasets = []

    for year in range(start_year, current_year + 1):
      df = self.download_year_data(year, ticker_obj)
      datasets.append(df)
      
    df = pd.concat(datasets)

    df = self.get_standard_prices_form(df)

    # if df is not empty
    if not df.empty:
      ticker_obj.save_new_dataframe(df)

  def download_year_data(self, year, ticker_obj: TickerData):
    data = req.get(
      f'https://invest-public-api.tinkoff.ru/history-data?figi={ticker_obj.figi}&year={year}', 
      headers={'Authorization': f'Bearer {self.token}'}
    )

    if data.status_code == 200:
      # get buffer folder absolute path
      buffer_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../buffer')
      # get buffer zip file absolute path
      buffer_zip_file_path = os.path.join(buffer_folder_path, ticker_obj.zip_name)
      # get buffer data folder
      buffer_data_folder = os.path.join(buffer_folder_path, ticker_obj.file_name)
      # create buffer folder if not exists
      if not os.path.exists(buffer_folder_path):
        os.mkdir(buffer_folder_path)
      # create zip file
      with open(buffer_zip_file_path, 'wb') as f:
        f.write(data.content)
      # check if file is empty
      if os.path.getsize(buffer_zip_file_path) == 0:
        os.remove(buffer_zip_file_path)
        return pd.DataFrame(columns=['datetime', 'open', 'close', 'high', 'low', 'volume'])
      # unzip file
      with zipfile.ZipFile (buffer_zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(buffer_data_folder)
      # remove zip file
      os.remove(buffer_zip_file_path)
      try:
        # read all files from folder
        files = os.listdir(buffer_data_folder)
      except Exception as e:
        return pd.DataFrame(columns=['datetime', 'open', 'close', 'high', 'low', 'volume'])
      # concat all files
      df = pd.concat([
        pd.read_csv(
          os.path.join(buffer_data_folder, file), 
          sep=';',
          names=['datetime', 'open', 'close', 'high', 'low', 'volume'],
          usecols=[1,2,3,4,5,6]
        ) for file in files
      ])
      # remove folder even if it is not empty
      for file in files:
        os.remove(os.path.join(buffer_data_folder, file))
      os.rmdir(buffer_data_folder)

      return df
    elif data.status_code == 429:
      print('Too many requests')
      time.sleep(5)
      return self.download_year_data(year, ticker_obj)
    elif data.status_code == 401:
      print('Unauthorized')
      raise Exception('Unauthorized')
    elif data.status_code == 404:
      print(f'Not found: {ticker_obj.figi} {year}')
      return pd.DataFrame(columns=['datetime', 'open', 'close', 'high', 'low', 'volume'])
    else:
      print('Unknown error')
      raise Exception('Unknown error')
    
  def update_ticker(self, ticker_obj: TickerData):    
    # download data for each year from last candle date to current date inclusive
    for year in range(ticker_obj.last_candle_year, datetime.now().year + 1):
      df = self.download_year_data(year, ticker_obj)
      df = self.get_standard_prices_form(df)
      ticker_obj.update_dataframe(df)
    

class TinkoffApi:
  def __init__(self):
    self.token = LocalStorage.get_local_storage().get('token')
    if self.token:
      try:
        self.instruments_service = InstrumentsService(self.token)
      except Exception as e:
        print(e)
        self.instruments_service = None
        self.token = None
        raise e
    else:
      self.instruments_service = None
  
  def update_token(self):
    self.token = LocalStorage.get_local_storage().get('token')
    if self.token:
      self.instruments_service = InstrumentsService(self.token)
    else:
      self.instruments_service = None

  def update_prices_by_ticker(self, ticker, ticker_type):
    ticker_obj = TickerData(ticker=ticker, ticker_type=ticker_type)
    DataLoader(self.token).load_by_ticker(ticker_obj, self.instruments_service)

  def update_prices_by_figi(self, figi):
    ticker_obj = TickerData(figi=figi)
    DataLoader(self.token).load_by_figi(ticker_obj, self.instruments_service)
  