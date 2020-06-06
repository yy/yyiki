from flask_wtf import FlaskForm
from wtforms import (BooleanField, HiddenField, PasswordField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Email


class SearchForm(FlaskForm):
    query = StringField("query", validators=[DataRequired()])


class EditForm(FlaskForm):
    path = HiddenField("path", validators=[DataRequired()])
    content = TextAreaField("content", validators=[DataRequired()])
    pagemeta = TextAreaField("pagemeta", validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")
