# -*- coding: utf-8 -*-
from app import db


class ProjectModel(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    proname = db.Column(db.String(256), nullable=False, index=True)
    address = db.Column(db.String(256), nullable=False, index=True)
    verify = db.Column(db.String(256), nullable=False, index=True)
    build = db.Column(db.Boolean, default=False)
    create_on = db.Column(
        db.TIMESTAMP,
        index=True,
        server_default=db.func.current_timestamp()
    )

    def is_build(self):
        return self.build

    def will_build(self):
        self.build = True
