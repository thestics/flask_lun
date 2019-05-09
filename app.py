from sqlite3 import OperationalError
from threading import Thread
from secrets import token_bytes
from base64 import b64encode
from os import environ
from html import escape
from flask import Flask, render_template, request, url_for
from art_parser import DBManager, poll_update
from form import SearchForm
from constants import TAIL_TEMPLATE, PATH_TO_DB, POLLING_DELAY


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'abc'
priceMax = 10_000_000_000


def _handle_form_args(reg, price, rooms, desc):
    new_price = price
    if rooms is None:
        new_rooms = ''
    else:
        new_rooms = str(rooms)
    if price is not None and price:
        p_min = int(price) - 1500
        p_max = int(price) + 1500
    else:
        p_min = 0
        p_max = priceMax
        new_price = ''
    return reg, new_price, p_min, p_max, new_rooms, desc


def _handle_pg(pg: str, pg_amt):
    if int(pg) < 1:
        res = '1'
    elif int(pg) > pg_amt:
        res = pg_amt
    else:
        res = pg
    return res


@app.route('/', methods=['GET', 'POST'])
def home_route():
    db = DBManager(PATH_TO_DB)     # connect db
    form = SearchForm()
    if form.is_submitted():
        # extract form params
        form_params = (form.region.data, form.price.data,
                       form.rooms.data, form.descr.data)
        reg, price, p_min, p_max, rooms, desc = _handle_form_args(*form_params)
        # sanitize string params
        reg, price, desc = map(escape, (reg, str(price), desc))
        # format url tail
        tail = TAIL_TEMPLATE.format(reg, price, rooms, desc)
        # total amount of pages
        pg_amt = db.get_amount_of_pages(reg=reg, price_min=p_min,
                                        price_max=p_max, rooms=rooms, desc=desc)
        # form entered values
        form_values = {'reg': reg, 'price': price, 'rooms': rooms, 'desc': desc}
        pg = '1'
        # db request for data
        data = db.get_data_by(0, reg=reg, price_min=p_min, price_max=p_max,
                              rooms=rooms, desc=desc)
        return render_template('index.html', price=price, tail=tail,
                               pgAmt=pg_amt, form_vals=form_values,
                               page=int(pg), data=data, form=form)
    # extract params from url
    url_params = (request.args.get('reg', ''), request.args.get('price', ''),
                  request.args.get('rooms', ''), request.args.get('desc', ''))
    reg, price, p_min, p_max, rooms, desc = _handle_form_args(*url_params)
    # Two more params to sanitize (field format differs, so in form
    # no text would get through, whereas here we got this params from
    # GET request as an str, sanitization needed)
    reg, price, rooms, desc = map(escape, (reg, str(price), str(rooms), desc))
    # format url tail
    tail = TAIL_TEMPLATE.format(reg, price, rooms, desc)
    pg_amt = db.get_amount_of_pages(reg=reg, price_min=p_min, price_max=p_max,
                                    rooms=rooms, desc=desc)
    pg = request.args.get('page', '1')
    # ensure 0 < page number < pgAmt + 1
    pg = _handle_pg(pg, pg_amt)
    form_values = {'reg': reg, 'price': price, 'rooms': rooms, 'desc': desc}
    data = db.get_data_by(int(pg) - 1, reg=reg, price_min=p_min,
                          price_max=p_max, rooms=rooms, desc=desc)
    return render_template('index.html', price=price, tail=tail, pgAmt=pg_amt,
                           form_vals=form_values,
                           page=int(pg), data=data, form=form)


def ensure_table_existence():
    db = DBManager(PATH_TO_DB)
    try:
        db.get_last_ref()
    except OperationalError:
        db.conn.execute(
            """CREATE TABLE articles (id integer primary key, title text, 
               ref text, descr text, rooms text, price text)"""
        )


def ensure_post_secret_key():
    global app
    rand_bytes = token_bytes()
    rand_token = b64encode(rand_bytes).decode()
    app.config['SECRET_KEY'] = rand_token


if __name__ == '__main__':
    port = environ.get("PORT", 5000)
    ensure_post_secret_key()
    ensure_table_existence()
    t2 = Thread(target=poll_update, args=(PATH_TO_DB, POLLING_DELAY))
    t2.start()
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
else:
    ensure_post_secret_key()
    ensure_table_existence()
    t2 = Thread(target=poll_update, args=(PATH_TO_DB, POLLING_DELAY))
    t2.start()
