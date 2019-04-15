from . import parse
from . import dbmngr
import time


def poll_update(path, delay=3600):
    print("polling started")
    db = dbmngr.DBManager(path)
    last_ref = db.get_last_ref()
    db.conn_close()
    parser = parse.DRIAParser(last_art_ref=last_ref, amt=1000)
    while True:
        print("parser awake...")
        db.conn_open(path)
        ref = db.get_last_ref()
        parser.set_last_ref(ref)
        to_add = parser.parse()
        db.insert_data(to_add)
        db.conn_close()
        print(f"parser asleep for {delay/60} min...")
        time.sleep(delay)


# if __name__ == '__main__':
    # poll_update("articles.db")
