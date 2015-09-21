from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)



@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 5, 'r':255, 'g':255, 'b':0})
    emit('my response', {'data': 6, 'r':255, 'g':255, 'b':0})
    time.sleep(1)
    emit('my response', {'data': 5, 'r':0, 'g':0, 'b':0})
    emit('my response', {'data': 6, 'r':255, 'g':255, 'b':0})
    emit('my response', {'data': 7, 'r':255, 'g':255, 'b':0})
    time.sleep(1)
    emit('my response', {'data': 6, 'r':0, 'g':0, 'b':0})
    emit('my response', {'data': 7, 'r':255, 'g':255, 'b':0})
    emit('my response', {'data': 8, 'r':255, 'g':255, 'b':0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
