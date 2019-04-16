from flask import Flask, render_template, request
import art_parser
from threading import Thread
from sqlite3 import OperationalError
from form import SearchForm
from secrets import token_bytes
from base64 import b64encode
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc'
priceMax = 10_000_000_000
form_vals = {'reg': '', 'price':0, 'pMin': 0, 'pMax':priceMax ,'rooms': '','desc': '', 'pgAmt': '50'}


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
        if rooms is None:
            rooms = ''
        else:
            rooms = str(rooms)
        if not price is None:
            pMin = int(price) - 1000
            pMax = int(price) + 1000
        else:
            pMin = 0
            pMax = priceMax
            price = 0
        pgAmt = db.get_amount_of_pages(reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)
        new_args = {'reg': reg, 'price': price,'pMin': pMin, 'pMax': pMax, 'rooms': rooms,'desc': desc, 'pgAmt': str(pgAmt)}
        form_vals = new_args
        pg = '1'
    reg, price, pMin, pMax, rooms, desc, pgAmt = form_vals.values()
    if int(pg) < 1:
        pg = '1'
    elif int(pg) > int(pgAmt):
        pg = pgAmt
    data = db.get_data_by(int(pg) - 1, reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)     # y i know about python container unpacking
    return render_template('index.html', price=price, pgAmt=pgAmt, form_vals=form_vals, page=int(pg), data=data, form=form)


def init_page_amt():
    global form_vals
    db = art_parser.DBManager('art_parser/articles.db')
    amt = db.get_amount_of_pages(price_min=0, price_max=priceMax)
    form_vals['pgAmt'] = str(amt)


def ensure_table_existence():
    db = art_parser.DBManager('art_parser/articles.db')
    try:
        db.get_last_ref()
    except OperationalError:
        db.conn.execute(
            "CREATE TABLE articles (id integer primary key, title text, ref text, descr text, rooms text, price text)")

def ensure_post_secret_key():
    global app
    rand_bytes = token_bytes()
    rand_token = b64encode(rand_bytes).decode()
    app.config['SECRET_KEY'] = rand_token



if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    ensure_post_secret_key()
    ensure_table_existence()
    init_page_amt()
    t2 = Thread(target=art_parser.poll_update, args=('art_parser/articles.db', 900))
    t2.start()
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
else:
    ensure_post_secret_key()
    ensure_table_existence()
    init_page_amt()
    t2 = Thread(target=art_parser.poll_update, args=('art_parser/articles.db', 900))
    t2.start()


