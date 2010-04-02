import sqlite3

conn = sqlite3.connect('radioreference.db')
c = conn.cursor()

schema = '''CREATE TABLE IF NOT EXISTS trs_info (
    sid INTEGER PRIMARY KEY,
    name TEXT,
    type INT,
    lastupdated TEXT);
CREATE TABLE IF NOT EXISTS trs_freq (
    sid INT,
    site_id INT,
    use TEXT,
    freq TEXT);
CREATE TABLE IF NOT EXISTS trs_type (
    id INTEGER PRIMARY KEY,
    name TEXT);
CREATE TABLE IF NOT EXISTS trs_sites (
    id INTEGER PRIMARY KEY,
    sid INT,
    tone TEXT,
    description TEXT);
CREATE TABLE IF NOT EXISTS trs_talkgroup (
    id INTEGER PRIMARY KEY,
    sid INT,
    decid INT,
    alpha TEXT,
    description TEXT,
    mode TEXT);
'''

c.executescript(schema)
c.close()
