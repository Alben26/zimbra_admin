import re

from flask_wtf import Form
from wtforms.fields import BooleanField, TextField, PasswordField
from wtforms.validators import EqualTo, Email, InputRequired, Length

from ..data.models import User
from ..fields import Predicate

def email_is_available(email):
    if not email:
        return True
    return not User.find_by_email(email)

def username_is_available(username):
    if not username:
        return True
    return not User.find_by_username(username)

def safe_characters(s):
    " Only letters (a-z) and  numbers are allowed for usernames and passwords. Based off Google username validator "
    if not s:
        return True
    return re.match(r'^[\w]+$', s) is not None
def domain_validate(s):
    if not s:
        return True
    return re.match(r'(\.|\/)(([A-Za-z\d]+|[A-Za-z\d][-])+[A-Za-z\d]+){1,63}\.([A-Za-z]{2,3}\.[A-Za-z]{2}|[A-Za-z]{2,6})', s) is not None


class EmailForm(Form):
    email = TextField('Email Address', validators=[
        Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])
class DomainForm(Form):
    email = TextField('Domain Address', validators=[
        #Predicate(domain_validate, message="Please use domain name"),
        InputRequired(message="You can't leave this empty")
    ])
class LoginForm(DomainForm):
    password = PasswordField('Password', validators=[
        InputRequired(message="You can't leave this empty")
    ])

    remember_me = BooleanField('Keep me logged in')

class ResetPasswordForm(Form):
    password = PasswordField('New password', validators=[
        EqualTo('confirm', message='Passwords must match'),
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

    confirm = PasswordField('Repeat password')


class RegistrationForm(Form):
    username = TextField('Choose your username', validators=[
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Predicate(username_is_available,
                  message="An account has already been registered with that username. Try another?"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

    email = TextField('Your email address', validators=[
        Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])

    password = PasswordField('Create a password', validators=[
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

class NewUserForm(Form):
    email = TextField('Your new email address', validators=[
        #Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        #Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])
    displayname = TextField('Prefered Display Name', validators=[
        #Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        #Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])
    password = PasswordField('New password', validators=[
#        EqualTo('confirm', message='Passwords must match'),
        Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])

class EditUserForm(Form):
    displayname = TextField('Prefered Display Name', validators=[
        #Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        #Email(message="Please enter a valid email address"),
        #InputRequired(message="You can't leave this empty")
    ])

class ChangePasswordForm(Form):
    password = TextField('New password', validators=[
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        #Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        #Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])

class DelUserForm(Form):
    email = TextField('Email address you want delete.', validators=[
        #Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        #Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])


class NewAliasForm(Form):
        alias = TextField('Enter a new alias', validators=[
        Length(min=3, max=10, message="Please use between 6 and 30 characters"),
        #Predicate(email_is_available, message="An account has already been reigstered with that email. Try another?"),
        #Email(message="Please enter a valid email address"),
        InputRequired(message="You can't leave this empty")
    ])

###
class DomainForm(Form):
    domainname = TextField('Choose your name for domain', validators=[
        #Predicate(safe_characters, message="Please use only letters (a-z) and numbers"),
        Predicate(username_is_available,
                  message="A domain has already been registered with that name. Try another?"),
        Length(min=3, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="You can't leave this empty")
    ])
###