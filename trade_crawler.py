import atexit
import datetime
import json
import re
import time
import sqlite3 as sl
from typing import List

import requests
from apscheduler.schedulers.background import BackgroundScheduler

headers = {
    'content-type': 'application/json',
    'user-agent': 'liberatorist@gmail.com',
}
cookies = {}
current_league = "Crucible"

def connect_to_db():
    return sl.connect('trade.db')

def create_tables():
    con = connect_to_db()
    with con:

        con.execute("""
        CREATE TABLE JEWELS (
            seed INTEGER,
            type TEXT,
            last_seen TEXT,
            price REAL,
            PRIMARY KEY (seed, type)
        )""")
        con.execute("""
        CREATE TABLE IMPOSSIBLE_ESCAPES (
            keystone INTEGER,
            name TEXT,
            last_seen TEXT,
            price REAL,
            PRIMARY KEY (keystone)
        )""")

with open("data/compressed_solutions.json", "r") as file:
    steiner_solutions = json.loads(file.read())
    keys = steiner_solutions["keys"]
    solutions = steiner_solutions["solutions"]
    num2type = steiner_solutions["num2type"]
    num2slot = steiner_solutions["num2slot"]
    key_map = {v: idx for idx, v in enumerate(steiner_solutions["keys"])}
    slot2num = {v: k for k, v in enumerate(steiner_solutions["num2slot"])}
    solutions = [s for s in steiner_solutions["solutions"] if s[key_map["effect"]] / s[key_map["cost"]] >= 2.5]


def fill_tables():
    con = connect_to_db()
    with open("data/skill_tree.json", "r") as file:
        tree = json.loads(file.read())["nodes"]
    keystones = set()
    jewels = set()
    for solution in solutions:
        jewels.add((num2type[solution[key_map["type"]]], solution[key_map["seed"]]))
        if solution[key_map["ie"]]:
            keystones.add(solution[key_map["ie"]])
    with con:
        con.executemany("""
            INSERT INTO JEWELS (type, seed)
            VALUES (?, ?);
            """, list(jewels))

    with con:  
        con.executemany("""
            INSERT INTO IMPOSSIBLE_ESCAPES (keystone, name)
            VALUES (?,?);
            """, [(k, tree[str(k)]["name"]) for k in keystones])



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
    jewel_prices = {(jewel.type, jewel.seed): {"price": jewel.price, "last_seen": jewel.last_seen} for jewel in get_jewels()}
    ie_prices = {ie.keystone: {"price": ie.price, "last_seen": ie.last_seen} for ie in get_impossible_escapes()}
    return jewel_prices, ie_prices

class Jewel:
    def __init__(self, seed, type, last_seen, price):
        self.seed = seed
        self.type = type
        self.last_seen = datetime.datetime.strptime(last_seen, '%Y-%m-%d %H:%M:%S.%f') if last_seen else None
        self.price = float(price) if (price is not None and price != "None") else None

class ImpossibleEscape:
    def __init__(self, keystone, name, last_seen, price):
        self.keystone = keystone
        self.name = name
        self.last_seen = datetime.datetime.strptime(last_seen, '%Y-%m-%d %H:%M:%S.%f') if last_seen else None
        self.price = float(price) if (price is not None and price != "None") else None


versions = {
    "Glorious Vanity": ["xibaqua", "doryani", "ahuana"],
    "Brutal Restraint": ["asenath", "balbala", "nasima"],
    "Elegant Hubris": ["cadiro", "caspiro", "victario"]
}


def get_price_in_div(result):
    price_data = result["listing"]["price"]
    div_price = 220
    if price_data["currency"] == "chaos":
        return round(price_data["amount"] / div_price, 2)
    elif price_data["currency"] == "divine":
        return price_data["amount"]
    return None

current_states_get = ""
current_states_post = ""
policies_get = '12:4:60,16:12:60'
policies_post = '8:10:60,15:60:120,60:300:1800'


def wait_for_request(policies, current_states):
    if not current_states:
        return
    for policy, state in zip(reversed(policies.split(',')), reversed(current_states.split(','))):
        request_limit, interval, _ = policy.split(':')
        current_hits = state.split(':')[0]
        if int(current_hits) >= int(request_limit) - 1:
            print(f"sleeping for {interval}s")
            time.sleep(int(interval))
            return


def make_request(url, method, data=None):
    if method == "GET":
        global policies_get, current_states_get
        wait_for_request(policies_get, current_states_get)

        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code > 399:
            raise ConnectionError(response.text)
        policies_get, current_states_get = response.headers["X-Rate-Limit-Ip"], response.headers["X-Rate-Limit-Ip-State"]

    elif method == "POST":
        global policies_post, current_states_post
        wait_for_request(policies_post, current_states_post)
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        if response.status_code > 399:
            raise ConnectionError(response.text)
        policies_post, current_states_post = response.headers["X-Rate-Limit-Ip"], response.headers["X-Rate-Limit-Ip-State"]
    else:
        return None
    return response


