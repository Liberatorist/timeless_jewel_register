from datetime import datetime
import sqlite3 as sl
from flask import Flask, render_template, send_file

from trade_crawler import Jewel, initialize_scheduler

app = Flask(__name__)


class JewelOut:
    def __init__(self, type, position, seed, effect, url_hash, last_queried, price, points_to_jewel, additional_points, ie, anoint):
        self.type = type
        self.position = position
        self.seed = seed
        self.url = f"https://www.pathofexile.com/trade/search/Crucible/{url_hash}"
        if last_queried:
            self.last_queried = get_human_readable_time_diff(last_queried)

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
    con = sl.connect('jewels.db')
    with con:
        for update in con.execute("SELECT time FROM LAST_UPDATE"):
            return get_human_readable_time_diff(update[0])


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
    return render_template("basic_table.html", table=get_all_jewels(), last_update=get_last_update())


@app.route('/dump')
def dump_db():
    return send_file('jewels.db', as_attachment=True)


with app.app_context():
    initialize_scheduler()

if __name__ == '__main__':
    app.run()
