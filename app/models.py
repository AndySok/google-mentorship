from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    update_privileges = db.Column(db.Boolean, index=True, default=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.fname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def create_cycles(self):
        cycle1 = Cycle(name="Cycle A", user=self)
        cycle2 = Cycle(name="Cycle B", user=self)
        cycle3 = Cycle(name="Cycle C", user=self)
        cycle4 = Cycle(name="Cycle D", user=self)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_privileges(self):
        return self.update_privileges

    def med_authenticated(self, med_id):
        medication = Medicine.query.filter_by(id=med_id).first()
        return medication.user_id == self.id

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

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('medicines', lazy=True))

    cycles = db.relationship('Cycle',secondary='association_table', back_populates='medicines')

    def __repr__(self):
        return '{}'.format(self.name)

    # def add_to_cycle(self, cycle_number):
    #     self.cycle = Cycle.query.filter_by(cycle=cycle_number, user_id=self.user_id).first()

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

    # def get_medications(self):
    #     medications = Medicine.query.filter_by(cycle_id=self.id).all()
    #     return medications

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

db.create_all()
db.session.commit()
