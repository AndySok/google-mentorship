from flask import render_template, flash, redirect, request, url_for, session
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddMedicationForm, CaretakerAddMedicationForm, CaretakerFindMedicationForm, FindMedicationForm, FindCaretakerForm, ProfileForm, EmptyForm
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
        patient=form.patient.data
        user = User(fname=fname, lname=lname, email=email, update_privileges=update_privileges, isPatient=patient)
        user.set_password(form.password.data)
        user.create_cycles()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('user_info.html', title='Register', form=form)

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
        return render_template('user_info.html', title='Update Info', form=form, email=email, user=current_user)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('index'))

@app.route('/medication', methods=['GET', 'POST'])
@login_required
def medication():
    medications = current_user.medicines
    cycles = current_user.cycles
    return render_template('medication.html', title='Medication', medications=medications, cycles=cycles)


@app.route('/add_medication', methods=['GET', 'POST'])
@login_required
def add_medication():
    if current_user.check_privileges():
        if current_user.is_patient():
            form = AddMedicationForm()

        else:
            form = CaretakerAddMedicationForm()
        form.cycles.choices = [(cycle.id, cycle.name) for cycle in current_user.cycles]

        if form.validate_on_submit():
            if current_user.is_patient():
                med_user = current_user
            else:
                med_user = User.query.filter_by(email=form.email.data).first()
                if med_user is None:
                    flash('User {} not found'.format(form.email.data))
                    return redirect(url_for('medication'))
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
        if current_user.is_patient():
            form = FindMedicationForm()
        else:
            form = CaretakerFindMedicationForm()
        if form.validate_on_submit():
            if current_user.is_patient():
                med_user = current_user
            else:
                med_user = User.query.filter_by(email=form.email.data).first()
                if med_user is None:
                    flash('User {} not found'.format(form.email.data))
                    return redirect(url_for('medication'))
            medication = Medicine.query.filter_by(name=form.name.data, user_id=med_user.id).first()
            if medication is None:
                flash('This medication does not exist')
                return redirect(url_for('medication'))
            elif current_user.med_authenticated(medication.id):
                return redirect(url_for('edit_medication', medication_id=medication.id))
            flash('You are not authorized to update this medication')
            return render_template(url_for('medication'))
        return render_template('search.html', title='Choose Medication', form=form)
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
            form.cycles.data = [cycle.id for cycle in medication.cycles]

        return render_template('add_medication.html', title='Edit Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/delete_medication', methods=['GET', 'POST'])
@login_required
def delete_medication():
    if current_user.check_privileges():
        if current_user.is_patient():
            form = FindMedicationForm()
        else:
            form = CaretakerFindMedicationForm()
        if form.validate_on_submit():
            if current_user.is_patient():
                med_user = current_user
            else:
                med_user = User.query.filter_by(email=form.email.data).first()
                if med_user is None:
                    flash('User {} not found'.format(form.email.data))
                    return redirect(url_for('medication'))
            medication = Medicine.query.filter_by(name=form.name.data, user_id=med_user.id).first()
            if medication is None:
                flash('This medication does not exist')
                return redirect(url_for('delete_medication'))
            if current_user.med_authenticated(medication.id):
                db.session.delete(medication)
                db.session.commit()
                flash('Medication deleted successfully')
            else:
                flash('You are not authenticated for this medication')
            return redirect(url_for('medication'))
        return render_template('search.html', title='Delete Medication', form=form)
    else:
        flash('You do not have update privileges.')
        return redirect(url_for('medication'))

@app.route('/taken_med/<med_id>/<done>', methods=['GET', 'POST'])
@login_required
def taken_med(med_id, done):
    if current_user.med_authenticated(med_id):
        medication = Medicine.query.filter_by(id=med_id).first()
        if (done == "yes"):
            medication.taken = True
        else:
            medication.taken = False
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('medication'))
    else:
        flash('Not authenticated to make changes.')

@app.route('/caretaker_search', methods=['GET', 'POST'])
@login_required
def caretaker_search():
    form = FindCaretakerForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('This user does not exist')
            return redirect(url_for('caretaker_search'))
        return redirect(url_for('caretaker', user_id=user.id))
    return render_template('search.html', title='Add Caretaker', form=form)

@app.route('/caretaker/<user_id>', methods=['GET', 'POST'])
@login_required
def caretaker(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User {} not found.'.format(user_id))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot add yourself as a caretaker!')
    set = current_user.set_caretaker(user)
    if set == 0:
        db.session.commit()
        flash('You set {} as a caretaker!'.format(user.fname))
    elif set == 1:
        flash('{} is not a caretaker!'.format(user.fname))
    elif set == 2:
        flash('{} is already your caretaker!'.format(user.fname))
    return redirect(url_for('index'))
