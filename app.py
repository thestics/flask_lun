from sqlite3 import OperationalError
from threading import Thread
from secrets import token_bytes
from base64 import b64encode
from os import environ

from flask import Flask, render_template, request, url_for

from art_parser import DBManager, poll_update
from form import SearchForm
from constants import TAIL_TEMPLATE, PATH_TO_DB, POLLING_DELAY, aliases, \
                      form_default_values


app = Flask(__name__)


def _handle_pg(pg: str, pg_amt):
    if int(pg) < 1:
        res = '1'
    elif int(pg) > int(pg_amt):
        res = pg_amt
    else:
        res = pg
    return res


@app.route('/', methods=['GET', 'POST'])
def home_route():
    db = DBManager(PATH_TO_DB)     # connect db
    form = SearchForm(request.args)

    # extract form params
    form_data = form.extract_params()
    region, rooms, price_min, price_max, description = form_data
    # format url tail
    tail = TAIL_TEMPLATE.format(region, price_min, price_max, rooms,
                                description)
    # form entered values
    form_values = {
        alias: value for alias, value in zip(aliases, form_data)
    }
    # total amount of pages
    pg_amt = db.get_amount_of_pages(**form_values)

    if form.is_submitted():
        pg = '1'
    else:
        pg = request.args.get('page', '1')
        pg = _handle_pg(pg, pg_amt)
    # ensure 0 < page number < pgAmt + 1
    articles_data = db.get_data_by(int(pg) - 1, **form_values)
    return render_template('index.html', tail=tail, pg_amt=pg_amt,
                           page=int(pg), data=articles_data, form=form,
                           default=form_default_values)


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
