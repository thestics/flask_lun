from math import ceil
from time import sleep
from . import parse
from . import dbmngr


def poll_update(path, delay=3600):
    print("polling started")
    db = dbmngr.DBManager(path)
    last_ref = db.get_last_ref()
    db.conn_close()
    parser = parse.DRIAParser(last_art_ref=last_ref, amt=100)
    while True:
        print("parser awake...")
        db.conn_open(path)
        ref = db.get_last_ref()
        parser.set_last_ref(ref)
        to_add = parser.parse()
        db.insert_data(to_add)
        db.conn_close()
        print(f"parser asleep for {delay/60} min...")
        sleep(delay)


class ExtendedParser(parse.DRIAParser):

    def __init__(self, path, last_art_ref="", amt=100):
        super().__init__(last_art_ref, amt)
        self.db = dbmngr.DBManager(path)

    def check_updated_articles(self, offset: int, n: int):
        """
        Checks if any of parsed articles was updated on original website,
        if so - collects updated articles

        :param offset:
        :param n:
        :return:
        """
        pass

    def _remove_head(self, parsed_data: list, last_ref: str) -> list:
        for i, record in enumerate(parsed_data):
            if record[2] == last_ref:   # record[2] - link
                return parsed_data[i:]
        return []

    def check_deleted_articles(self, offset: int, n: int):
        """
        Checks if any of parsed articles was deleted on original website,
        if so - collects them and retrieves

        :param n: amount of last articles to be checked
        :param offset: offset from start (from latest parsed article)
        :return: list - deleted articles
        """
        parsed_data = self.db.get_data_by(offset, amount=n)
        ...


if __name__ == '__main__':
    p = ExtendedParser('art_parser/articles.db')
    p.check_deleted_articles(0, 10)
