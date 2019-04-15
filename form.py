from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField


class SearchForm(FlaskForm):
    region = StringField('Регион', validators=[])
    rooms = IntegerField('Количество комнат', validators=[])
    price = IntegerField('Цена', validators=[])
    descr = StringField('Описание', validators=[])
    submit = SubmitField('Поиск', validators=[])


if __name__ == '__main__':
    f = SearchForm()
    f.hidden_tag()