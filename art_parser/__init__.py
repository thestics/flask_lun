from .dbmngr import DBManager
from .parse import DRIAParser
from .back import poll_update
import time


__all__ = ['DBManager', 'DRIAParser', 'poll_update']


# def poll_update(delay=3600):
#     db = dbmngr.DBManager()
#     last_ref = db.get_last_ref()
#     db.conn_close()
#     parser = parse.DRIAParser(last_art_ref=last_ref, amt=100)
#     while True:
#         print("parser awake...")
#         db.conn_open()
#         ref = db.get_last_ref()
#         parser.set_last_ref(ref)
#         to_add = parser.parse()
#         db.insert_data(to_add)
#         db.conn_close()
#         print(f"parser asleep for {delay/60} min...")
#         time.sleep(delay)


# if __name__ == '__main__':
#     poll_update()
