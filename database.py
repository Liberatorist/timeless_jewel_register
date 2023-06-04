from collections import defaultdict
from datetime import datetime
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
    print(prices)
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


def update_db(data):
    update_jewels(data["jewels"])
    update_ie(data["ie"])