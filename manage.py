from flask_script import Manager
from gamesess.app import app

manager = Manager(app)
app.config['DEBUG'] = True # Enable debugger

if __name__ == '__main__':
    manager.run()
