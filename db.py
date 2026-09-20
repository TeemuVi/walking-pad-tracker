import sqlite3

def query(sql, params=[]):
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
def execute(sql, params=[]):
    con = sqlite3.connect("database.db")
    con.execute(sql, params)
    con.commit()
    con.close()