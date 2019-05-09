import sqlite3
from math import ceil


class DBManager:
    records_per_page = 20

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

    def get_amount_of_pages(self, reg='', rooms='', price_min=None,
                            price_max=None, desc='') -> int:
        q = """SELECT COUNT(*) FROM articles where 
                title like '%' || ? || '%' AND (price_uah BETWEEN ? AND ?) 
                AND (rooms=?) AND descr like '%' || ? || '%' 
                ORDER BY id DESC LIMIT ? OFFSET ?"""
        self.curs.execute(q,
                          (reg, price_min, price_max, rooms, desc))
        return ceil(self.curs.fetchone()[0] / self.records_per_page)

    def get_data_by(self, offset, reg='', rooms=0, price_min=None,
                    price_max=None, desc='', amount=None) -> list:
        """
        Pagination-oriented method for querying data for a current page.
        Designed to retrieve all records in database by-default
        (with no arguments provided).

        :param offset:      if we need data for n-th page,
                            (n-1) is to be provided
        :param reg:         string from "region" field in form
        :param rooms:       string from "rooms" field in form
        :param price_min:   minimum price
        :param price_max:   maximum price
        :param desc:        string from 'description' column in form
        :return:    list of tuples - matched records from database
        """

        # price_min price_max None or not None simultaneously, one is enough
        if price_min is None:
            price_min = 0
            price_max = 10_000_000_000  # hardcoded value
        records_amount = amount if amount else self.records_per_page

        if rooms:
            q = """SELECT * FROM articles where 
                    title like '%' || ? || '%' AND (price_uah BETWEEN ? AND ?) 
                    AND (rooms=?) AND descr like '%' || ? || '%' ORDER BY id 
                    DESC LIMIT ? OFFSET ?"""
            self.curs.execute(q, (reg, price_min, price_max, rooms, desc,
                                  records_amount, offset*self.records_per_page))
        else:
            q = """SELECT * FROM articles where 
                    title like '%' || ? || '%' AND (price_uah BETWEEN ? AND ?) 
                    AND descr like '%' || ? || '%' ORDER BY id 
                    DESC LIMIT ? OFFSET ?"""
            self.curs.execute(q, (reg, price_min, price_max, desc,
                                  records_amount, offset*self.records_per_page))
        return self.curs.fetchall()

    def insert_data(self, data: list):
        """
        Adds records from data list into database. Required format:
            [
                (title1, url1, description1, rooms1, price1_usd, price1_uah),...
            ]
        data

        :return: None
        """
        last_id = self._get_last_id()
        q = """INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?)"""

        # newest was on top, we want them to be on the bottom of database
        # to be able to add new records freely and to preserve order
        for art in data[::-1]:
            last_id += 1
            title, url, desc, rooms, price_usd, price_uah = art
            self.curs.execute(q, (last_id, title, url, desc, rooms,
                                  price_uah, price_usd))
        self.conn.commit()

    def conn_close(self):
        self.conn.close()

    def conn_open(self, path):
        self.conn = sqlite3.connect(path)
        self.curs = self.conn.cursor()
        