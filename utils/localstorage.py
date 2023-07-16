import json
import os

def get_config_path():
  return os.path.join(os.path.dirname(__file__), '../storage', 'config.json')

def get_config():
  return LocalStorage(get_config_path())

def get_local_storage_path():
  return os.path.join(os.path.dirname(__file__), '../storage', 'localstorage.json')

def get_local_storage():
  return LocalStorage(get_local_storage_path())

class LocalStorage:
  def __init__(self, path):
    self.path = path
    self.data = {}
    self.load()

  def load(self):
    if os.path.exists(self.path):
      with open(self.path, 'r') as f:
        self.data = json.load(f)

  def save(self):
    with open(self.path, 'w') as f:
      json.dump(self.data, f)

  def get(self, key):
    return self.data.get(key)

  def set(self, key, value):
    self.data[key] = value
    self.save()
  
  @staticmethod
  def get_config():
    return get_config()
  
  @staticmethod
  def get_local_storage():
    return get_local_storage()