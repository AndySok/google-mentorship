from flask import render_template, flash, redirect, request, url_for, session
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddMedicationForm, FindMedicationForm, ProfileForm, TakenForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Medicine, Cycle
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
        user.create_cycles()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/update_info', methods=['GET', 'POST'])
@login_required
def update_info():
    if current_user.check_privileges():
        form = ProfileForm()
        if form.validate_on_submit():
            current_user.fname=form.fname.data
            current_user.lname=form.lname.data
            current_user.email=form.email.data
            current_user.update_privileges=form.update_privileges.data
            db.session.commit()
            flash('Your changes have been saved.')
        elif request.method == 'GET':
            form.fname.data = current_user.fname
            form.lname.data = current_user.lname
            form.email.data = current_user.email
            form.update_privileges.data = current_user.update_privileges
        email = current_user.email
        return render_template('register.html', title='Update Info', form=form, email=email)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('index'))

@app.route('/medication', methods=['GET', 'POST'])
@login_required
def medication():
    medications = current_user.medicines
    form = TakenForm()
    #for medication in medications:
    #    if form.validate_on_submit():
    #        if current_user.check_privileges():
    #            medication.add_to_cycle(form.cycle.data)
    #        else:
    #            flash('You do not have update privileges')
    #        medication.taken = medication.taken
    #        db.session.commit()
    #        flash('Your changes have been saved.')
    #        return redirect(url_for('medication'))
    #    if request.method == 'GET':
    #        form.cycle.data = medication.cycle.cycle
    #        form.taken.data = medication.taken
    #if form.validate_on_submit():
    #    for i in range(0, len(medications)):
    #        medications[i].taken = [form.medications.taken[i]]
    #elif request.method == 'GET':
    #    form.medications.taken = [medication.taken for medication in medications]
    cycles = current_user.cycles
    print(cycles)
    return render_template('medication.html', title='Medication', medications=medications, form=form, cycles=cycles)

@app.route('/add_medication', methods=['GET', 'POST'])
@login_required
def add_medication():
    if current_user.check_privileges():
        form = AddMedicationForm()

        form.cycles.choices = [(cycle.id, cycle.name) for cycle in current_user.cycles]

        if form.validate_on_submit():
            medication = Medicine(name = form.name.data, dose = form.dose.data,
                pills = form.pills.data, period = form.period.data, user = current_user)

            cycles = Cycle.query.filter(Cycle.id.in_(form.cycles.data)).all()
            medication.cycles = cycles

            db.session.add(medication)
            db.session.commit()

            flash('Congratulations, you have entered new medication!')
            return redirect(url_for('medication'))
        return render_template('add_medication.html', title='Add Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/choose_medication', methods=['GET', 'POST'])
@login_required
def choose_medication():
    if current_user.check_privileges():
        form = FindMedicationForm()
        if form.validate_on_submit():
            medication = Medicine.query.filter_by(name=form.name.data, user_id=current_user.id).first()
            if medication is None:
                flash('This product does not exist')
                return redirect(url_for('choose_medication'))
            elif current_user.med_authenticated(medication.id):
                return redirect(url_for('edit_medication', medication_id=medication.id))
                flash('You are not authorized to update this medication')
            return render_template(url_for('choose_medication'))
        return render_template('choose_medication.html', title='Choose Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/edit_medication/<medication_id>', methods=['GET', 'POST'])
@login_required
def edit_medication(medication_id):
    if current_user.check_privileges() and current_user.med_authenticated(medication_id):
        medication = Medicine.query.filter_by(id=medication_id).first()
        form = AddMedicationForm()
        form.cycles.choices = [(cycle.id, cycle.name) for cycle in current_user.cycles]
        form.cycles.data = [cycle.id for cycle in medication.cycles]

        print(form.cycles.data)

        if form.validate_on_submit():
            medication.name = form.name.data
            medication.dose = form.dose.data
            medication.pills = form.pills.data
            medication.period = form.period.data

            cycles = Cycle.query.filter(Cycle.id.in_(form.cycles.data)).all()
            medication.cycles = cycles

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
    if current_user.check_privileges() and current_user.med_authenticated(medication_id):
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

@app.route('/taken_med/<med_id>/<done>', methods=['GET', 'POST'])
@login_required
def taken_med(med_id, done):
    if current_user.med_authenticated(med_id):
        medication = Medicine.query.filter_by(id=med_id, user_id=current_user.id).first()
        if (done == "yes"):
            medication.taken = True
        else:
            medication.taken = False
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('medication'))
    else:
        flash('Not authenticated to make changes.')
