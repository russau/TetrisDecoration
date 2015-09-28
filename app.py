#http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent
#http://www.alexhadik.com/blog/2015/1/29/using-socketio-with-python-and-flask-on-heroku
# apt-get install python-dev
# apt-get install -y gcc
# pip install  gevent-socketio
# pip install gevent-websocket
# pip install gevent

from gevent import monkey
# monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)
thread = None

def background_thread():
    """Example of how to send server generated events to clients."""
    print "XXXX"
    while True:
        time.sleep(5)
        squares = [{'r':255, 'g':255, 'b':0} for x in range(200)]
        socketio.emit('my response', squares, namespace='/test')
        time.sleep(5)
        squares = [{'r':128, 'g':0, 'b':128} for x in range(200)]
        socketio.emit('my response', squares, namespace='/test')
        time.sleep(5)
        squares = [{'r':0, 'g':0, 'b':255} for x in range(200)]
        socketio.emit('my response', squares, namespace='/test')

@app.route('/')
def index():
    global thread
    print "starting thread"
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
