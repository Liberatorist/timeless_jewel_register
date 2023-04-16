import atexit
import datetime
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


class Jewel:
    def __init__(self, id, seed, type, version, position, effect, points_base, points_to_jewel, points_w_anoint,
                 points_w_ie, url_hash, last_queried, price):
        self.id = id
        self.seed = seed
        self.type = type
        self.version = version
        self.position = position
        self.effect = effect
        self.points_base = points_base
        self.points_to_jewel = points_to_jewel
        self.points_w_anoint = points_w_anoint
        self.points_w_ie = points_w_ie
        self.url_hash = url_hash
        self.last_queried = last_queried
        self.price = price


versions = {
    "Glorious Vanity": ["xibaqua", "doryani", "ahuana"],
    "Brutal Restraint": ["asenath", "balbala", "nasima"],
    "Elegant Hubris": ["cadiro", "caspiro", "victario"]
}


def get_price_in_div(result):
    price_data = result["listing"]["price"]
    div_price = 180
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
            # print(f"sleeping for {interval}s")
            time.sleep(int(interval))
            return


def make_request(url, method, data=None):
    if method == "GET":
        global policies_get, current_states_get
        wait_for_request(policies_get, current_states_get)

        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code > 399:
            raise ConnectionError
        policies_get, current_states_get = response.headers["X-Rate-Limit-Ip"], response.headers["X-Rate-Limit-Ip-State"]

    elif method == "POST":
        global policies_post, current_states_post
        wait_for_request(policies_post, current_states_post)
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        if response.status_code > 399:
            raise ConnectionError
        policies_post, current_states_post = response.headers["X-Rate-Limit-Ip"], response.headers["X-Rate-Limit-Ip-State"]
    else:
        return None
    return response


def trade_post(jewels: List[Jewel]):
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


def trade_fetch(jewels: List[Jewel]):
    response = trade_post(jewels)
    url_hash = response.json()["id"]
    results = response.json()["result"]
    prices = {(jewel.type, str(jewel.seed)): None for jewel in jewels}
    for items in [','.join(results[n: n + 10]) for n in range(0, len(results), 10)]:
        url = f"https://www.pathofexile.com/api/trade/fetch/{items}?query={url_hash}"
        response = make_request(url, "GET")
        for result in response.json()["result"]:
            seed = re.findall('\d+', result["item"]["explicitMods"][0])[0]
            price = get_price_in_div(result)
            jewel_type = result["item"]["name"]
            if prices[(jewel_type, seed)] is None:
                prices[(jewel_type, seed)] = price
        if all(price is not None for price in prices.values()):
            break
    return prices

def set_last_update():
    con = sl.connect('jewels.db')
    with con:
        con.execute(f"UPDATE LAST_UPDATE SET time = '{datetime.datetime.utcnow()}' where id=0")


def update_all_jewels():
    start_time = datetime.datetime.utcnow()
    print(f"Starting update at {start_time}")
    con = sl.connect('jewels.db')
    with con:
        for jewel_data in con.execute("SELECT * FROM JEWEL WHERE url_hash is NULL"):
            jewel = Jewel(*jewel_data)
            response = trade_post([jewel])
            url_hash = response.json()["id"]
            sql_query = f'UPDATE JEWEL SET url_hash = "{url_hash}" WHERE id={jewel.id};'
            con.execute(sql_query)

    with con:
        jewels = [Jewel(*jewel_data) for jewel_data in con.execute("SELECT * FROM JEWEL")]
        k = 12
        for jewels_subset in [jewels[n: n + k] for n in range(0, len(jewels), k)]:
            for (jewel_type, seed), price in trade_fetch(jewels_subset).items():
                if price is not None:
                    sql_query = f'UPDATE JEWEL SET price = "{price}", last_queried = "{datetime.datetime.utcnow()}" WHERE seed={seed} AND type="{jewel_type}";'
                    con.execute(sql_query)
    set_last_update()
    print(f"Finished updates at {datetime.datetime.utcnow()} after {(datetime.datetime.utcnow() - start_time).seconds}s")


def initialize_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_all_jewels, trigger="interval", minutes=10)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    initialize_scheduler()
