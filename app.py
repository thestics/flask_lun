from flask import Flask, render_template, request
import art_parser
from threading import Thread
from sqlite3 import OperationalError
from form import SearchForm
import os


app = Flask(__name__)


app.config['SECRET_KEY'] = 'abc'
form_vals = {'reg': '','pMin': 0, 'pMax':10_000_000_000 ,'rooms': '','desc': ''}


@app.route('/', methods=['GET', 'POST'])
def home_route():
    global form_vals
    db = art_parser.DBManager('art_parser/articles.db')
    form = SearchForm()
    pg = request.args.get('page', default='1')
    if form.is_submitted():
        reg = form.region.data
        price = form.price.data
        rooms = form.rooms.data
        desc = form.descr.data
        if price:
            pMin = int(price) - 1000
            pMax = int(price) + 1000
        else:
            pMin = 0
            pMax = 10_000_000_000
        pg = 1
        new_args = {'reg': reg,'pMin': pMin, 'pMax': pMax, 'rooms': rooms,'desc': desc}
        form_vals = new_args
    reg, pMin, pMax, rooms, desc = form_vals.values()
    data = db.get_data_by(int(pg) - 1, reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)
    return render_template('index.html', form_vals=form_vals, page=int(pg), data=data, form=form)


def _ensure_table_existence():
    db = art_parser.DBManager('art_parser/articles.db')
    try:
        db.get_last_ref()
    except OperationalError:
        db.conn.execute(
            "CREATE TABLE articles (id integer primary key, title text, ref text, descr text, rooms text, price text)")

def __dummy(*args, **kwargs):
    import time
    while True:
        print('dummy awake')
        time.sleep(10)


if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    _ensure_table_existence()
    t2 = Thread(target=art_parser.poll_update, args=('art_parser/articles.db', 300))
    t2.start()
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)


