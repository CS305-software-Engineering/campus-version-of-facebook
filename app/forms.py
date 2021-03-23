from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, ValidationError
from app.models import *
import datetime

def invalid_credentials(form,field):
    mail_id_entered = form.mail_id.data
    password_entered = field.data
    user_object = Credentials.query.filter_by(mail_id = mail_id_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif password_entered!=user_object.password:
        raise ValidationError("Username or password is incorrect")

def invalid_mail(form,field):
    mail_id_entered = form.mail_id.data
    user_object = Credentials.query.filter_by(mail_id=mail_id_entered).first()
    if user_object:
        raise ValidationError("Email already exists.")


def invalid_password(form,field):
    password_entered = field.data
    password_re_entered = form.confirm_password.data
    if password_entered != password_re_entered:
        raise ValidationError("Passwords entered don't match")

class LoginForm(FlaskForm):
    mail_id = StringField('mail_id', validators=[InputRequired(message = "Username required")])
    password = PasswordField('Password', validators=[InputRequired(message = "Password required"),invalid_credentials])


class RegistrationForm(FlaskForm):
    mail_id = StringField('mail_id',validators=[InputRequired(message = "Mail already exists"), invalid_mail])
    password = PasswordField('password',validators=[InputRequired(message = "Password mismatch"),invalid_password])
    confirm_password = PasswordField('confirm_password')
    full_name = StringField('full_name')
    year = IntegerField('year')
    department = StringField('department')
    degree = StringField('degree')

