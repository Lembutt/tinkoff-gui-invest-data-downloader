from tinkoff.invest import Client, InstrumentStatus
from tinkoff.invest.constants import INVEST_GRPC_API
from . import LocalStorage
import pandas as pd
from datetime import datetime
import os, json, requests as req, zipfile, gzip

def get_current_year():
  return datetime.now().year

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
        for item in getattr(instruments, method)().instruments: #instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL
          l.append({
            'ticker': item.ticker,
            'figi': item.figi,
            'type': method,
            'name': item.name,
          })
 
      df = pd.DataFrame(l)

      self.instruments = df

  def find_figi_by_ticker(self, ticker, ticker_type):
    return self.instruments[(self.instruments["ticker"] == ticker) & (self.instruments["type"] == ticker_type)].iloc[0]["figi"]

class DataLoader:
  def __init__(self, token):
    self.token = token

  def remove_non_trading_days(self, df):
    # remove non trading days
    trade_calendar = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../util-data/trade-calendar.csv'), names=['date', 'is_holiday'])
    # convert date string from '%Y-%m-%d' to '%m/%d/%Y' string
    trade_calendar['date'] = trade_calendar['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))
    # remove non trading days
    df = df[~df['date'].isin(trade_calendar[trade_calendar['is_holiday'] == 1]['date'])]
    return df

  def load_by_ticker(self, ticker, ticker_type, instrument_service: InstrumentsService):
    print(f'Loading {ticker} {ticker_type} data')
    figi = instrument_service.find_figi_by_ticker(ticker, ticker_type)
    exists = self.check_ticker_existance(ticker, ticker_type)
    print(f'Exists: {exists}')
    if exists:
      
      data = pd.read_csv(
        self.get_ticker_path(ticker, ticker_type),
        names=['date', 'time', 'open', 'close', 'high', 'low', 'volume']
      )
      # get last candle
      last_candle = data.iloc[-1]
      # get last candle date
      last_candle_date = datetime.strptime(last_candle['date'], '%m/%d/%Y')
      # get current date
      current_date = datetime.now()
      
      # download data for each year from last candle date to current date inclusive
      for year in range(last_candle_date.year, current_date.year + 1):
        print(f'Loading {ticker} {ticker_type} data for {year}')
        # get filename
        filename = f'{figi}_{year}'
        # download year data
        df = self.download_year_data(year, figi, filename)
        # get standard prices form
        df = self.get_standard_prices_form(df)
        # add unique rows to data by date and time
        data = pd.concat([data, df]).drop_duplicates(subset=['date', 'time'], keep='last')
      # remove ticker file
      os.remove(self.get_ticker_path(ticker, ticker_type))
      # save data to ticker file
      self.remove_non_trading_days(data).to_csv(
        self.get_ticker_path(ticker, ticker_type), 
        index=False,
        columns=['date', 'time', 'open', 'close', 'high', 'low', 'volume'],
        header=False
      )
    else:
      df = self.download_all_data(figi).drop_duplicates(subset=['date', 'time'], keep='last')
      self.remove_non_trading_days(df).to_csv(
        self.get_ticker_path(ticker, ticker_type), 
        index=False,
        columns=['date', 'time', 'open', 'close', 'high', 'low', 'volume'],
        header=False
      )

  def get_standard_prices_form(self, df):
    # set moscow timezone for datetime column
    df['datetime'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert('Europe/Moscow')

    # split datetime column to date and time columns
    df['date'] = df['datetime'].dt.strftime('%m/%d/%Y')
    df['time'] = df['datetime'].dt.strftime('%H:%M:%S')

    # remove datetime column
    df = df.drop(columns=['datetime'])
    return df

  def download_all_data(self, figi):
    # get start year
    start_year = LocalStorage.get_config().get('start_year')

    # get current year
    current_year = get_current_year()

    # list of datasets
    datasets = []
    # download data for each year
    for year in range(start_year, current_year + 1):
      print(f'Loading {figi} data for {year}')
      # get filename
      filename = f'{figi}_{year}'
      # download year data
      df = self.download_year_data(year, figi, filename)
      # save data to datasets
      datasets.append(df)
      
    # concat all datasets
    df = pd.concat(datasets)

    # get standard prices form
    df = self.get_standard_prices_form(df)

    return df

  def download_year_data(self, year, figi, filename):
    # get zip file
    data = req.get(
      f'https://invest-public-api.tinkoff.ru/history-data?figi={figi}&year={year}', 
      headers={'Authorization': f'Bearer {self.token}'}
    )
    # get buffer folder absolute path
    buffer_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../buffer')
    # get buffer zip file absolute path
    buffer_zip_file_path = os.path.join(buffer_folder_path, f'{filename}.zip')
    print()
    # get buffer data folder
    buffer_data_folder = os.path.join(buffer_folder_path, filename)

    print(buffer_folder_path)
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

    # read all files from folder
    files = os.listdir(buffer_data_folder)

    # concat all files
    df = pd.concat([
      pd.read_csv(
        os.path.join(buffer_data_folder, file), 
        sep=';',
        names=['datetime', 'open', 'close', 'high', 'low', 'volume'],
        usecols=[1,2,3,4,5,6]
      ) for file in files
    ])
    print(df.head(5))

    # remove folder even if it is not empty
    for file in files:
      os.remove(os.path.join(buffer_data_folder, file))
    os.rmdir(buffer_data_folder)

    return df

  def get_ticker_path(self, ticker, ticker_type):
    # create ticker_type folder if not exists
    if not os.path.exists(os.path.join(LocalStorage.get_local_storage().get('folder_path'), ticker_type)):
      os.mkdir(os.path.join(LocalStorage.get_local_storage().get('folder_path'), ticker_type))
    # return ticker path
    return os.path.join(LocalStorage.get_local_storage().get('folder_path'), ticker_type, f'{ticker}.csv')

  def check_ticker_existance(self, ticker, ticker_type):
    data_path = self.get_ticker_path(ticker, ticker_type)
    return os.path.exists(data_path) 

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
    else:
      self.instruments_service = None
  
  def update_token(self):
    self.token = LocalStorage.get_local_storage().get('token')
    if self.token:
      self.instruments_service = InstrumentsService(self.token)
    else:
      self.instruments_service = None

  def update_prices_by_ticker(self, ticker, ticker_type):
    DataLoader(self.token).load_by_ticker(ticker, ticker_type, self.instruments_service)
  