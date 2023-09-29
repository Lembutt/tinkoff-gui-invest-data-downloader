from tkinter import *
from tkinter import ttk, filedialog
from .._base import RowComponent

class FolderPathComponent(RowComponent):
  '''
  FolderPathComponent class
  
  This class is responsible for drawing folder path component'''
  def __init__(self, frame, local_storage, row):
    '''
    FolderPathComponent constructor
    
    frame: tkinter.Frame
    local_storage: utils.LocalStorage
    row: int
    '''

    super().__init__(frame, row)
    self.local_storage = local_storage
  
  def choose_folder(self, folder_path_entry, local_storage):
    '''
    Choose folder path. This method is called when user clicks on "Choose folder" button
  
    folder_path_entry: ttk.Entry
    local_storage: utils.LocalStorage

    return: None
    '''
    folder_path = filedialog.askdirectory()
    folder_path_entry.delete(0, END)
    folder_path_entry.insert(0, folder_path)
    local_storage.set('folder_path', folder_path)

  def _draw(self):
    self.create_folder_choose_menu()

  def create_folder_choose_menu(self):
    '''
    Create folder choose menu. This method is responsible for drawing folder choose menu

    return: None
    '''
    # Create folder path label
    folder_path_label = ttk.Label(self.frame, text="Folder path", width=15)
    folder_path_label.grid(row=self.row, column=0, sticky=W)

    # Create folder path entry
    folder_path_entry = ttk.Entry(self.frame, width=45, )
    folder_path_entry.grid(row=self.row, column=1, sticky=W, columnspan=2)

    try:
      default_folder_path = self.local_storage.get('folder_path')
    except:
      default_folder_path = './data'

    folder_path_entry.delete(0, END)
    folder_path_entry.insert(0, '')

    # Create folder choose button
    folder_choose_button = ttk.Button(
      self.frame, 
      text="Choose folder", 
      command=lambda: self.choose_folder(folder_path_entry, self.local_storage))
    folder_choose_button.grid(row=self.row, column=3, sticky=W)
