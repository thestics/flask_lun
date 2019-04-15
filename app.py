from flask import Flask, render_template, request
import art_parser
from threading import Thread
from sqlite3 import OperationalError
from form import SearchForm
import os


app = Flask(__name__)

priceMax = 10_000_000_000
app.config['SECRET_KEY'] = 'abc'
form_vals = {'reg': '','pMin': 0, 'pMax':priceMax ,'rooms': '','desc': '', 'pgAmt': ''}


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
            pMax = priceMax
        pgAmt = db.get_amount_of_pages(reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)
        new_args = {'reg': reg,'pMin': pMin, 'pMax': pMax, 'rooms': rooms,'desc': desc, 'pgAmt': str(pgAmt)}
        form_vals = new_args
        pg = '1'
    reg, pMin, pMax, rooms, desc, pgAmt = form_vals.values()
    if int(pg) < 1:
        pg = '1'
    elif int(pg) > int(pgAmt):
        pg = pgAmt
    data = db.get_data_by(int(pg) - 1, reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)     # y i know about python container unpacking
    return render_template('index.html', pgAmt=pgAmt, form_vals=form_vals, page=int(pg), data=data, form=form)


def _init_page_amt():
    global form_vals
    db = art_parser.DBManager('art_parser/articles.db')
    amt = db.get_amount_of_pages(price_min=0, price_max=priceMax)
    form_vals['pgAmt'] = str(amt)


def _ensure_table_existence():
    db = art_parser.DBManager('art_parser/articles.db')
    try:
        db.get_last_ref()
    except OperationalError:
        db.conn.execute(
            "CREATE TABLE articles (id integer primary key, title text, ref text, descr text, rooms text, price text)")

# TODO: fix pagination

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    _ensure_table_existence()
    _init_page_amt()
    t2 = Thread(target=art_parser.poll_update, args=('art_parser/articles.db', 300))
    t2.start()
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)  # idk but not defined use_reloader causes sub-thread to run twice


