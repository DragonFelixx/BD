from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.debug import console

from models import User, Character, Gender, Race
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length

from models import *


class CharacterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
    age = IntegerField('Age', validators=[DataRequired()])
    gender_id = SelectField('Gender', coerce=int, validators=[DataRequired()])
    custom_gender = StringField('Custom Gender', validators=[Length(max=50)])
    race_id = SelectField('Race', coerce=int, validators=[DataRequired()])
    custom_race = StringField('Custom Race', validators=[Length(max=50)])
    description = StringField('Description', validators=[DataRequired(), Length(max=500)])


# Функции для Flask-Login
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    characters = Character.query.all()
    return render_template('index.html', characters=characters, current_user=current_user)


@staticmethod
def get(user_id):
    return User.query.get(int(user_id))


#
@login_required
@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html')


@app.route('/profile')
@login_required
def profile():
    is_own_profile = True
    characters = Character.query.filter_by(user_id=current_user.user_id).all()
    return render_template('profile.html', user=current_user, characters=characters, is_own_profile=is_own_profile)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))

        flash('Invalid login or password')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        nickname = request.form['nickname']

        if not login or not password or not nickname:
            flash('All fields are required')
            return redirect(url_for('register'))

        user = User.query.filter_by(login=login).first()
        if user:
            flash('This login is already taken')
            return redirect(url_for('register'))

        user = User(login=login, password=generate_password_hash(password), nickname=nickname)
        db.session.add(user)
        db.session.commit()

        flash('You have been registered successfully. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')


# @app.route('/character/<int:character_id>')
# def view_character(character_id):
#

@app.route('/characters/<int:character_id>')
def view_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        return {'message': 'Character not found'}, 404

    # получаем данные о пользователе, поле "gender" и "race" персонажа
    user = User.query.get(character.user_id)
    gender = Gender.query.get(character.gender_id)
    race = Race.query.get(character.race_id)

    # проверяем, если у персонажа пользовательское значение для поля "gender" и "race"
    if character.custom_gender:
        gender_name = character.custom_gender
    else:
        gender_name = gender.name

    if character.custom_race:
        race_name = character.custom_race
    else:
        race_name = race.name

    # формируем информацию о персонаже для отображения на странице
    character_info = {
        'name': character.name,
        'age': character.age,
        'gender': gender_name,
        'race': race_name,
        'description': character.description,
        'user_nickname': user.nickname
    }

    return render_template('view_character.html', character=character_info, character_id=character_id)


@app.route('/characters/<int:character_id>', methods=['DELETE'])
@login_required
def delete_character(character_id):
    character = Character.query.get(character_id)
    if character is None or current_user != character.user:
        abort(404)
    db.session.delete(character)
    db.session.commit()
    print(f"Deleted character with id {character_id}")
    return '', 204


@app.route('/create_character', methods=['GET', 'POST'])
@login_required
def create_character():
    form = CharacterForm()
    genders = Gender.query.all()
    races = Race.query.all()
    form.gender_id.choices = [(g.gender_id, g.name) for g in genders]
    form.race_id.choices = [(r.race_id, r.name) for r in races]
    if form.validate_on_submit():
        character = Character(user_id=current_user.user_id,
                              name=form.name.data,
                              age=form.age.data,
                              gender_id=form.gender_id.data,
                              custom_gender=form.custom_gender.data,
                              race_id=form.race_id.data,
                              custom_race=form.custom_race.data,
                              description=form.description.data)
        db.session.add(character)
        db.session.commit()
        flash('Your character has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_character.html', title='Create Character', form=form, genders=genders, races=races)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
