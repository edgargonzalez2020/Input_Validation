#!/usr/bin/env python3
import sqlite3 as sql

db = sql.connect('people.db')
c = db.cursor()
c.execute('SELECT * FROM people')
print(c.fetchall())
