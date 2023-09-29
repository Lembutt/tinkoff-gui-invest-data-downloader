from tkinter import *
from utils import LocalStorage, TinkoffApi

from interface import MainView

tinkoff_api = TinkoffApi()

root = Tk()
root.title("Tinkoff Stock Data Downloader")

root.geometry("600x400")
root.resizable(False, False)

local_storage = LocalStorage.get_local_storage()

main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

MainView(main_frame, local_storage, tinkoff_api).draw()

root.mainloop()
