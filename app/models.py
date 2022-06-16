from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import time, timedelta, datetime

#users_medicine = db.Table("Medicine",
#    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id')))

patients = db.Table(
    'patients',
    db.Column('patient_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('caretaker_id', db.Integer, db.ForeignKey('users.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    update_privileges = db.Column(db.Boolean, index=True, default=False)
    password_hash = db.Column(db.String(128))
    isPatient = db.Column(db.Boolean, index=True, default=True)
    caretaker = db.relationship(
        'User', secondary=patients,
        primaryjoin=(patients.c.patient_id == id),
        secondaryjoin=(patients.c.caretaker_id == id),
        backref=db.backref('patients', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.fname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_patient(self):
        return self.isPatient

    def set_caretaker(self, user):
        if not self.is_caretaker(user):
            if not user.is_patient():
                self.caretaker.append(user)
                return 0
            return 1
        return 2

    def delete_caretaker(self, user):
        if self.is_caretaker(user):
            self.caretaker.remove(user)

    def is_caretaker(self, user):
        return self.caretaker.filter(patients.c.caretaker_id == user.id).count() > 0

    def create_cycles(self):
        cycle1 = Cycle(name="Morning", user=self)
        cycle1.time = time(hour=9, minute=0)
        cycle2 = Cycle(name="Lunch", user=self)
        cycle2.time = time(hour=12, minute=30)
        cycle3 = Cycle(name="Dinner", user=self)
        cycle3.time = time(hour=17, minute=30)
        cycle4 = Cycle(name="Night", user=self)
        cycle4.time = time(hour=20, minute=0)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_privileges(self):
        return self.update_privileges

    def check_medications(self):
        if self.is_patient():
            medications = Medicine.query.filter_by(user_id=self.id).all()
        else:
            medications = Medicine.query.join(
                patients, (patients.c.patient_id == Medicine.user_id)).filter(
                    patients.c.caretaker_id == self.id)
        return medications

    def med_authenticated(self, med_id):
        medication = Medicine.query.filter_by(id=med_id).first()
        if self.is_patient():
            return medication.user_id == self.id
        else:
            return medication.user.is_caretaker(self)

class Association(db.Model):
    __tablename__ = "association_table"

    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), primary_key=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycles.id'), primary_key=True)


class Medicine(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    dose = db.Column(db.Integer, index=True)
    pills = db.Column(db.Integer, index=True)
    period = db.Column(db.Float, index=True)
    taken = db.Column(db.Boolean, index=True, default=False)
    time_taken = db.Column(db.Time, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('medicines', lazy=True))

    cycles = db.relationship('Cycle',secondary='association_table', back_populates='medicines')

    def __repr__(self):
        return '{}'.format(self.name)

    def reset_taken(self):
        if self.taken == True:
            time_taken = datetime(2022, 1, 1, hour=self.time_taken.hour, minute=self.time_taken.minute, second=self.time_taken.second)
            time_taken = time_taken + timedelta(minutes = 10)
            time = time_taken.time()
            print(self.cycles)
            for cycle in self.cycles:
                if datetime.now().time() > cycle.time and cycle.time > (time):
                    self.taken = False

    def check_taken(self):
        self.reset_taken()
        if self.taken == False:
            for cycle in self.cycles:
                if datetime.now().time() > cycle.time:
                    return False
            return True
        return True

    def get_cycles(self):
        str = ""
        for i in range(len(self.cycles)-1):
            str += self.cycles[i].name + ", "
        if len(self.cycles) > 0:
            str += self.cycles[len(self.cycles)-1].name
        return str


class Cycle(db.Model):
    __tablename__ = 'cycles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    time = db.Column(db.Time, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('cycles', lazy=True))

    medicines = db.relationship('Medicine',secondary='association_table', back_populates='cycles')

    def __repr__(self):
        return '<Cycle {} for {}>'.format(self.name, self.user)


    def get_medications(self):
        str = ""
        for i in range(len(self.medicines)-1):
            str += self.medicines[i].__repr__() + ", "
        if len(self.medicines) > 0:
            str += self.medicines[len(self.medicines)-1].__repr__()
        return str

    def get_time(self):
        return self.time.strftime("%I:%M%p")


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

db.create_all()
db.session.commit()
