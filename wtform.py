from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from db import User

def invalid_details(form, field):

    username_entered = form.username.data
    password_entered = field.data

    user_object = User.query.filter_by(username=username_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif password_entered != user_object.password:
        raise ValidationError("Username or password is incorrect")


class RegistrationForm(FlaskForm):
    username = StringField('username', 
        validators=[InputRequired(message="Username required"), 
        Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    password = PasswordField('password', 
        validators=[InputRequired(message="Password required"), 
        Length(min=4, max=25, message="Password must be between 4 and 25 characters")])
    confirm_pswd = PasswordField('confirm_pswd', 
        validators=[InputRequired(message="Password required"), 
        EqualTo('password', message="Passwords must match")])
    submit_button = SubmitField('Create')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Type a different username.")


class LoginForm(FlaskForm):
        username = StringField('username_label', 
            validators=[InputRequired(message="Username required")])
        password = PasswordField('password', 
            validators=[InputRequired(message="Password required"), invalid_details])

        submit_button = SubmitField('Login')