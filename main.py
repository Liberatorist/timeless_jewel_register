from datetime import datetime
import json
import sqlite3 as sl
from flask import Flask, jsonify, render_template, request, send_file

from trade_crawler import Jewel, get_prices, initialize_scheduler

app = Flask(__name__)

with open("data/steiner_solutions.json", "r") as file:
    steiner_solutions = json.loads(file.read())

with open("static/tree.json", "r") as file:
    tree = json.loads(file.read())

with open("data/jewel_slots.json", "r") as file:
    jewel_slots = json.loads(file.read())

 
def get_price(type, seed):
    return None, datetime.utcnow()

class Jewel:
    def __init__(self, id, price, last_seen, seed, type, slot, effect, ie, anoint, cost, **kwargs):
        self.id = id
        self.seed = seed
        self.type = type
        self.position = slot
        self.price = price
        self.last_seen = last_seen
        self.effect = effect
        self.ie = ie[0] if ie else None
        self.anoint = True if anoint else False
        self.point_cost = cost
        self.effect_pp = round(effect/cost, 2)



def get_human_readable_time_diff(last_date):
    diff = (datetime.utcnow() - datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S.%f')).seconds
    if (seconds := diff) < 60:
        return f"{seconds} second{'s' if seconds > 1 else ''} ago"
    elif (minutes := round(diff / 60)) < 60:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif (hours := round(minutes / 60)) < 24:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    days = round(hours / 24)
    return f"{days} day{'s' if round(days) > 1 else ''} ago"


def get_last_update():
    return get_human_readable_time_diff(str(datetime.utcnow()))
    # con = sl.connect('jewels.db')
    # with con:
    #     for update in con.execute("SELECT time FROM LAST_UPDATE"):
    #         return get_human_readable_time_diff(update[0])


def get_all_jewels():
    jewel_prices, ie_prices = get_prices()
    jewels = []
    for id, solution in enumerate(steiner_solutions):
        p = jewel_prices[(solution["type"], solution["seed"])]
        price = p["price"] if p["price"] else ""
        last_seen = p["last_seen"]
        if solution["ie"] and price and ie_prices[solution["ie"][0]]["price"]:
            price = price + ie_prices[solution["ie"][0]]["price"]
        jewels.append(Jewel(id=id, price=price, last_seen=last_seen, **solution))
    return jewels


@app.route('/',methods = ['GET'])
def endpoint():
    return render_template("basic_table.html", table=get_all_jewels(), last_update=get_last_update())

 
@app.route('/',methods = ['POST'])
def post():
    solution = steiner_solutions[int(request.json["id"])]
    return jsonify({
        "jewel_id": jewel_slots[solution["type"]][solution["slot"]]["jewel_hash"],
        "keystone_id": solution["ie"][0] if solution["ie"] else None,
        "active_nodes": solution["steiner_tree"],
        "important_nodes": solution["aura_nodes"]
    })

@app.route('/tree.json')
def get_json():
    return jsonify(tree)



@app.route('/dump')
def dump_db():
    return send_file('jewels.db', as_attachment=True)


with app.app_context():
    initialize_scheduler()

if __name__ == '__main__':
    app.run()
