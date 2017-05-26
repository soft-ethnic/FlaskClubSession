from flask import Flask
from flask.ext.alchemy import SQLAlchemy

from shed.models import Base

app = Flask(__name__)
app.config[] = 'sqlite:///clubsession.db'

db = SQLAlchemy(app)
db.Model = Base

@app.route('/')
def main():
    return u'Hello, Flask Game Club Sessions !'

@app.route('/club/<int:club_id>/')
def club_details(club_id):
    return 'Details on club %i' % club_id

@app.route('/session/<int:session_id>/')
@app.route('/soiree/<int:session_id>/')
@app.route('/weekend/<int:session_id>/')
def session_details(session_id):
    return 'Details on session %i' % session_id

@app.route('/table/<int:table_id>/')
def table_details(table_id):
    return 'Details on table %i' % table_id

@app.route('/gamer/<int:gamer_id>/')
def gamer_details(gamer_id):
    return 'Details on gamer %i' % gamer_id

@app.route('/game/<int:game_id>/')
def game_details(game_id):
    return 'Details on game/scenario %i' % game_id

@app.route('/get_image')
def get_urban_image():
    return 'image', 200, {'Content-Type':'image/jpeg'}

if __name__ == '__main__':
    app.run('0.0.0.0',8002,debug=True)
