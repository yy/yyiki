from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    query = StringField("query", validators=[DataRequired()])


class EditForm(FlaskForm):
    path = HiddenField("path", validators=[DataRequired()])
    content = TextAreaField("content", validators=[DataRequired()])
    pagemeta = TextAreaField("pagemeta", validators=[DataRequired()])