def trade_for_impossible_escapes(impossible_escapes: List[ImpossibleEscape]):
    url = f"https://www.pathofexile.com/api/trade/search/{current_league}"
    query_data = {
        "query":{
            "status":{
                "option":"onlineleague"
            },
            "stats":[
                {
                    "type":"count",
                    "filters":[
                    {
                        "id":"explicit.stat_2422708892",
                        "value":{
                            "option":ie.keystone
                        },
                        "disabled":False
                    } for ie in impossible_escapes
                    ],
                    "value":{
                    "min":1
                    }
                }
            ]
        },
        "sort":{
            "price":"asc"
        }
    }
    return make_request(url, "POST", query_data)


def trade_for_jewels(jewels: List[Jewel]):
    url = f"https://www.pathofexile.com/api/trade/search/{current_league}"
    query_data = {
        "query": {
            "status": {
                "option": "onlineleague"
            },
            "stats": [
                {
                    "type": "count",
                    "filters": [
                        {
                            "id": f"explicit.pseudo_timeless_jewel_{version}",
                            "value": {
                                "min": jewel.seed,
                                "max": jewel.seed
                            },
                            "disabled": False
                        }
                        for jewel in jewels
                        for version in versions[jewel.type]
                    ],
                    "value": {
                        "min": 1
                    }
                }
            ]
        },
        "sort": {
            "price": "asc"
        }
    }
    return make_request(url, "POST", query_data)


def trade_fetch(post_response):
    url_hash = post_response.json()["id"]
    results = post_response.json()["result"]
    for items in [','.join(results[n: n + 10]) for n in range(0, len(results), 10)]:
        url = f"https://www.pathofexile.com/api/trade/fetch/{items}?query={url_hash}"
        response = make_request(url, "GET")
        for result in response.json()["result"]:
            yield result


def update_all_jewels():
    start_time = datetime.datetime.utcnow()
    print(f"Starting jewel update at {start_time}")
    con = connect_to_db()
    with con:
        jewels = list(get_jewels())
        k = 12
        for jewels_subset in [jewels[n: n + k] for n in range(0, len(jewels), k)]:
            seen_already = set()
            post_response = trade_for_jewels(jewels_subset)#
            for result in trade_fetch(post_response):
                seed = re.findall('\d+', result["item"]["explicitMods"][0])[0]
                jewel_type = result["item"]["name"]
                if (seed, jewel_type) in seen_already:
                    continue
                else:
                    price = get_price_in_div(result)
                    if price is None:
                        continue
                    sql_query = f'UPDATE JEWELS SET price = "{price}", last_seen = "{datetime.datetime.utcnow()}" WHERE seed={seed} AND type="{jewel_type}";'
                    con.execute(sql_query)
                    seen_already.add((seed, jewel_type))                
                if len(seen_already) == len(jewels_subset):
                    break

    print(f"Finished jewel updates at {datetime.datetime.utcnow()} after {(datetime.datetime.utcnow() - start_time).seconds}s")

def update_all_impossible_escapes():
    start_time = datetime.datetime.utcnow()
    print(f"Starting IE update at {start_time}")
    con = connect_to_db()
    with con:
        impossible_escapes = list(get_impossible_escapes())
        k = 4
        for impossible_escapes_subset in [impossible_escapes[n: n + k] for n in range(0, len(impossible_escapes), k)]:
            post_response = trade_for_impossible_escapes(impossible_escapes_subset)
            seen_already = set()
            for result in trade_fetch(post_response):
                keystone = re.findall('Passives in Radius of (.*) can be Allocated', result["item"]["explicitMods"][0])[0]
                if keystone in seen_already:
                    continue
                else:
                    price = get_price_in_div(result)
                    if price is None:
                        continue
                    sql_query = f'UPDATE impossible_escapes SET price = "{price}", last_seen = "{datetime.datetime.utcnow()}" WHERE name = "{keystone}";'
                    con.execute(sql_query)
                    seen_already.add(keystone)
                if len(seen_already) == len(impossible_escapes_subset):
                    break
    print(f"Finished IE updates at {datetime.datetime.utcnow()} after {(datetime.datetime.utcnow() - start_time).seconds}s")

def update_all():
    update_all_jewels()
    update_all_impossible_escapes()

def initialize_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_all, trigger="interval", hours=24)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    # con = connect_to_db()
    # r = con.cursor().execute("SELECT * FROM JEWELS")
    # for rr in r:
    #     print(rr)
    update_all_jewels()
    update_all_impossible_escapes()
    # create_tables()
    # fill_tables()
