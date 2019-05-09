
TAIL_TEMPLATE = "&reg={}&price_min={}&price_max={}&rooms={}&desc={}"
PATH_TO_DB = 'art_parser/articles.db'
POLLING_DELAY = 900
aliases = ['region', 'rooms', 'price_min', 'price_max', 'description']
form_default_values = {'description': '', 'rooms': 0, 'price_min': 0,
                       'price_max': 10_000_000}
