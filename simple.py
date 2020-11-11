from flask import Flask, redirect, url_for, render_template, request
from flask_login import LoginManager, current_user, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from clue import Game
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '1faf50e934b6df68fdc808d2fbad63ba'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'welcome'


clue = Game()

players = []
responder = ''
guess = ''

people = ['Professor Plum', 'Mrs. Peacock', 'Mrs. White', 'Miss Scarlett', 'Mr. Green', 'Colonel Mustard']
weapons = ['Candlestick', 'Dagger', 'Lead Pipe', 'Revolver', 'Rope', 'Wrench']
rooms = ['Kitchen', 'Ballroom', 'Conservatory', 'Dining room', 'Lounge', 'Hall', 'Study', 'Library', 'Billiard Room']
all_things = [people, weapons, rooms]
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

#set up user class
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True, nullable=False)
	is_guesser = False
	is_responder = False

	def __repr__(self):
		return f"User('{self.name}')"


#forms
class WelcomeForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	submit = SubmitField('Enter')

class StartForm(FlaskForm):
	submit = SubmitField('start')

class GameForm(FlaskForm):
	person = RadioField('Person', choices=[('Professor Plum','Professor Plum'), ('Mrs. Peacock', 'Mrs. Peacock'), ('Mrs. White', 'Mrs. White'), ('Miss Scarlett', 'Miss Scarlett'), ('Mr. Green', 'Mr. Green'), ('Colonel Mustard', 'Colonel Mustard')])
	weapon =  RadioField('Weapon', choices=[('Dagger','Dagger'),('Rope','Rope'), ('Candlestick', 'Candlestick'), ('Revolver', 'Revolver'), ('Wrench', 'Wrench'), ('Lead Pipe', 'Lead Pipe')])
	room =  RadioField('Room', choices=[('Kitchen','Kitchen'),('Study', 'Study'), ('Hall', 'Hall'), ('Library', 'Library'), ('Dining Room', 'Dining Room'), ('Lounge', 'Lounge'), ('Billiard Room', 'Billiard Room'), ('Conservatory', 'Conservatory'), ('Ballroom', 'Ballroom')])
	submit = SubmitField('Guess')

class ResponderForm(FlaskForm):
	reveal = RadioField('Which do you reveal', choices='')
	submit = SubmitField('Reveal')



#routes
@app.route('/')
def go_to_welcome():
	return redirect(url_for('welcome'))

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
	form = WelcomeForm()
	try:
		players.remove(current_user)
	except:
		pass
	logout_user()
	if form.validate_on_submit():
		user = User.query.filter_by(name=form.name.data).first()
		if user:
			if user not in players:
				players.append(user)
			login_user(user)
		else:
			user = User(name=form.name.data)
			db.session.add(user)
			db.session.commit()
			if user not in players:
				players.append(user)
			login_user(user)
		return redirect(url_for('sessions'))
	return render_template('welcome.html', title='welcome', form=form)

@app.route("/sessions", methods=['GET', 'POST'])
@login_required
def sessions():
	form = StartForm()
	if form.validate_on_submit():
		return redirect(url_for('waiting'))
	return render_template('session.html', form=form, players=players, user=current_user)

@app.route('/waiting')
@login_required
def waiting():
	if not clue.is_started:
		clue.start(players)
	if clue.winner:
		return redirect(url_for('end'))
	if current_user == players[clue.players_turn] and not clue.guess:
		return redirect(url_for('guessing'))
	elif current_user == players[clue.responder] and clue.guess:
		print(current_user.name + ' is responding')
		return redirect(url_for('respond'))
	return render_template('game.html', clue=clue, current_user=current_user, all_things=all_things)

@app.route("/guessing", methods=['GET', 'POST'])
@login_required
def guessing():
	form = GameForm()
	if form.validate_on_submit():
		guess = [form.person.data, form.weapon.data, form.room.data]
		if guess == clue.solution:
			return redirect(url_for('winning'))
		clue.make_guess(guess, players)
		return redirect(url_for('waiting'))
	current_user.is_guesser = True
	return render_template('guesser.html', form=form, clue=clue, current_user=current_user, all_things=all_things)

@app.route('/respond', methods=['GET', 'POST'])
@login_required
def respond():
	form = ResponderForm()
	if request.method == 'POST':
		reveal = form.reveal.data
		current_user.is_responder = False
		if reveal not in clue.known[players[clue.players_turn].name]:
			clue.known[players[clue.players_turn].name].append(reveal)
		clue.new_turn()
		try:
			print(players[clue.responder].name + 'is the new responder')
		except IndexError:
			clue.responder = 0
			print(players[clue.responder].name + 'is the new responder')
		try:
			print(players[clue.players_turn].name + 'is the new responder')
		except IndexError:
			clue.players_turn = 0
			print(players[clue.players_turn].name + 'is the new responder')
		return redirect(url_for('waiting'))
	if current_user.name in clue.right.values():
			current_user.is_responder = True
			choices = []
			for item in clue.guess:
				if item in clue.hands[current_user.name]:
					choices.append((item, item))
			form.reveal.choices = choices
			return render_template('responder.html', clue=clue, current_user=current_user, form=form, all_things=all_things)
	else:
		clue.responder += 1
		if clue.responder == clue.players_turn:
			clue.responder +=1
		try:
			print(players[clue.responder].name + 'is the new responder')
			return redirect(url_for('waiting'))
		except:
			clue.responder = 0
			if clue.responder == clue.players_turn:
				clue.responder +=1
			return redirect(url_for('waiting'))

@app.route('/winning')
@login_required
def winning():
	clue.winner = current_user.name
	return clue.winner + ' has won.'

@app.route('/end')
@login_required
def end():
	return clue.winner + ' has won.'

@app.route('/boardtest')
def boardtest():
	return render_template('board.html', board=url_for('static', filename='/images/GameboardClue.jpg'), piece=[0,0] )


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')