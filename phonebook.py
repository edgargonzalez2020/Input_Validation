import sys
import os 
import sqlite3 
import re

def err(*args, **kwargs):
  print(*args, file=sys.stderr)
  sys.exit(int(kwargs['exit_code']))
def main():
    argc = len(sys.argv) - 1
    parser = Parser(argc, sys.argv[1:])
    person = Person(command = parser.command, first = parser.first, middle
    = parser.middle, last = parser.last, number = parser.number)
class Parser:
  def __init__(self, argc = None, raw_command_args = None):
    self.argc = argc
    self.raw_command = raw_command_args
    self._init()
    self.validate_args()
  def _init(self):
    if self.argc == 0: 
      self.command = "HELP"
    elif self.argc == 1 and self.raw_command[0].lower() == "list":
      self.command = "LIST"
    elif self.argc == 2 and self.raw_command[0].lower() == "del":
      self.command = "DEL"
    elif self.argc == 3 and self.raw_command[0].lower() == "add":
      self.command = "ADD"
    else:
      err("Invalid operation", exit_code = 1)
  def validate_args(self):
    name = number = name_or_num = None
    if self.command == "ADD":
      name, number = self.raw_command[1:]
    elif self.command == "DEL":
      name_or_num = self.raw_command[1]
    if name is not None and number is not None:
      is_name_valid = self.validate_name(name)
      is_number_valid = self.validate_number(number)
      print(is_name_valid, is_number_valid)
      if is_name_valid and is_number_valid:
        self.first, self.middle, self.last = self.get_name(name)
        self.number = number
      else:
        err("Invalid argument(s) given", exit_code = 1)
    else:
      is_name_valid = self.validate_name(name_or_num)
      is_number_valid = self.validate_number(name_or_num)
      if is_name_valid:
        self.first, self.middle, self.last = self.get_name(name)
      elif is_number_valid:
        self.number = number
      else:
        err("Invalid argument(S) given", exit_code = 1)
    print(self.first, self.middle, self.last)
  def get_name(self, name):
    first = middle = last = None
    if ',' in name:
      idx = name.index(',')
      last = name[:idx].strip()
      if len(name[idx + 1:].lstrip().split(' ')) > 2:
        err("Invalid argument(s) given", exit_code = 1)
      first = name[idx + 1:].lstrip().split(' ')[0]
      middle = name[idx + 1:].lstrip().split(' ')[1] if len(name[idx+1:].lstrip().split(' ')) == 2 else None
      first = first.strip()
      last = last.strip()
    else:
      size = len(name.split(' '))
      if size == 1:
        first = name.strip()
      elif size == 2:
        first, last = name.split(' ')
        first = first.strip()
        last = last.strip()
      elif size == 3:
        first, middle, last = name.split(' ')
        first = first.strip()
        middle = middle.strip()
        last = last.strip()
    return first, middle, last
  def validate_name(self, name):
    return bool(re.match("^[a-zA-Z ,.'-]+$", name))
  def validate_number(self, number):
    return bool(re.match("^(?:(?:\(?(?:00|\+)([1-4]\d\d|[1-9]\d?)\)?)?[\-\.\\\\/]?)?((?:\(?\d{1,}\)?[\-\.\\\\/]?){0,})(?:[\-\.\\\\/]?(?:#|ext\.?|extension|x)[\-\.\\\\/]?(\d+))?$", number))
class Person:
  def __init__(self,command = None, first = None, middle = None, last = None,
  number = None):
    self.number = number
    self.command = command
    self.first = first
    self.middle = middle
    self.last = last
    self.init_db()
    self.handle_flow()
  def init_db(self):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "people.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS people (first text, middle text,last text,number text)''')
    conn.commit()
    self.conn = conn
  def handle_flow(self):
    if self.command == "ADD":
      self.add()
    elif self.command == "DEL":
      self.delete()
  def add(self):
    if self.first and self.middle and self.last:
      c = self.conn.cursor()
      c.execute('INSERT INTO people (first, middle, last, number) VALUES (?,?,?,?);', (self.first, self.middle, self.last, self.number,))
    elif self.first and self.last:
      c = self.conn.cursor()
      c.execute('INSERT INTO people (first,last, number) VALUES (?,?,?);',(self.first, self.last, self.number,))
    elif self.first:
      c.execute('INSERT INTO people (first, number) VALUES (?,?);', (self.first, self.number,))
    self.conn.commit()
  def delete(self):
    pass
if __name__ == '__main__':
  main()
