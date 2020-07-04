from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event,DDL
from sqlalchemy.sql import select
import json

class User(db.Model):
    __tablename__ = 'userstore'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(15))
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    logged_in = db.Column(db.TIMESTAMP, nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



event.listen(User.__table__,"after_create",
DDL(" ALTER TABLE %(table)s AUTO_INCREMENT = 100000001;")
)

#one
class Patient(db.Model):
    __tablename__ = 'patients'

    pid = db.Column(db.Integer, primary_key=True)
    ssnid = db.Column(db.Integer, index=True, unique=True)
    pname = db.Column(db.String(60), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(300), nullable=False)
    state = db.Column(db.String(60), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    bedtype = db.Column(db.String(15), nullable=False)
    pstatus = db.Column(db.String(10), nullable=False, default='active')
    patientmedicine=db.relationship('PatientMedicine', backref='patients', lazy='dynamic',cascade='all, delete-orphan')
    patienttest=db.relationship('PatientTest', backref='patients', lazy='dynamic',cascade='all, delete-orphan')
    admitdate = db.Column(db.Date, default=datetime.now())
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(), onupdate=datetime.now())

event.listen(Patient.__table__,
    "after_create",
    DDL("""
    ALTER TABLE %(table)s AUTO_INCREMENT = 100000001;
    """)
)

class MedicineDetails(db.Model):
    __tablename__ = 'medicine_details'

    medid = db.Column(db.Integer, primary_key=True)
    medname = db.Column(db.String(100), nullable=False,unique=True)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Numeric(10,4), nullable=False)
    patientmedicine=db.relationship('PatientMedicine', backref='medicine_details', uselist=False)
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(), onupdate=datetime.now())

#many
class PatientMedicine(db.Model):
    __tablename__ = 'patient_medicines'

    id = db.Column(db.Integer, primary_key=True)
    pid=db.Column(db.Integer, db.ForeignKey('patients.pid',ondelete='CASCADE'))
    medid = db.Column(db.Integer,db.ForeignKey('medicine_details.medid'))
    medname = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Numeric(10,4), nullable=False)
    amount=db.Column(db.Numeric(10,4), nullable=False,default=(rate*quantity),onupdate=(rate*quantity))
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(), onupdate=datetime.now())


event.listen(
    PatientMedicine.__table__,
    "after_create",
    DDL("""
    ALTER TABLE %(table)s AUTO_INCREMENT = 100000001;
    """)
)



# PatientTest have one to one relationship woth TestDetails
#Diagnostic Test Master Table
class TestDetails(db.Model):
    __tablename__ = 'test_details'

    testid = db.Column(db.Integer, primary_key=True)
    testname = db.Column(db.String(100), nullable=False,unique=True)
    charge = db.Column(db.Numeric(10,4), nullable=False)
    patienttest=db.relationship('PatientTest', backref='test_details', uselist=False)
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(), onupdate=datetime.now())

def seedData(*args, **kwargs):
    with open('static/MedicalTest.json') as datafile:
            data = json.load(datafile)
    for key,val in data.items():
        db.session.add(TestDetails(testname=key,charge=val))
        db.session.commit()

event.listen(TestDetails.__table__,"after_create",seedData)

        

# 1 patient can have many Tests (one to many)
class PatientTest(db.Model):
    __tablename__ = 'patient_tests'

    id = db.Column(db.Integer, primary_key=True)
    pid=db.Column(db.Integer, db.ForeignKey('patients.pid',ondelete='CASCADE'))
    testid = db.Column(db.Integer,db.ForeignKey('test_details.testid'))
    testname=db.Column(db.String(100))
    charge=db.Column(db.Numeric(10,4))
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(), onupdate=datetime.now())



db.create_all()
db.session.commit()