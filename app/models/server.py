# -*- coding: utf-8 -*-
from app import db


class ServerModel(db.Model):
    __tablename__ = 'server'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(256), nullable=False, index=True)
    Ip = db.Column(db.String(64), nullable=False, index=True)
    create_on = db.Column(
        db.TIMESTAMP,
        index=True,
        server_default=db.func.current_timestamp()
    )
