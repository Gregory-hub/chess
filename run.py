from chess import app, socketio, hosts, port, logger


if __name__ == '__main__':
    for host in hosts:
        try:
            socketio.run(app, debug=True, host=host, port=port)
            break
        except Exception as e:
            logger.error(e)
            print(e)
