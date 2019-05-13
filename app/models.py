from datetime import datetime
from hashlib import md5
from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt
import cloudinary

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	dietary_restrictions = db.Column(db.String(128))
	picture_url = db.Column(db.String(200))

	dinners = db.relationship("Dinner", backref='author', lazy='dynamic')
	attending = db.relationship("Dinner", secondary="attends")
	bringing = db.relationship("Dinner", secondary="brings")

	def attend(self, dinner):
		if not self.is_attending(dinner):
			dinner.attendees.append(self)

	def unattend(self, dinner):
		if self.is_attending(dinner):
			dinner.attendees.remove(self)

	def is_attending(self, dinner):
		return self in dinner.attendees

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest, size)

	def get_dinners(self):
		return Dinner.query.order_by(Dinner.timestamp.asc())

	def hosting_dinners(self):
		return self.get_dinners() is not None

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	def set_picture(self, url):
		img = cloudinary.CloudinaryImage(url)
		img.build_url(width=100, height=100, crop="fill", gravity="east")
		self.picture_url = str(img)
		db.session.commit()

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
				algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

class NewUser(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True)
	email = db.Column(db.String(120), index=True)
	
	def get_register_token(self, expires_in=600):
		return jwt.encode(
			{'register': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_register_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
				algorithms=['HS256'])['register']
		except:
			return
		return NewUser.query.get(id)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class Dinner(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	address = db.Column(db.String(140))
	date = db.Column(db.DateTime)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	max_attendees = db.Column(db.Integer)
	picture_url = db.Column(db.String(200))

	attendees = db.relationship("User", secondary="attends")
	foods = db.relationship("User", secondary="brings")

	def get_dietary_restrictions(self):
		restrictions = []
		for attendee in self.attendees:
			restrictions.append(attendee.dietary_restrictions)
		return restrictions

	def num_restrictions(self):
		restrictions = self.get_dietary_restrictions()
		return len(restrictions)

	def count_restrictions(self):
		restrictions = self.get_dietary_restrictions()
		ret_map = {}

		for i in restrictions:
			if str(i) not in ret_map.keys():
				ret_map[str(i)] = 1
			else:
				ret_map[str(i)] += 1
		return ret_map

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def get_num_of_attendees(self):
		count = 0
		for attendee in self.attendees:
			count += 1
		return count

	def is_full(self):
		if self.max_attendees is None:
			return False
		count = 0
		for attendee in self.attendees:
			count += 1
		if count >= self.max_attendees:
			return True
		return False

	def set_picture(self, url):
		img = cloudinary.CloudinaryImage(url)
		img.build_url(width=400, height=200, crop="fill", gravity="east")
		self.picture_url = str(img)
		db.session.commit()

	def __repr__(self):
		return '<Dinner {}>'.format(self.body)

class Attends(db.Model):
	__tablename__ = 'attends'
	id = db.Column(db.Integer, primary_key=True)
	attendee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	dinner_id = db.Column(db.Integer, db.ForeignKey('dinner.id'))
	user = db.relationship(User, backref=db.backref("attends", cascade="all, delete-orphan"))
	dinner = db.relationship(Dinner, backref=db.backref("attends", cascade="all, delete-orphan"))

class Brings(db.Model):
	__tablename__ = 'brings'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	dinner_id = db.Column(db.Integer, db.ForeignKey('dinner.id'))
	item = db.Column(db.String(140))
	user = db.relationship(User, backref=db.backref("brings", cascade="all, delete-orphan"))
	dinner = db.relationship(Dinner, backref=db.backref("brings", cascade="all, delete-orphan"))


		