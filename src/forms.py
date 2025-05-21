# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from src.db import get_user_by_username

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 128)])
    confirm  = PasswordField('Confirm Password',
                             validators=[DataRequired(),
                                         EqualTo('password', message='Passwords must match')])
    submit   = SubmitField('Register')

    def validate_username(self, field):
        if get_user_by_username(field.data):
            raise ValidationError('Username already taken.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3,25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit   = SubmitField('Log In')
