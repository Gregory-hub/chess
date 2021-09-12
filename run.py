from chess import app, socketio, host, port


if __name__ == '__main__':
    socketio.run(app, debug=True, host=host, port=port)
