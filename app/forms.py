from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    update_privileges = BooleanField('Update Privileges')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AddMedicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    dose = FloatField('Dose (mg)', validators=[DataRequired()])
    pills = IntegerField('Pills per Cycle', validators=[DataRequired()])
    period = FloatField('Period (hrs)', validators=[DataRequired()])
    submit = SubmitField('Add')

class FindMedicationForm(FlaskForm):
    name = StringField('Medication Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CyclesForm(FlaskForm):
    cycles = IntegerField('Cycle')
    submit = SubmitField('Submit')
