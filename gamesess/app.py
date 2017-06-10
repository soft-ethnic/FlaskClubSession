from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template, redirect, request, url_for, flash

from gamesess.models import Base, Gamer, Club, Game, GameSession
from gamesess.forms import LoginForm

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

# Flask-Bootstrap initialization
from flask.ext.bootstrap import Bootstrap
bootstrap = Bootstrap(app)

from werkzeug.security import generate_password_hash, check_password_hash
# End of extensions initializations

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/about')
def about():
    return str(current_user)+'Auth:'+str(current_user.is_authenticated)+'About Flask Game Club Sessions'

@app.route('/clubs')
@login_required
def clubs_list():
    clubs = db.session.query(Club).filter_by(public=True).order_by(Club.name).all()
    return render_template('club_list.html',clubs = clubs)

@app.route('/myclubs')
@login_required
def user_clubs_list():
    return 'List of clubs for the current user'

@app.route('/club/<int:club_id>/')
@login_required
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
@login_required
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
    form = LoginForm()
    if form.validate_on_submit():
        #user = Gamer.query.filter_by(email=form.email.data).first()
        user = db.session.query(Gamer).filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or '/')
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect('/')
# EOF Flask-Login class

if __name__ == '__main__':
    app.run('0.0.0.0',8002,debug=True)
