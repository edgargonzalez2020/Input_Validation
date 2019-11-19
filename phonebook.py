from __future__ import print_function
import sqlite3
import sys
import os
import re
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
def validate_name(name):
  return bool(re.match("^[a-zA-Z ,.'-]+$", name))
def validate_number(number):
  pattern = re.compile(r'''^\+((?:9[679]|8[035789]|6[789]|5[90]|42|3[578]|2[1-689])|9[0-58]|8[1246]|6[0-6]|5[1-8]|4[013-9]|3[0-469]|2[70]|7|1)(?:\W*\d){0,13}\d$''')
  print(number)
  print(pattern.match(number))

def add(conn,command,person, number):
  first = last = MI = None
  if not command == "ADD":
    eprint("Invalid command provided")
    sys.exit(1)
  if ',' in person:
    idx = person.index(',')
    last = person[:idx].strip()
    if len(person[idx + 1:].lstrip().split(' ')) > 2:
      eprint("Invalid argument provided")
      sys.exit(1)
    first = person[idx + 1:].lstrip().split(' ')[0]
    MI = person[idx + 1:].lstrip().split(' ')[1].strip() if len(person[idx + 1:].lstrip().split(' ')[0]) == 2 else None
    first = first.strip()
    last = last.strip()
  else:
    size = len(person.split(' '))
    if size == 2:
      first, last = person.split(' ')
    elif size == 3:
      first , MI, last = person.split(' ')
    else:
      eprint("Invalid argument provided")
      sys.exit(1)
  if validate_number(number) and validate_name(first) and validate_name(last):
    if MI and validate_name(MI):
      #middle_name exists
      pass
    else:
      pass
  else:
    eprint("Invalid arguments given")
    sys.exit(1)
def delete(conn,command,person_or_number):
  person_or_number = person_or_number[1::-1]
  pass
def _help():
  print("HELP")
def _list():
  print("LIST")
def init_db():
  conn = sqlite3.connect('people.db')
  c = conn.cursor()
  if not os.path.isfile('people.db'):
    c.execute('''CREATE TABLE people
             (name text, number text)''')
    conn.commit()
def command(conn, args):
  argc = len(args)
  if argc == 0:
    _help()
  elif argc == 1:
    _list()
  elif argc == 2:
    delete(conn,*args)
  elif argc == 3:
    add(conn,*args)
def main():
  argc = len(sys.argv) - 1
  if argc <= 3 and argc >= 0:
    conn = init_db()
    command(conn,sys.argv[1:])
  else:
    #invalid operaion
    pass
if __name__ == "__main__":
  main()

