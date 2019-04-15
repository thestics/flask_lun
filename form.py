from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField


class SearchForm(FlaskForm):
    region = StringField('Регион', validators=[])
    rooms = StringField('Количество комнат', validators=[])
    price = StringField('Цена', validators=[])
    descr = StringField('Описание', validators=[])
    submit = SubmitField('Поиск', validators=[])


if __name__ == '__main__':
    f = SearchForm()
    f.hidden_tag()