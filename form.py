from html import escape

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField


class SearchForm(FlaskForm):

    region = StringField('Регион', validators=[])
    rooms = IntegerField('Количество комнат', validators=[])
    price_min = IntegerField('Цена от, грн.', validators=[])
    price_max = IntegerField('Цена до, грн.', validators=[])
    description = StringField('Описание', validators=[])
    submit = SubmitField('Поиск', validators=[])

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def extract_params(self):
        """Sanitizes provided params and retrieves them

        :return: tuple
        """
        region = escape(self.region.data)
        rooms = 0
        price_min = 0
        price_max = 10_000_000
        description = escape(self.description.data)

        self.region.data = region
        self.description.data = description
        if self.rooms.data is not None:
            if int(self.rooms.data) == rooms: # default value
                rooms = 0
            rooms = self.rooms.data


        if self.price_min.data is not None:
            price_min = self.price_min.data

        if self.price_max.data is not None:
            price_max = self.price_max.data

        return region, rooms, price_min, price_max, description
