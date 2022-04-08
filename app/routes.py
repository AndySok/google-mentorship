from flask import render_template, flash, redirect, request, url_for, session
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddMedicationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Medicine
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first()
        return render_template('index.html', title='Home Page', user=user)
    guest = User.query.filter_by(username="guest").first()
    return render_template('index.html', title='Home Page', user=guest)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/add_medication', methods=['GET', 'POST'])
@login_required
def add_medication():
    form = AddMedicationForm()
    if form.validate_on_submit():
        medication = Medicine(name = form.name.data, dose = form.dose.data,
            pills = form.pills.data, period = form.period.data, user = current_user)
        db.session.add(medication)
        db.session.commit()
        flash('Congratulations, you have entered new medication!')
    return render_template('add_medication.html', title='Add Medication', form=form)
