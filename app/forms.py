# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Email, Length, Regexp


class LoginForm(Form):
    username_or_email = StringField(validators=[Required()])
    password = PasswordField(validators=[Required()])
    submit = SubmitField(u'登录')


class RegisterForm(Form):
    email = StringField(validators=[Required(), Email()])
    username = StringField(validators=[
        Required(),
        Length(3, 20),
        Regexp('[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Nickname must have only letter, '
               'numbers, dots and underscores')
    ])
    password = PasswordField(validators=[Required()])
    submit = SubmitField(u'添加')


class ServerForm(Form):
    nickname = StringField(validators=[Required()])
    ip = StringField(validators=[Required()])
    submit = SubmitField(u'提交')
