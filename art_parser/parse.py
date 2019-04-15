import requests
from bs4 import BeautifulSoup as BS


class DRIAParser:
    cardViewBaseUrl = "https://dom.ria.com"

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

    def _get_title(self, tag):  # region is defined in card title isn't it redundant to search for region separately?
        """Extract title (link, text) from card"""
        aTag = tag.find('div', class_='mb-10').a
        if aTag:
            link = aTag['href']
            data = aTag.text.strip()
            metroTag = tag.find('span', class_="i-block")
            if metroTag:
                data += f" {metroTag.text} "
            return link, data

    def _get_description(self, tag):
        """Extract description from card"""
        pTag = tag.find('p', class_='descriptions-ticket')
        if pTag:
            descr = pTag.span.text.strip()
            return descr

    def _get_rooms(self, tag):
        """Extract amount of rooms from cards"""
        listTag = tag.find('ul')
        if listTag:
            rooms = listTag.li.text.strip()
            return rooms

    def _get_price(self, tag):
        """Extract price from tag"""
        moneyTag = tag.find('div', class_="mb-5 mt-10 pr")
        if moneyTag:
            usdVal, uahVal = moneyTag.span.text.strip().split(' / ')
            usdVal = ''.join(usdVal.split())    # 9 000 -> 9000 to be able to cast it to integer safely in sql query
            uahVal = ''.join(uahVal.split())
            return usdVal, uahVal

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
        resp = requests.get(self.cardViewBaseUrl + rel_url)
        if resp.status_code == 200:
            soup = BS(resp.text, 'html.parser')
            divTag = soup.find("div", id="catalogResults")
            sections = divTag.find_all("section")
            pagination = soup.find('div', id='pagination')
            nextUrl = pagination.find('span', class_='page-item next text-r').a['href'].strip()

            for s in sections:
                cardLink, cardTitle = self._get_title(s)
                if self.cardViewBaseUrl + cardLink == self.last_art:           # last parsed article check
                    return ""
                desc = self._get_description(s)
                rooms = self._get_rooms(s)
                price = self._get_price(s)
                self.cards.append(
                    (cardTitle, self.cardViewBaseUrl + cardLink, desc, rooms, price)
                )
            return nextUrl
        else:
            raise Exception # TODO: refactor for project-specific exceptions


# if __name__ == '__main__':
#     from pprint import pprint
#     p = DRIAParser(amt=100)
#     pprint(p.parse())
