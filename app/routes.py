from flask import render_template, flash, redirect, request, url_for, session
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddMedicationForm, FindMedicationForm, CyclesForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Medicine
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        return render_template('index.html', title='Home Page', user=user)
    guest = User.query.filter_by(id=1).first()
    return render_template('index.html', title='Home Page', user=guest)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
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
        fname=form.fname.data
        lname=form.lname.data
        email=form.email.data
        update_privileges=form.update_privileges.data
        user = User(fname=fname, lname=lname, email=email, update_privileges=update_privileges)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/update_info', methods=['GET', 'POST'])
@login_required
def update_info():
    if current_user.check_privileges():
        form = RegistrationForm()
        if form.validate_on_submit():
            current_user.fname=form.fname.data
            current_user.lname=form.lname.data
            current_user.email=form.email.data
            current_user.update_privileges=form.update_privileges.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('medication'))
        elif request.method == 'GET':
            form.fname.data = current_user.fname
            form.lname.data = current_user.lname
            form.email.data = current_user.email
            form.update_privileges.data = current_user.update_privileges
        return render_template('register.html', title='Update Info', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('index'))

@app.route('/medication', methods=['GET'])
@login_required
def medication():
    medications = current_user.check_medications()
    return render_template('medication.html', title='Medication', medications=medications)

@app.route('/add_medication', methods=['GET', 'POST'])
@login_required
def add_medication():
    if current_user.check_privileges():
        form = AddMedicationForm()
        if form.validate_on_submit():
            medication = Medicine(name = form.name.data, dose = form.dose.data,
                pills = form.pills.data, period = form.period.data, user = current_user)
            db.session.add(medication)
            db.session.commit()
            flash('Congratulations, you have entered new medication!')
            return redirect(url_for('medication'))
        return render_template('add_medication.html', title='Add Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/choose_medication/<purpose>', methods=['GET', 'POST'])
@login_required
def choose_medication(purpose):
    if current_user.check_privileges():
        form = FindMedicationForm()
        if form.validate_on_submit():
            medication = Medicine.query.filter_by(name=form.name.data, user_id=current_user.id).first()
            if medication is None:
                flash('This product does not exist')
                return redirect(url_for('choose_medication'))
            if purpose == "edit_medication":
                return redirect(url_for('edit_medication', medication_id=medication.id))
            elif purpose == "cycles":
                return redirect(url_for('cycles', medication_id=medication.id))
        return render_template('choose_medication.html', title='Choose Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/edit_medication/<medication_id>', methods=['GET', 'POST'])
@login_required
def edit_medication(medication_id):
    if current_user.check_privileges():
        medication = Medicine.query.filter_by(id=medication_id, user_id=current_user.id).first()
        form = AddMedicationForm()
        if form.validate_on_submit():
            medication.name = form.name.data
            medication.dose = form.dose.data
            medication.pills = form.pills.data
            medication.period = form.period.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('medication'))
        elif request.method == 'GET':
            form.name.data = medication.name
            form.dose.data = medication.dose
            form.pills.data = medication.pills
            form.period.data = medication.period
        return render_template('add_medication.html', title='Edit Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/delete_medication', methods=['GET', 'POST'])
@login_required
def delete_medication():
    if current_user.check_privileges():
        form = FindMedicationForm()
        if form.validate_on_submit():
            medication = Medicine.query.filter_by(name=form.name.data, user_id=current_user.id).first()
            if medication is None:
                flash('This medication does not exist')
                return redirect(url_for('delete_medication'))
            db.session.delete(medication)
            db.session.commit()
            flash('Medication deleted successfully')
            return redirect(url_for('medication'))
        return render_template('choose_medication.html', title='Delete Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/cycles/<medication_id>', methods=['GET', 'POST'])
@login_required
def cycles(medication_id):
    if current_user.check_privileges():
        form = CyclesForm()
        medication = Medicine.query.filter_by(id=medication_id, user_id=current_user.id).first()
        if form.validate_on_submit():
            medication.cycle = form.cycles.data
            db.session.commit()
            flash('Cycle updated successfully')
            return redirect(url_for('medication'))
        return render_template('cycles.html', title='Cycles', form=form, medication=medication.name)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))
