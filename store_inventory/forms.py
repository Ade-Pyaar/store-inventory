from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.core import IntegerField

from wtforms.validators import DataRequired, EqualTo, ValidationError
from store_inventory.models import User
from flask_login import current_user


class Regform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('That username is taken.')


class Loginform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'autocomplete': 'new-password', 'readonly': "",
     'onfocus':"this.removeAttribute('readonly');"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class Updateform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    old_password = PasswordField("Old Password", validators=[DataRequired()], render_kw={'autocomplete': 'new-password'})
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')

    def validate_name(self, name):
        if name.data != current_user.name:
            user = User.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('That username is taken.')




class RequestResetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user is None:
            raise ValidationError('There is no account with that name.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')