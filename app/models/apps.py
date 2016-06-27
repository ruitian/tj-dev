# -*- coding: utf-8 -*-
from app import db

from .app_server import AppServer


class AppModel(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    containerId = db.Column(db.String(256), index=True)
    verify = db.Column(db.String(256), nullable=False, index=True)
    appname = db.Column(db.String(256), nullable=False, index=True)
    port = db.Column(db.String(64))
    image = db.Column(db.String(256), index=True)
    host = db.Column(db.String(128))
    create_on = db.Column(
        db.TIMESTAMP,
        index=True,
        server_default=db.func.current_timestamp()
    )
