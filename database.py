from collections import defaultdict
from datetime import datetime
import json
import os
import sqlite3 as sl


def connect_to_db():
    return sl.connect('trade.db')


def get_jewels():
    con = connect_to_db()
    with con:
        response = con.execute("SELECT * FROM JEWELS ORDER BY price")
    for r in response:
        yield Jewel(*r)


def get_impossible_escapes():
    con = connect_to_db()
    with con:
        response = con.execute("SELECT * FROM IMPOSSIBLE_ESCAPES ORDER BY price")
    for r in response:
        yield ImpossibleEscape(*r)


def get_prices():
    con = connect_to_db()
    prices = {"timeless": defaultdict(dict), "ie": defaultdict(dict)}
    with con:
        jewels = con.execute("SELECT * FROM JEWELS ORDER BY price")
        for jewel in jewels:
            prices["timeless"][jewel[1]][jewel[0]] = [jewel[3], jewel[2]]
        impossible_escapes = con.execute("SELECT * FROM IMPOSSIBLE_ESCAPES ORDER BY price")
        for ie in impossible_escapes:
            prices["ie"][ie[0]] = [ie[3], ie[2]]
    return prices

class Jewel:
    def __init__(self, seed, type, last_seen, price):
        self.seed = seed
        self.type = ["Brutal Restraint","Glorious Vanity","Elegant Hubris"][type]
        self.last_seen = datetime.strptime(last_seen, '%Y-%m-%d %H:%M') if last_seen else None
        self.price = float(price) if (price is not None and price != "None") else None


class ImpossibleEscape:
    def __init__(self, keystone, name, last_seen, price):
        self.keystone = keystone
        self.name = name
        self.last_seen = datetime.strptime(last_seen, '%Y-%m-%d %H:%M:%S.%f') if last_seen else None
        self.price = float(price) if (price is not None and price != "None") else None

def update_jewels(data):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    con = connect_to_db()
    with con:
        for jewel in data:
            price, seed, jewel_type = jewel
            sql_query = f'UPDATE JEWELS SET price = {price}, last_seen = "{now}" WHERE seed={seed} AND type={jewel_type};'
            con.execute(sql_query)
    con.commit()


def update_ie(data):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    # now = datetime.strptime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')
    con = connect_to_db()
    with con:
        for ie in data:
            price, keystone = ie
            sql_query = f'UPDATE impossible_escapes SET price = {price}, last_seen = "{now}" WHERE name = "{keystone}";'
            con.execute(sql_query)
    con.commit()

def initialise_db():
    os.remove("trade.db")
    con = connect_to_db()
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS jewels (
                seed INTEGER NOT NULL,
                type INTEGER NOT NULL,
                last_seen DATETIME,
                price REAL,
                PRIMARY KEY (seed, type)
            );
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS impossible_escapes (
                keystone INTEGER NOT NULL,
                name TEXT NOT NULL,
                last_seen DATETIME,
                price REAL,
                PRIMARY KEY (name)
            );
        """)
        timeless_jewels = {0: set(), 1: set(), 2: set()}
        impossible_escapes = set()

        with open("static/compressed_solutions.json", "r") as file:
            for solution in json.loads(file.read())["solutions"]:
                timeless_jewels[solution[1]].add(solution[0])
                if solution[8]:
                    impossible_escapes.add(solution[8])

        for jewel_type, seeds in timeless_jewels.items():
            for seed in seeds:
                con.execute(f'INSERT OR IGNORE INTO jewels (seed, type) VALUES ({seed}, {jewel_type});')
        with open("data/tree_data.json", "r") as file:
            tree_data = json.loads(file.read())
        for keystone_id in impossible_escapes:
            con.execute(f'INSERT OR IGNORE INTO impossible_escapes (keystone, name) VALUES ("{keystone_id}", "{tree_data["nodes"][str(keystone_id)]["name"]}");')
    con.commit() 


def update_db(data):
    update_jewels(data["jewels"])
    update_ie(data["ie"])

if __name__ == "__main__":
    initialise_db()