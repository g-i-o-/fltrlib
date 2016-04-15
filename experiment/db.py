from paths import paths
import sqlite3

def get_db():
    db = sqlite3.connect(paths.DATABASE)
    db.row_factory = dict_factory
    return db

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
