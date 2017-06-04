from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from gamesess.models import Base, Gamer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamesess_test1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'guess_my_secret_and_difficult_key'

db = SQLAlchemy(app)
db.Model = Base

from flask import session
from flask.ext.login import LoginManager, current_user
from flask.ext.login import login_user, logout_user, login_required

# Flask-Login initialization
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """ Flask-Login hook to load a User instance from ID """
    return db.session.query(Gamer).get(int(user_id))
    
@app.route('/')
def main():
    return u'Hello, Flask Game Club Sessions !<br/><a href="/clubs">List of your clubs</a>'

@app.route('/about')
def about():
    return str(current_user)+'Auth:'+str(current_user.is_authenticated)+'About Flask Game Club Sessions'

@app.route('/clubs')
@login_required
def clubs_list():
    return 'List of clubs'

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

# Flask-Login calls
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('clubs_list'))
    form = LoginForm(request.form)
    error = None
    if request.form == 'POST' and form.validate():
        email = form.username.data.lower().strip()
        password = form.password.data.strip()
        user, authenticated = User.authenticate(db.session.query, email, password)
        if authenticated:
            login_user(user)
            return redirect(url_for('clubs_list'))
        else:
            error = 'Incorrect username or password'
        return render_template('user/login.html', form=form, error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run('0.0.0.0',8002,debug=True)
