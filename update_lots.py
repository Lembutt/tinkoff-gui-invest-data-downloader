import os
import pandas as pd

from utils.tinkoff_api import InstrumentsService
from utils.localstorage import LocalStorage

token = LocalStorage.get_local_storage().get('token')
_is = InstrumentsService(token)

shares = os.listdir('./data/shares/')

for share in shares:
  try:
    figi = share.split('.')[0].split('_')[1]
    df = pd.read_csv(
      f'./data/shares/{share}', 
      names=[
        'date', 
        'time', 
        'open', 
        'close', 
        'high', 
        'low', 
        'volume'
      ]
    )
    lot = _is.find_lot_by_figi(figi)
    df['volume'] = df['volume'] * lot
    df.to_csv(
      f'./updated_lots/{share}', 
      index=False, 
      header=False
    )
  except Exception as e:
    print(share, e)
    continue