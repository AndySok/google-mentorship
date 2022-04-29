from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, FieldList
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

class ProfileForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    update_privileges = BooleanField('Update Privileges')
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class AddMedicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    dose = FloatField('Dose (mg)', validators=[DataRequired()])
    cycle = FloatField('Cycle', validators=[DataRequired()])
    pills = IntegerField('Pills per Cycle', validators=[DataRequired()])
    period = FloatField('Period (hrs)', validators=[DataRequired()])
    submit = SubmitField('Add')

class FindMedicationForm(FlaskForm):
    name = StringField('Medication Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CycleTakenForm(FlaskForm):
    cycle = IntegerField('Cycle', validators=[DataRequired()])
    taken = BooleanField('Taken', validators=[DataRequired()])
    submit = SubmitField('Update Changes')
