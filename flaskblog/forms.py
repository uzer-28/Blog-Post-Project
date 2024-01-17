from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):

    username = StringField('Username',validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(me, username):                                        #this fun is created to check if there is a username already existing
        user = User.query.filter_by(username=username.data).first()             #if username exits then ValidationError will be raised and msg will be shown
        if user:
            raise ValidationError('Username already exits. Try using another username!')

    def validate_email(me, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exits. Try using another mail!')


class LoginForm(FlaskForm):

    email = StringField('Email',validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Field')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):                                    #to change the username and email of user.

    username = StringField('Username',validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators = [DataRequired(), Email()])
    picture = FileField('Change profile picture', validators = [FileAllowed(['jpg','png'])])
    submit = SubmitField('Save')

    def validate_username(me, username):                                     #if username/email is not equal to current username then username will be queried from database
        if username.data != current_user.username:                            #if the username/email is found in the database then the validationerror msg will be displayed
           user = User.query.filter_by(username=username.data).first()       #& if not found then the username/email will be passed to routes.py-account for update
           if user:
              raise ValidationError('Username already exits. Try using another username!')

    def validate_email(me, email):
        if email.data != current_user.email:
           user = User.query.filter_by(email=email.data).first()
           if user:
              raise ValidationError('Email already exits. Try using another mail!')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[ DataRequired() ])
    content = TextAreaField('Content', validators=[ DataRequired() ])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset Password')
    def validate_email(me, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("The email you entered doesn't exists. SignUp first!")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

