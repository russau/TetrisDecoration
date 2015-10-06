#http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent

from gevent import monkey
# monkey.patch_all()

import time
import random
import Tetris
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)
thread = None

def background_thread():
    while True:
        print "New Tetris class"
        t = Tetris.Tetris(socketio)
        result = True
        result = t.dropPiece(0, 'o', 90)
        result = t.dropPiece(2, 'o', 90)
        result = t.dropPiece(4, 'o', 90)
        result = t.dropPiece(6, 'o', 90)

        result = t.dropPiece(0, 'i', 90)
        result = t.dropPiece(4, 'i', 90)
        while result:
            piece = random.choice(['i','j','l','o','s','t','z'])
            result = t.dropPiece(5, piece, 90)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected')
    global thread
    print "starting thread"
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
