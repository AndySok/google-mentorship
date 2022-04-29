from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#users_medicine = db.Table("Medicine",
#    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id')))

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
        cycle1 = Cycle(cycle=1, user=self)
        cycle2 = Cycle(cycle=2, user=self)
        cycle3 = Cycle(cycle=3, user=self)
        cycle4 = Cycle(cycle=4, user=self)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_privileges(self):
        return self.update_privileges

    def check_medications(self):
        medications = Medicine.query.filter_by(user_id=self.id).all()
        return medications

    def get_cycle(self, n):
        cycle = Cycle.query.filter_by(user_id=self.id).all()[n-1]
        return cycle

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

    cycle_id = db.Column(db.Integer, db.ForeignKey('cycles.id'), nullable=True)
    cycle = db.relationship('Cycle',backref=db.backref('medicines', lazy=True))

    def __repr__(self):
        return '<Medicine {} for {}>'.format(self.name, self.cycle.user)

    def add_to_cycle(self, cycle_number):
        cycle = Cycle.query.filter_by(cycle=cycle_number, user_id=self.user_id).first()
        self.cycle = cycle
        self.cycle_id = cycle.id

class Cycle(db.Model):
    __tablename__ = 'cycles'

    id = db.Column(db.Integer, primary_key=True)
    cycle = db.Column(db.Integer, index=True)
    time = db.Column(db.Time, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('cycles', lazy=True))

    def __repr__(self):
        return '<Cycle {} for {}>'.format(self.cycle, self.user)

    def get_medications(self):
        medications = Medicine.query.filter_by(cycle_id=self.id).all()
        return medications

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
