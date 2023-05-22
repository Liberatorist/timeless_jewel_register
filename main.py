from datetime import datetime
import json
from flask import Flask, jsonify, render_template, request, send_file

from trade_crawler import Jewel, get_prices, initialize_scheduler

app = Flask(__name__)

with open("data/compressed_solutions.json", "r") as file:
    steiner_solutions = json.loads(file.read())
    keys = steiner_solutions["keys"]
    solutions = steiner_solutions["solutions"]
    num2type = steiner_solutions["num2type"]
    num2slot = steiner_solutions["num2slot"]
    key_map = {v: idx for idx, v in enumerate(steiner_solutions["keys"])}
    slot2num = {v: k for k, v in enumerate(steiner_solutions["num2slot"])}
    solutions = [s for s in steiner_solutions["solutions"] if s[key_map["effect"]] / s[key_map["cost"]] >= 2.5]


with open("data/jewel_slots.json", "r") as file:
    jewel_slots = json.loads(file.read())


image_map = ["static/Brutal_Restraint_inventory_icon.png","static/Glorious_Vanity_inventory_icon.png","static/Elegant_Hubris_inventory_icon.png"]


slot2hash = {}
for k, v in jewel_slots.items():
    for kk, vv in v.items():
        slot2hash[slot2num[kk]] = vv["jewel_hash"]


class Jewel:
    def __init__(self, id, values, price, last_seen):
        self.id = id
        self.seed = values[key_map["seed"]]
        self.type = values[key_map["type"]]
        self.position = values[key_map["slot"]]
        self.price = price
        self.last_seen = last_seen
        self.effect = values[key_map["effect"]]
        self.ie = values[key_map["ie"]]
        self.anoint = 1 if values[key_map["anoint"]]>0 else 0
        self.point_cost = values[key_map["cost"]]



def get_all_jewels():
    jewel_prices, ie_prices = get_prices()
    jewels = []
    for id, s in enumerate(solutions):
        p = jewel_prices[(num2type[s[key_map["type"]]], s[key_map["seed"]])]
        price = p["price"] if p["price"] else ""
        last_seen = p["last_seen"]
        if s[key_map["ie"]] and price and ie_prices[s[key_map["ie"]]]["price"]:
            price = price + ie_prices[s[key_map["ie"]]]["price"]
        jewels.append(Jewel(id=id, price=price, last_seen=last_seen, values=s))
    return jewels


@app.route('/',methods = ['GET'])
def endpoint():
    return render_template("basic_table.html")

 
@app.route('/',methods = ['POST'])
def post():
    solution = solutions[int(request.json["id"])]
    return jsonify({
        "jewel_id": slot2hash[solution[key_map["slot"]]],
        "keystone_id": solution[key_map["ie"]] if solution[key_map["ie"]] else None,
        "active_nodes": solution[key_map["active_nodes"]],
        "important_nodes": solution[key_map["aura_nodes"]]
    })

@app.route('/tree.json')
def get_json():
    with open("static/tree.json", "r") as file:
        return file.read()

@app.route('/solutions.json')
def get_solutions():
    return solutions

@app.route('/prices.json')
def get_price():
    return get_prices()


@app.route('/dump')
def dump_db():
    return send_file('trade.db', as_attachment=True)


with app.app_context():
    initialize_scheduler()

if __name__ == '__main__':
    app.run()
