from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:454545foma@localhost/BD_Finder'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'we4fh%gC_za:*8G5v=fbv'

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(db.Model):
    tablename = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    characters = db.relationship('Character', backref='user', lazy=True)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.user_id)

    def is_authenticated(self):
        return True


class Character(db.Model):
    tablename = 'character'
    character_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender_id = db.Column(db.Integer, db.ForeignKey('gender.gender_id'), nullable=False)
    custom_gender = db.Column(db.String(50))
    race_id = db.Column(db.Integer, db.ForeignKey('race.race_id'), nullable=False)
    custom_race = db.Column(db.String(50))
    description = db.Column(db.String(500), nullable=False)


class Race(db.Model):
    tablename = 'race'
    race_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    characters = db.relationship('Character', backref='race', lazy=True)


class Gender(db.Model):
    tablename = 'gender'
    gender_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    characters = db.relationship('Character', backref='gender', lazy=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
