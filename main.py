from datetime import datetime
import sqlite3 as sl

import atexit
from flask import Flask, render_template, send_file
from apscheduler.schedulers.background import BackgroundScheduler

from trade_crawler import update_all_jewels, Jewel

app = Flask(__name__)


class JewelOut:
    def __init__(self, type, position, seed, effect, url_hash, last_queried, price, points_to_jewel, additional_points, ie, anoint):
        self.type = type
        self.position = position
        self.seed = seed
        self.url = f"https://www.pathofexile.com/trade/search/Crucible/{url_hash}"
        if last_queried:
            diff = (datetime.utcnow() - datetime.strptime(last_queried, '%Y-%m-%d %H:%M:%S.%f')).seconds
            if diff < 60:
                self.last_queried = "<1 min ago"
            elif diff < 60 * 60:
                self.last_queried = f"{round(diff / 60)} min ago"
            elif diff < 60 * 60 * 24:
                self.last_queried = f"{round(diff / 60 / 60)} h ago"
            else:
                self.last_queried = f"{round(diff / 60 / 60 / 24)} d ago"

        else:
            self.last_queried = "Never"

        self.total_points = points_to_jewel + additional_points
        # if ie:
        #     self.total_points += 3
        self.effect = effect
        self.effect_pp = round(self.effect / self.total_points, 2)
        self.ie = ie
        self.anoint = anoint
        self.price = price if price != "None" else ""


def get_all_jewels():
    jewels = []
    con = sl.connect('jewels.db')
    with con:
        for jewel_data in con.execute("SELECT * FROM JEWEL"):
            jewel = Jewel(*jewel_data)
            base = [jewel.type, jewel.position, jewel.seed, jewel.effect, jewel.url_hash,
                    jewel.last_queried, jewel.price, jewel.points_to_jewel]
            if jewel.points_base:
                jewels.append(JewelOut(*base, jewel.points_base, False, False))
            if jewel.points_w_ie:
                jewels.append(JewelOut(*base, jewel.points_w_ie, True, False))
            if jewel.points_w_anoint:
                jewels.append(JewelOut(*base, jewel.points_w_anoint, False, True))
    return jewels


@app.route('/')
def endpoint():
    return render_template("basic_table.html", table=get_all_jewels())

@app.route('/dump')
def dump_db():
    return send_file('jewels.db', as_attachment=True)


def initialize_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_all_jewels, trigger="interval", minutes=10)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    initialize_scheduler()
    app.run()
