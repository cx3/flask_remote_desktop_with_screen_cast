from server import app, config

if __name__ == "__main__":
    app.run(config['host'], config['port'], config['debug'])
