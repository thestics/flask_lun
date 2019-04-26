import requests
from bs4 import BeautifulSoup as BS
import re


class DRIAParser:
    card_view_base_url = "https://dom.ria.com"

    def __init__(self, last_art_ref="", amt=100):
        """

        :param last_art_ref: the newest parsed article. No parsing will be made after this one occurred while
                      crawling
        :param amt: amount of articles to be parsed
        If both parameters provided (something) is chosen
        """
        self.amt = amt
        self.last_art = last_art_ref
        self.cards = []

    def set_last_ref(self, ref):
        self.last_art = ref

    def _get_title(self, tag):
        """Extract title (link, text) from card"""
        a_tag = tag.find('div', class_='mb-10').a
        if a_tag:
            link = a_tag['href']
            data = a_tag.text.strip()
            metro_tag = tag.find('span', class_="i-block")
            if metro_tag:
                data += f" м. {metro_tag.text} "
            return link, data

    def _get_description(self, tag):
        """Extract description from card"""
        p_tag = tag.find('p', class_='descriptions-ticket')
        if p_tag:
            description = p_tag.span.text.strip()
            return description

    def _get_rooms(self, tag):
        """Extract amount of rooms from cards"""
        list_tag = tag.find('ul')
        if list_tag:
            rooms_string = list_tag.li.text.strip()
            patt = r'(\d+)'
            rooms_amt = re.search(patt, rooms_string).group(0)
            return int(rooms_amt)

    def _get_price(self, tag):
        """Extract price from tag"""
        money_tag = tag.find('div', class_="mb-5 mt-10 pr")
        if money_tag:
            data = money_tag.text.replace(' ', '').replace('грн', '').replace('$', '')
            patt = r'(\d+)/(\d+)'
            match_res = re.search(patt, data)
            uah_val, usd_val = match_res.group(1), match_res.group(2)
            return int(usd_val), int(uah_val)

    def parse(self):
        next = "/arenda-kvartir/kiev/?page=1"
        self.cards.clear()
        while len(self.cards) < self.amt:   # not more then specified in init
            next = self._parse(next)
            if not next:                # last article reference encountered
                return self.cards
        return self.cards

    def _parse(self, rel_url):
        """

        :param rel_url: relative to base url
        """
        resp = requests.get(self.card_view_base_url + rel_url)
        if resp.status_code == 200:
            soup = BS(resp.text, 'html.parser')
            div_tag = soup.find("div", id="catalogResults")
            sections = div_tag.find_all("section")
            pagination = soup.find('div', id='pagination')
            next_url = pagination.find('span', class_='page-item next text-r').a['href'].strip()

            for s in sections:
                card_link, card_title = self._get_title(s)
                if self.card_view_base_url + card_link == self.last_art:           # last parsed article check
                    return ""
                desc = self._get_description(s)
                rooms = self._get_rooms(s)
                price_usd, price_uah = self._get_price(s)
                self.cards.append(
                    (card_title, self.card_view_base_url + card_link, desc, rooms, price_usd, price_uah)
                )
            return next_url
        else:
            raise Exception # TODO: refactor for project-specific exceptions


if __name__ == '__main__':
    from pprint import pprint
    p = DRIAParser(amt=10)
    print(p.parse())
