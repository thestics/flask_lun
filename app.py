from flask import Flask, render_template, request, url_for
import art_parser
from threading import Thread
from sqlite3 import OperationalError
from form import SearchForm
from secrets import token_bytes
from base64 import b64encode
from html import escape
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc'
priceMax = 10_000_000_000


def _handle_form_args(reg, price, rooms, desc):
    new_price = price
    if rooms is None:
        new_rooms = ''
    else:
        new_rooms = str(rooms)
    if not price is None and price:
        pMin = int(price) - 1500
        pMax = int(price) + 1500
    else:
        pMin = 0
        pMax = priceMax
        new_price = ''
    return reg, new_price, pMin, pMax, new_rooms, desc


def _handle_pg(pg: str, pgAmt):
    if int(pg) < 1:
        res = '1'
    elif int(pg) > pgAmt:
        res = pgAmt
    else:
        res = pg
    return res


tail_template = "&reg={}&price={}&rooms={}&desc={}"


@app.route('/', methods=['GET', 'POST'])
def home_route():
    db = art_parser.DBManager('art_parser/articles.db')     # connect db
    form = SearchForm()
    if form.is_submitted():
        form_params = (form.region.data, form.price.data,   # extract form params
                        form.rooms.data, form.descr.data)
        reg, price, pMin, pMax, rooms, desc = _handle_form_args(*form_params)
        reg, price, desc = map(escape, (reg, str(price),desc))         # sanitize string params
        tail = tail_template.format(reg, price, rooms, desc)                    # format url tail
        pgAmt = db.get_amount_of_pages(reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc) # total amount of pages
        form_vals = {'reg': reg, 'price': price, 'rooms': rooms, 'desc': desc}                      # form entered vals
        pg = '1'
        data = db.get_data_by(0, reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)   # db request for data
        return render_template('index.html', price=price, tail=tail, pgAmt=pgAmt, form_vals=form_vals,
                               page=int(pg), data=data, form=form)
    url_params = (request.args.get('reg', ''), request.args.get('price', ''),           # extract params from url
                  request.args.get('rooms', ''), request.args.get('desc', ''))
    reg, price, pMin, pMax, rooms, desc = _handle_form_args(*url_params)
    # two more params to sanitize (field format differs, so in form no text would get through,
    # whereas here we got this params from GET request as an str, sanitization needed)
    reg, price, rooms, desc = map(escape, (reg, str(price), str(rooms), desc))
    tail = tail_template.format(reg, price, rooms, desc)                                        # format url tail
    pgAmt = db.get_amount_of_pages(reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)
    pg = request.args.get('page', '1')
    pg = _handle_pg(pg, pgAmt)                                                      # ensure 0 < page number < pgAmt + 1
    form_vals = {'reg': reg, 'price': price, 'rooms': rooms, 'desc': desc}
    data = db.get_data_by(int(pg) - 1, reg=reg, price_min=pMin, price_max=pMax, rooms=rooms, desc=desc)     # y i know about python container unpacking
    return render_template('index.html', price=price, tail=tail, pgAmt=pgAmt, form_vals=form_vals,
                           page=int(pg), data=data, form=form)


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
    t2 = Thread(target=art_parser.poll_update, args=('art_parser/articles.db', 900))
    t2.start()
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
else:
    ensure_post_secret_key()
    ensure_table_existence()
    t2 = Thread(target=art_parser.poll_update, args=('art_parser/articles.db', 900))
    t2.start()


