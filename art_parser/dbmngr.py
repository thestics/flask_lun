import sqlite3
from math import ceil


class DBManager:
    recordsPerPage = 20

    def __init__(self, path):
        self.conn = None
        self.curs = None
        self.conn_open(path)

    def _get_last_id(self):
        q = """SELECT id FROM articles ORDER BY id DESC LIMIT 1"""
        self.curs.execute(q)
        num = self.curs.fetchone()
        if not num:
            return -1
        return num[0]

    def get_last_ref(self):
        q = """SELECT ref FROM articles ORDER BY id DESC LIMIT 1"""
        self.curs.execute(q)
        res = self.curs.fetchone()
        if not res:
            return ""
        return res[0]

    def get_last_arts(self, n: int):
        q = """SELECT * FROM articles ORDER BY id DESC LIMIT ?"""
        self.curs.execute(q, (n,))
        res = self.curs.fetchall()
        return res

    def get_amount_of_pages(self, reg='', rooms='', price_min=None, price_max=None, desc=''):
        # probably would be better to somehow combine these two heavy queries in one
        q = """SELECT COUNT(*) FROM articles where 
            title like '%' || ? || '%' AND (price_uah BETWEEN ? AND ?) AND (rooms=?) AND
            descr like '%' || ? || '%' ORDER BY id DESC LIMIT ? OFFSET ?"""
        self.curs.execute(q,
                          (reg, price_min, price_max, rooms, desc))
        return ceil(self.curs.fetchone()[0] / self.recordsPerPage)

    def get_data_by(self, offset, reg='', rooms='', price_min=None, price_max=None, desc=''):
        """
        Pagination-oriented method for querying data for a current page
        Designed to retrieve all records in database by-default (with no arguments provided).

        :param offset:if we need data for n-th page, (n-1) is to be provided
        :param reg:     string from "region" field in form
        :param rooms:   string from "rooms" field in form
        :param price_min: A little deviation is to be added to price string from field in form (+- 1-2k for instance).
                        Though in task description only one field for price was defined, imo it will be much more
                        convenient for user to get records not only with strict match on string provided by form and
                        string stored in 'price' column in database
        :param desc:    string from 'description' column in form
        :return:    list of tuples - matched records from database
        """
        if price_min is None:   # price_min price_max None or not None simultaneously, one is enough
            price_min = 0
            price_max = 10_000_000_000  # hardcoded value, hope sudden inflation won't break it all :)

        q = """SELECT * FROM articles where 
            title like '%' || ? || '%' AND (price_uah BETWEEN ? AND ?) AND (rooms=?) AND
            descr like '%' || ? || '%' ORDER BY id DESC LIMIT ? OFFSET ?"""

        self.curs.execute(q, (reg, price_min, price_max, rooms, desc, self.recordsPerPage, offset*self.recordsPerPage))
        return self.curs.fetchall()

    def insert_data(self, data: list):
        """
        Adds records from data list into database. Required format:
            [
                (title1, url1, description1, rooms1, price1_usd, price1_uah), ...
            ]
        Adds additional parameter date_added before inserting into database, to be able to sort by latest parsed
        data
        :return:
        """
        last_id = self._get_last_id()
        q = """INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?)"""
        # newest was on top, we want them to be on the bottom of database, to be able to add new records freely and to
        # preserve order
        for art in data[::-1]:
            last_id += 1
            title, url, desc, rooms, price_usd, price_uah = art
            # price = '/'.join(price)
            self.curs.execute(q, (last_id, title, url, desc, rooms, price_uah, price_usd))
        self.conn.commit()

    def conn_close(self):
        self.conn.close()

    def conn_open(self, path):
        self.conn = sqlite3.connect(path)
        self.curs = self.conn.cursor()


# if __name__ == '__main__':
    # p = parse.DRIAParser(amt=100)
    # from pprint import pprint
    # db = DBManager("articles.db")
    # print(db.get_amount_of_pages())
    # pprint(db.get_data_by(60, price_min=10_000, price_max=20_000))
    # parsed_list = p.parse()
    # print(db._get_last_ref())
