from application import db

class Userstore (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True)
    password = db.Column(db.String(8))
    user_created=db.Column(db.DateTime,nullable=False)

class Patient(db.Model):
    patient_id =db. Column(db.BigInteger,primary_key=True)
    ssn=db.Column(db.Integer,unique=True)
    patient_name=db.Column(db.String(50))
    address=db.Column(db.String(500))
    age=db.Column(db.Integer)
    date_of_joining=db.Column(db.Date,nullable=False)
    room_type=db.Column(db.String(50))
    status=db.Column(db.String(50),default='active')
    state=db.Column(db.String(50))
    city=db.Column(db.String(50))

class Medicine_store(db.Model):
    # medicine_id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(100), primary_key=True)
    quantity = db.Column(db.Integer)
    rate = db.Column(db.Integer)

class Medicine(db.Model):
    m_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.BigInteger,db.ForeignKey(Patient.patient_id,ondelete='CASCADE'))
    medicine_name = db.Column(db.String(100),db.ForeignKey(Medicine_store.medicine_name,ondelete='CASCADE'))
    quantity = db.Column(db.Integer)
    # patient_id = db.Column(db.BigInteger,db.ForeignKey(Patient.patient_id,ondelete='CASCADE'))
    # # medicine_name = db.Column(db.String(100))
    # rate = db.Column(db.Integer)

class DiagnosisStore(db.Model):
    test_id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), unique=True)
    charge = db.Column(db.Integer)

class Diagnostic(db.Model):
    sl_no = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.BigInteger,db.ForeignKey(Patient.patient_id,ondelete='CASCADE'))
    test_id = db.Column(db.Integer, db.ForeignKey(DiagnosisStore.test_id, ondelete='CASCADE'))
    test_name = db.Column(db.String(100),db.ForeignKey(DiagnosisStore.test_name, ondelete='CASCADE'))


