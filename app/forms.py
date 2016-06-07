# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp


class LoginForm(Form):
    username_or_email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField(u'登录')


class RegisterForm(Form):
    email = StringField(validators=[DataRequired(), Email()])
    username = StringField(validators=[
        DataRequired(),
        Length(3, 20),
        Regexp('[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Nickname must have only letter, '
               'numbers, dots and underscores')
    ])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField(u'添加')
