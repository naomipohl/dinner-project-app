from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField
#from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User
from wtforms.fields.html5 import DateField

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')

class RegistrationPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')


class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
	dietary_restrictions = RadioField('Dietary Restrictions', 
		choices = [('None','None'),('Vegetarian','Vegetarian'),('Pescatarian','Pescatarian'),
		('Vegan','Vegan'),('Gluten-Free','Gluten-Free')])
	submit = SubmitField('Submit')

	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username.')

class DinnerForm(FlaskForm):
	dinner = TextAreaField(validators=[
		DataRequired(), Length(min=1, max=140)])
	address = TextAreaField(validators=[
		DataRequired(), Length(min=1, max=140)])
	date = DateField(format='%Y-%m-%d', validators=[
		DataRequired()])
	max_attendees = IntegerField(validators=[
		DataRequired()])
	submit = SubmitField('Let\'s Eat!')

class BringingForm(FlaskForm):
	bringing = TextAreaField('What are you bringing??:', validators=[
		DataRequired(), Length(min=1, max=140)])
	submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Request Password Reset')




