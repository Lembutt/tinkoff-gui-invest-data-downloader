from tkinter import *
from tkinter import ttk, filedialog
from utils import LocalStorage, TinkoffApi
import winsound

tinkoff_api = TinkoffApi()

root = Tk()
root.title("Tinkoff Stock Data")

root.geometry("600x400")
root.resizable(False, False)

local_storage = LocalStorage.get_local_storage()

def choose_folder():
  folder_path = filedialog.askdirectory()
  folder_path_entry.delete(0, END)
  folder_path_entry.insert(0, folder_path)
  local_storage.set('folder_path', folder_path)

def update_ticker():
  try:
    status_label_text = StatusText()
    ticker = ticker_entry.get()
    ticker_type = ticker_type_combobox.get()
    if ticker and ticker_type:
      tinkoff_api.update_prices_by_ticker(ticker, ticker_type)
    else:
      print("Ticker or ticker type is empty")

    status_label_text.set_text(f"Ticker {ticker} of type {ticker_type} updated")
  except Exception as e:
    print(e)
    status_label_text.set_text(f"Error: {e}")
    winsound.Beep(100, 600)

# Create a main frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

# Create folder path label
folder_path_label = ttk.Label(main_frame, text="Folder path", width=15)
folder_path_label.grid(row=0, column=0, sticky=W)

# Create folder path entry
folder_path_entry = ttk.Entry(main_frame, width=45, )
folder_path_entry.grid(row=0, column=1, sticky=W, columnspan=2)

try:
  default_folder_path = local_storage.get('folder_path')
except:
  default_folder_path = './data'

folder_path_entry.delete(0, END)
folder_path_entry.insert(0, '')

# Create folder choose button
folder_choose_button = ttk.Button(main_frame, text="Choose folder", command=choose_folder)
folder_choose_button.grid(row=0, column=3, sticky=W)

# Create label from ttk
ticker_label = ttk.Label(main_frame, text="Choose ticker", width=15)
ticker_label.grid(row=1, column=0, sticky=W)

# Create ticker entry
ticker_entry = ttk.Entry(main_frame, width=20)  
ticker_entry.grid(row=1, column=1, sticky=W)

# Create ticker type combobox
ticker_type_combobox = ttk.Combobox(main_frame, width=20, state="readonly")
ticker_type_combobox["values"] = ("shares", "futures", "currencies", "bonds", "etfs")
ticker_type_combobox.current(0)
ticker_type_combobox.grid(row=1, column=2, sticky=W)

# Create ticker choose button
ticker_choose_button = ttk.Button(main_frame, text="Update Ticker", command=update_ticker)
ticker_choose_button.grid(row=1, column=3, sticky=W)

# Create status label
status_label = ttk.Label(main_frame, text="Status: ")
status_label.grid(row=2, column=0, sticky=W)

# Create current status
current_status_label = ttk.Label(main_frame, text="Waiting for action")
current_status_label.grid(row=2, column=1, sticky=W, columnspan=3)

# Create token label
token_label = ttk.Label(main_frame, text="Token: ")
token_label.grid(row=3, column=0, sticky=W)

# Create token entry
token_entry = ttk.Entry(main_frame, width=45)
token_entry.grid(row=3, column=1, sticky=W, columnspan=2)

# Create token save button
def save_token():
  try:
    token = token_entry.get()
    local_storage.set('token', token)
    status_label_text = StatusText()
    status_label_text.set_text("Token saved")
    tinkoff_api.update_token()
  except Exception as e:
    print(e)
    status_label_text = StatusText()
    status_label_text.set_text(f"Token Entry Error")
    winsound.Beep(100, 600)

token_save_button = ttk.Button(main_frame, text="Save token", command=save_token)
token_save_button.grid(row=3, column=3, sticky=W)


class StatusText:
  def __init__(self):
    self.text = current_status_label.cget("text")

  def set_text(self, text):
    self.text = text
    current_status_label.config(text=text)

  def get_text(self):
    return self.text  

root.mainloop()
