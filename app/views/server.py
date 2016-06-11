# -*- coding: utf-8 -*-
from flask import render_template
from flask_socketio import send, emit

from app import app, socketio


@app.route('/test')
def test():
    return render_template('test.html')


def ask():
    print 'it has recived'


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    return 'one', 2


@app.route('/server', methods=['GET', 'POST'])
def add_server():
    return render_template('server.html')
