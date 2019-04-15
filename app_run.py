from app import app, init_page_amt, ensure_post_secret_key, ensure_table_existence
import os
import art_parser
from threading import Thread


if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    ensure_post_secret_key()
    ensure_table_existence()
    init_page_amt()
    t2 = Thread(target=art_parser.poll_update, args=('art_parser/articles.db', 900))
    t2.start()
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
