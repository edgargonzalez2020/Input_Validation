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
    self.first = self.middle = self.last = self.number = None
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
    if self.command == "LIST" or self.command == "HELP":
      return 
    name = number = name_or_num = None
    if self.command == "ADD":
      name, number = self.raw_command[1:]
    elif self.command == "DEL":
      name_or_num = self.raw_command[1]
    if name is not None and number is not None:
      is_name_valid = self.validate_name(name)
      is_number_valid = self.validate_number(number)
      if is_name_valid and is_number_valid:
        self.first, self.middle, self.last = self.get_name(name)
        self.number = number
      else:
        err("Invalid argument(s) given", exit_code = 1)
    else:
      is_name_valid = self.validate_name(name_or_num)
      is_number_valid = self.validate_number(name_or_num)
      if is_name_valid:
        self.first, self.middle, self.last = self.get_name(name_or_num)
      elif is_number_valid:
        self.number = name_or_num
      else:
        err("Invalid argument(S) given", exit_code = 1)
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
      if first: first = first.lower()
      if middle: middle = middle.lower()
      if last: last = last.lower()
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
    if self.command == "HELP":
      print("usage: <command> <arguments>")
      print("<command>: ADD | DEL | LIST")
      print("ADD: [name] [phone number]")
      print("DEL: [name] | [phone number]")
      print("LIST: None")
      sys.exit(0)
    elif self.command == "LIST":
      self._list()
    else:  
      self.handle_flow()
  def _list(self):
    c = self.conn.cursor()
    c.execute("SELECT * FROM people;")
    for i, x in enumerate(c.fetchall()):
      string = ""
      if x[0]: string += f'Name: {x[0]} '
      if x[1]: string += f'{x[1]} '
      if x[2]: string += f'{x[2]} '
      string += f'Number: {x[3]}'
      print(string)
  
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
      c = self.conn.cursor()
      c.execute('INSERT INTO people (first, number) VALUES (?,?);', (self.first, self.number,))
    self.conn.commit()
  def delete(self):
    if self.first or self.middle or self.last:
      c = self.conn.cursor()
      if self.first and self.middle and self.last:
        c.execute('SELECT * FROM people WHERE first = ? AND middle = ? AND last = ?;',(self.first, self.middle, self.last, ))
        if len(c.fetchall()) == 0:
          err('Record does not exist', exit_code = 1)
        else:
          c.execute('DELETE FROM people WHERE first = ? AND middle = ? AND last = ?;',(self.first, self.middle, self.last,))
      elif self.first and self.last:
        c.execute('SELECT * FROM people WHERE first = ? AND last = ?;', (self.first, self.last,))
        if len(c.fetchall()) == 0:
          err('Record does not exist', exit_code = 1)
        else:
          c.execute('DELETE FROM people WHERE first = ? AND last = ?;',(self.first, self.last,))
      elif self.first:
        c.execute('SELECT * FROM people WHERE first = ?;', (self.first,))
        if len(c.fetchall()) == 0:
          err('Record does not exist', exit_code = 1)
        else:
          c.execute('DELETE FROM people WHERE first = ?;',(self.first,))
    elif self.number:
      c = self.conn.cursor()
      c.execute('SELECT * FROM people WHERE number = ?;', (self.number, ))
      if len(c.fetchall()) == 0:
        err('Record does not exist', exit_code = 1)
      else:
        c.execute('DELETE FROM people WHERE number = ?;', (self.number,))
    self.conn.commit()
if __name__ == '__main__':
  main()
  sys.exit(0)
