from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#users_medicine = db.Table("Medicine",
#    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id')))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    emergency_contact = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    medicine = db.relationship("Medicine", backref='consumer', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Medicine(db.Model):
    __tablename__ = 'medicine'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    dose = db.Column(db.Integer, index=True)
    cycle = db.Column(db.Integer, index=True)
    period = db.Column(db.Float, index=True)
    amount = db.Column(db.Integer, index=True)
    taken = db.Column(db.Boolean, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
