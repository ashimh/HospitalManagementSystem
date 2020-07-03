from flask import Flask, render_template, redirect, url_for, request, flash, g, session, json, jsonify
from application import app, db
from application.models import Userstore, Patient, Medicine_store, Medicine, DiagnosisStore, Diagnostic
from sqlalchemy import func
from datetime import datetime, date


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route("/")
def login():
    if request.method == 'Post':
        session.pop('user', None)
    return render_template("login.html")


@app.route('/dropsession') #drops the session(logout)
def dropsession():
    session.pop('user', None)
    return redirect(url_for('login'))


# USER LOGIN PAGE
@app.route('/login_action', methods=['Post'])
def login_action():
    username = request.form['username']
    password = request.form['password']
    user = Userstore.query.filter_by(
        username=username, password=password).first()
    #print(user)
    if user is None:
        flash('User does not exist', 'error')
        return redirect(url_for('login'))
    else:
        session['user'] = request.form['username']
        flash("you are successfuly logged in", 'success')
        return redirect(url_for('home'))
    return redirect(url_for('login'))


# HOME PAGE AFTER SUCCESSFULL LOGIN
@app.route("/home")
def home():
    if g.user:  # checking if user is signed in , if not signed in 'else block' will execute this applies for all the functions

        return render_template("create_patient.html")
    else:
        return redirect(url_for('login'))


# PATIENT REGISTRATION PAGE
@app.route("/createPatient")
def create_patient():
    if g.user:
        return render_template("create_patient.html")
    else:
        return redirect(url_for('login'))


@app.route('/create_patient_action', methods=['Post'])
def create_patient_action():
    if g.user:
        if request.method == "POST" and request.form['ssn'] != "":
            ssn = request.form['ssn']
            # creating 9digit patient id from ssn id on the go
            pid = ssn[2:4] + ssn[6:] + ssn[0:2] + ssn[4:6]
            patient_name = request.form['patient_name']
            age = request.form['age']
            admission_date = request.form['admission_date']
            bed_type = request.form['bed_type']
            address = request.form['address']
            state = request.form['state']
            city = request.form['city']
            # query data to check if exist the ssn id
            data = Patient.query.filter_by(ssn=ssn).first()
            if data is None:
                # If the ssn id is not present in db table below code will insert the data
                patient = Patient(patient_id=pid, ssn=ssn, patient_name=patient_name, address=address,
                                  age=age, date_of_joining=admission_date, room_type=bed_type, state=state, city=city)
                db.session.add(patient)  # function to insert into db
                db.session.commit()
                flash(
                    'Patient registered successfully. Note the patient ID: ' + pid, "success")
                return redirect(url_for('create_patient'))
            else:
                # if data is not none , user exists in db and it will not add the data and redirect to create patient page
                flash('Already reistered', "error")
                return redirect(url_for('create_patient'))
        flash('Unknown error occured', "error")
        return redirect(url_for('create_patient'))

    return redirect(url_for('login'))


# PATIENT UPDATION WORKS
@app.route("/updatePatientInput")
def update_patient_input():
    if g.user:
        return render_template("update_patient_input.html")
    else:
        return redirect(url_for('login'))


# below route will pull all the data from table and will show the data using jinja in update_patient.html file
@app.route("/updatePatient", methods=['POST', 'GET'])
def update_patient():
    if g.user:
        if request.method == 'GET':
            pid = request.args['patient_id']
            #query from database
            data = db.session.query(Patient.patient_id, Patient.patient_name, Patient.age, Patient.date_of_joining,
                                    Patient.room_type, Patient.address, Patient.state, Patient.city).filter_by(patient_id=pid).first()
            db.session.commit()
            #print(data)
            if data is not None:
                # passing the data to template using jinja2
                return render_template("update_patient.html", data=data)
            else:
                flash("Patient ID is not registered", "error")
                return redirect(url_for('update_patient_input'))
        return redirect(url_for('update_patient_input'))
    else:
        return redirect(url_for('login'))


# update action will take place in this url
@app.route("/update_action", methods=['POST', 'GET'])
def update_action():
    if g.user:
        if request.method == "POST":
            pid = request.form['id']
            name = request.form['patient_name']
            age = request.form['age']
            doj = request.form['doj']
            tob = request.form['tob']
            address = request.form['address']
            state = request.form['state']
            city = request.form['city']

            # query data based on the patient id from db
            update_data = Patient.query.filter_by(patient_id=pid).first()
            # this will update the data in database after commit
            update_data.patient_name = name
            update_data.age = age
            update_data.doj = doj
            update_data.room_type = tob
            update_data.address = address
            update_data.state = state
            update_data.city = city
            update_data.status = 'active'
            db.session.commit()
            flash("Patient ID : " + pid + " updated successfully", "success")
            return redirect(url_for('update_patient_input'))
    else:
        return redirect(url_for('login'))


# DELETE PATIENT WORKS
@app.route("/deletePatient")
def delete_patient():

    if g.user:

        d = ["", "", "", "", "", "", "", "", ""]
        return render_template("delete_patient.html", data=d)
    else:
        return redirect(url_for('login'))


# below route will pull all the data from table and will show the data using jinja in deleted_patient.html template
@app.route("/deleteAction", methods=['POST'])
def delete_action():
    if g.user:

        if request.method == 'POST':
            pid = request.form['pid']
            # pulls the data from database
            delete_pid = db.session.query(Patient.patient_id, Patient.patient_name, Patient.ssn, Patient.age, Patient.room_type,
                                          Patient.address, Patient.state, Patient.city, Patient.date_of_joining).filter_by(patient_id=pid).first()
            db.session.commit()
            #print(delete_pid)
            if delete_pid is None:
                # if the data does not exist in database it will show flash and redirect to previous page
                flash("Patient Id is incorrect", 'error')
                return redirect(url_for('delete_patient'))

            return render_template('/delete_patient.html', data=delete_pid)

        return redirect(url_for('delete_patient'))
    else:
        return redirect(url_for('login'))


# this will be called when user clicks delete button
@app.route("/deleted")
def deleted_action():
    if g.user:

        pid = request.args['id']
        # delete the data from database for the entered patient id
        delete_pid = db.session.query(
            Patient.patient_id).filter_by(patient_id=pid).delete()
        db.session.commit()
        #print(delete_pid)
        if delete_pid is None:
            flash("Patient Id is incorrect", 'error')

        flash('Patient ID:' + pid + ' deleted Successfully', "success")
        return redirect(url_for('delete_patient'))
    else:
        return redirect(url_for('login'))


# This route will pull and show all the active patient details in bootstrap table using jinja in view_patient.html
@app.route("/viewPatient")
def view_patient():
    if g.user:
        # it will retrieve all the active patients from database
        get_details = db.session.query(Patient.patient_id, Patient.patient_name, Patient.age,
                                       Patient.address, Patient.date_of_joining, Patient.room_type).filter_by(status="active").all()
        db.session.commit()
        #print(get_details)
        if get_details is not None and len(get_details) > 0:
            return render_template("view_patient.html", data=get_details)
        else:
            flash('No patients registered yet', "error")
            return render_template("view_patient.html")
    else:
        return redirect(url_for('login'))


# THIS ROUTE WILL SEARCH A PATIENT BASED ON THE ENTERED PATIENT ID
@app.route("/searchPatient") #search input
def search_patient():
    if g.user:
        d = ["", "", "", "", "", "", "", "", ""]
        return render_template("search_patient.html", data=d)
    else:
        return redirect(url_for('login'))

#search action
@app.route("/searchAction", methods=['POST', 'GET'])
def search_action():
    if g.user:
        if request.method == 'POST':
            pid = request.form['pid']
            #search the details of patient
            search_pid = db.session.query(Patient.patient_id, Patient.patient_name, Patient.ssn, Patient.age, Patient.room_type,
                                          Patient.address, Patient.state, Patient.city, Patient.date_of_joining).filter_by(patient_id=pid).first()
            db.session.commit()
            #print(search_pid)
            if search_pid is None:
                flash('Patient ID does not exist', "error")

            return render_template("search_patient.html", data=search_pid)
        return render_template("search_patient.html")
    else:
        return redirect(url_for('login'))


#ISSUE MEDICINE DROPDOWN
@app.route("/issue_medicine_input")
def issue_medicine_input():
    if g.user:
        return render_template("issue_medicine_input.html")
    else:
        return redirect(url_for('login'))


@app.route("/issue_medicine_action", methods=['POST','GET'])
def issue_medicine_action():
    if g.user:
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            patient=Patient.query.filter_by(patient_id=patient_id).first()
            if not patient: #if No patient Exist
                flash("No patient Exist","error")
                return redirect(url_for('issue_medicine_input'))

            elif patient.status=='discharged':
                
                flash("No medicine issued because patient already discharged","error")
                return redirect(url_for('issue_medicine_input'))

            else:  #if patient Exist
                medicine_issued=Medicine.query.filter_by(patient_id=patient_id).all()

                if not medicine_issued: #if no medicine issued to the respected patient
                    temp_list=[]
                    #print(temp_list)
                    return render_template("view_issued_patient_details.html",patient=patient,temp_list = temp_list)
        
                else:  #if  medicine issued to the respected patient
                    med_details=[]
                    for item in medicine_issued:
                        medicine_details=Medicine_store.query.filter_by(medicine_name=item.medicine_name).first()               
                        med_details.append(medicine_details)
                    temp_list = zip(med_details,medicine_issued)
                    return render_template("view_issued_patient_details.html",patient=patient,temp_list = temp_list)
        else:
            flash("Something went wrong","error")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    
@app.route("/add_issue_medicine", methods=['POST','GET'])
def add_issue_medicine():
    if g.user:
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            patient=Patient.query.filter_by(patient_id=patient_id).first() 
            medicine_issued=Medicine.query.filter_by(patient_id=patient_id).all()

            if not medicine_issued:
                temp_list=[]
                return render_template("add_issue_medicine.html",patient=patient,temp_list = temp_list)
        
            else:
                med_details=[]
                for item in medicine_issued:
                    medicine_details=Medicine_store.query.filter_by(medicine_name=item.medicine_name).first()
                    med_details.append(medicine_details)

                temp_list = zip(med_details,medicine_issued)
                return render_template("add_issue_medicine.html",patient=patient,temp_list = temp_list)
        else:
            flash("Something went wrong","error")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

#add action
@app.route("/add_issue_medicine_action", methods=['POST','GET'])
def add_issue_medicine_action():
    if g.user:
        details = request.get_json()
        patient_id=details[0]
        for data in details[1:]:
            # print(data['medicine_name'])
            if data['medicine_name'] and data['quantity']:
                
                quantity=int(data['quantity'])
                #update stock of medicines
                medicine_store=Medicine_store.query.filter(func.lower(Medicine_store.medicine_name)==func.lower(data['medicine_name'])).first()               
                medicine_store.quantity=medicine_store.quantity-quantity
                db.session.commit()
                #update the issue medicine table
                med_iss=Medicine.query.filter(func.lower(Medicine.medicine_name)==func.lower(data['medicine_name']),Medicine.patient_id==patient_id).first() 
                if med_iss:
                    med_iss.quantity=med_iss.quantity+quantity
                    db.session.commit()
                else:
                    medicine_issued=Medicine(patient_id=patient_id,medicine_name=medicine_store.medicine_name,quantity=quantity)
                    db.session.add(medicine_issued)
                    db.session.commit()
        flash("Successfully added medicine to list", "success")
        return jsonify(success=True)
    else:
        return redirect(url_for('login'))    


#search medicine to calculate its rate and show them to user  
@app.route("/search_med", methods=['POST','GET'])
def search_med():
    if g.user:
        med_name = request.form['med_name']
        quantity = int(request.form['quantity'])
        med_details=Medicine_store.query.filter(func.lower(Medicine_store.medicine_name)==func.lower(med_name)).first()
        
        if  med_details is None:
            return jsonify(message="Medicine not found"),500
        else:
            if med_details.quantity < quantity:
                return  jsonify(message=f"only {med_details.quantity} available"),500
            else:
                return jsonify(rate=med_details.rate,amount=med_details.rate*quantity)
    else:
        return redirect(url_for('login')) 


#ISSUE DIAGNOSIS DROPDOWN WORKS
@app.route("/diagnosis_input")#this will be input page
def diagnosis_input():
    if g.user:
        return render_template('conduct_diagnosis_input.html')
    else:
        return redirect(url_for('login'))

#this will show all the coducted diagnosis to the patient
@app.route("/view_conducted_diagnosis", methods=['POST', 'GET'])
def view_diagnosis():
    if g.user:
        if request.method == 'POST':
            pid = request.form['pid']
            patient = Patient.query.filter_by(patient_id=pid).first()#pulls user details to show in table

            if not patient:  # if No patient Exist
                flash("No patient Exist", "error")
                return redirect(url_for('diagnosis_input'))
            else:
                diagnosis_conducted = Diagnostic.query.filter_by(
                    patient_id=pid).all()
                #print(diagnosis_conducted)
                if not diagnosis_conducted:  # if no diagnosis conducted to the respected patient
                    temp_list = []

                else:  # if  diagnosis conducted to the respected patient

                    diag_details = []
                    for item in diagnosis_conducted:
                        diagnosis_details = DiagnosisStore.query.filter_by(
                            test_name=item.test_name).first() #pulls the diagnosis details from store to add to patient id
                        diag_details.append(diagnosis_details)
                    temp_list = zip(diag_details, diagnosis_conducted)

                return render_template("view_conducted_diagnosis.html", patient=patient, temp_list=temp_list)
        else:
            flash("Something went wrong", "error")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

#adds new diagnosis to the list of patient
@app.route("/add_diagnosis_to_view", methods=['POST', 'GET'])
def add_diagnosis():
    if g.user:
        if request.method == 'POST':
            pid = request.form['pid']
            patient = Patient.query.filter_by(patient_id=pid).first() #pulls user details
            diag_store = DiagnosisStore.query.all() #pulls all test names to show in dropdown
            #print(diag_store)
            if diag_store is None:
                diag_store = [("test_name", "Nothing")]
            #print("testing")

            if not patient:  # if No patient Exist
                flash("No patient Exist", "error")
                return redirect(url_for('diagnosis_input'))
            else:
                diagnosis_conducted = Diagnostic.query.filter_by(
                    patient_id=pid).all() #pulls details of previously conducted tests

                if not diagnosis_conducted:  # if no diagnosis conducted to the respected patient
                    temp_list = []

                else:  # if  diagnosis conducted to the respected patient

                    diag_details = []
                    for item in diagnosis_conducted:
                        diagnosis_details = DiagnosisStore.query.filter_by(
                            test_name=item.test_name).first()
                        diag_details.append(diagnosis_details)
                    temp_list = zip(diag_details, diagnosis_conducted)

                return render_template("add_diagnosis_to_view.html", patient=patient, temp_list=temp_list, diag_store=diag_store)
        else:
            flash("Something went wrong", "error")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

#it is the post action which will update the details in database and client side
@app.route('/add_diagnosis_action1', methods=['POST', 'GET'])
def add_diagnosis_action1():
    if g.user:
        details = request.get_json()
        pid = str(details[0])
        b = 0
        for data in details[1:]:
            if data['diagnosis_name'] and data['amount']:
                diagnosis_name = str(data['diagnosis_name'])
                diag_store = DiagnosisStore.query.filter_by(
                    test_name=diagnosis_name).first()
                diag_issued = Diagnostic(
                    patient_id=pid, test_name=diag_store.test_name, test_id=diag_store.test_id)
                db.session.add(diag_issued)
                db.session.commit()
                b = 1
        if(b>0):
            flash("Successfully added diagnostic", "success")
            return jsonify(success=True)

    else:
        return redirect(url_for('login'))


#BILLING SECTION
@app.route("/patient_billing_input")
def patient_billing_input():
    if g.user:
        return render_template("patient_billing_input.html")
    else:
        return redirect(url_for('login'))


@app.route("/patient_billing_action", methods=['POST', 'GET'])
def patient_billing_action():
    if g.user:
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            patient = Patient.query.filter_by(patient_id=patient_id).first()
            if not patient:  # if No patient Exist
                flash("No patient Exist", "error")
                return redirect(url_for('patient_billing_input'))

            elif patient.status == 'discharged':

                flash("patient already discharged", "error")
                return redirect(url_for('patient_billing_input'))

            else:  # if patient Exist
                total_amount = {}
                date_of_joining = patient.date_of_joining
                room_type = patient.room_type
                no_of_days = (date.today() - date_of_joining).days
                total_amount['room_charge'] = 0

                if room_type == ' General ward':
                    total_amount["room_charge"] = 2000 * no_of_days
                elif room_type == 'Semi sharing':
                    total_amount["room_charge"] = 4000 * no_of_days
                else:
                    total_amount["room_charge"] = 8000 * no_of_days

                medicine_issued = Medicine.query.filter_by(
                    patient_id=patient_id).all()
                diagnosis_conducted = Diagnostic.query.filter_by(
                    patient_id=patient_id).all()

                # if no medicine issued  but diagnosis test are conducted to the respected patient
                if not medicine_issued and diagnosis_conducted:
                    temp_list = []
                    total_amount["medicine_charge"] = 0
                    total_amount["diag_charge"] = 0
                    diag_details = []
                    for diag in diagnosis_conducted:
                        diagnosis_details = DiagnosisStore.query.filter_by(
                            test_name=diag.test_name).first()
                        diag_details.append(diagnosis_details)
                        total_amount["diag_charge"] += diagnosis_details.charge
                    total_amount["grand_total"] = sum(total_amount.values())
                    diag_list = zip(diag_details, diagnosis_conducted)
                    return render_template("view_patient_billing.html", patient=patient, temp_list=temp_list, diag_list=diag_list, no_of_days=no_of_days, total_amount=total_amount)

                elif medicine_issued and not diagnosis_conducted:
                    diag_list = []
                    med_details = []
                    total_amount["medicine_charge"] = 0
                    total_amount["diag_charge"] = 0
                    for item in medicine_issued:
                        medicine_details = Medicine_store.query.filter_by(
                            medicine_name=item.medicine_name).first()
                        med_details.append(medicine_details)
                        total_amount["medicine_charge"] += medicine_details.rate * \
                            item.quantity
                    total_amount["grand_total"] = sum(total_amount.values())
                    temp_list = zip(med_details, medicine_issued)
                    return render_template("view_patient_billing.html", patient=patient, temp_list=temp_list, diag_list=diag_list, no_of_days=no_of_days, total_amount=total_amount)

                elif medicine_issued and diagnosis_conducted:
                    total_amount["diag_charge"] = 0
                    total_amount["medicine_charge"] = 0
                    diag_details = []
                    med_details = []

                    for item in medicine_issued:
                        medicine_details = Medicine_store.query.filter_by(
                            medicine_name=item.medicine_name).first()
                        med_details.append(medicine_details)
                        total_amount["medicine_charge"] += medicine_details.rate * \
                            item.quantity
                    temp_list = zip(med_details, medicine_issued)

                    for diag in diagnosis_conducted:
                        diagnosis_details = DiagnosisStore.query.filter_by(
                            test_name=diag.test_name).first()
                        diag_details.append(diagnosis_details)
                        total_amount["diag_charge"] += diagnosis_details.charge
                    diag_list = zip(diag_details, diagnosis_conducted)
                    total_amount["grand_total"] = sum(total_amount.values())
                    return render_template("view_patient_billing.html", patient=patient, temp_list=temp_list, diag_list=diag_list, no_of_days=no_of_days, total_amount=total_amount)

                else:
                    total_amount["diag_charge"] = 0
                    total_amount["medicine_charge"] = 0
                    total_amount["grand_total"] = sum(total_amount.values())

                    diag_list = []
                    temp_list = []
                    return render_template("view_patient_billing.html", patient=patient, temp_list=temp_list, diag_list=diag_list, no_of_days=no_of_days, total_amount=total_amount)

        else:
            flash("Something went wrong", "error")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route("/discharge_patient", methods=['POST', 'GET'])
def discharge_patient():
    if g.user:
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            patient = Patient.query.filter_by(patient_id=patient_id).first()
            patient.status = 'discharged'
            db.session.commit()
            flash(
                "Sucessfully Generated the Bill, And the patient is discharged", "success")
        return redirect(url_for('patient_billing_input'))


#VIEW ALL AVAILABLE MEDICINE LIST(EXTRA FEATURES)
@app.route('/view_medicines_list') #views all available medicine in medicine master
def med_view_list():
    if g.user:
        data = [["", "", ""], ["", "", ""], ["", "", ""]]
        data = Medicine_store.query.all()
        #print(data[0].medicine_name)
        return render_template('view_medicines_list.html', data=data)
    return redirect(url_for('login'))

#views all available diagnostics in diagnosis master
@app.route('/view_diagnostics_list') 
def diag_view_list():
    if g.user:
        data = [["", "", ""], ["", "", ""], ["", "", ""]]
        data = DiagnosisStore.query.all()

        return render_template('view_diagnostics_list.html', data=data)
    return redirect(url_for('login'))


#input add new test names to diagnosis master database
@app.route('/add_diagnostics_to_stock_input')
def add_stock_diagn():
    if g.user:
        return render_template('add_diagnostics_to_stock.html')
    return redirect(url_for('login'))


#add new test name action
@app.route('/added_diagnostic', methods=['POST'])
def added_stock_diagn():
    if g.user:
        test_name = request.form['test_name']
        charge = request.form['charge']

        d_name = DiagnosisStore.query.filter(func.lower(
            DiagnosisStore.test_name) == func.lower(test_name)).first()
        if not d_name:
            test = DiagnosisStore(test_name=test_name, charge=charge)
            db.session.add(test)
            db.session.commit()
            db.session.close()
            flash('Successfully added new test details to stock', 'success')
        else:
            flash('Diagnosis test is already present on stock', 'error')
        return redirect(url_for('add_stock_diagn'))

    return redirect(url_for('login'))


#input add new medicine names to medicine master database
@app.route('/add_medicine_to_stock_input')
def add_stock_med():
    if g.user:
        return render_template('add_medicine_to_stock.html')
    return redirect(url_for('login'))


#add new medicine name action
@app.route('/added_medicine', methods=['POST'])
def added_stock_med():
    if g.user:
        med_name = request.form['med_name']
        charge = request.form['charge']
        quantity = request.form['q']

        m_name = Medicine_store.query.filter(func.lower(
            Medicine_store.medicine_name) == func.lower(med_name)).first()
        if not m_name:  # add new medicine to stock if the medicine name does not exists in the database
            med = Medicine_store(medicine_name=med_name,
                                 quantity=quantity, rate=charge)
            db.session.add(med)
            db.session.commit()
            db.session.close()
            flash('Successfully added new Medicine details to stock', 'success')
        else:

            flash(med_name + 'is already available in database, please update the details in  update medicine section', 'error')
        return redirect(url_for('add_stock_med'))

    return redirect(url_for('login'))


# Update the diagnostic store list names
@app.route('/update_diag_list_input') #takes input of diagnosis name
def update_list_diag_input():
    if g.user:
        diagnosis_list = DiagnosisStore.query.all()
        return render_template("update_diag_list_input.html", diag_store=diagnosis_list)
    return redirect(url_for('login'))

#shows previous details of diagnosis in input
@app.route('/update_diag_list_view', methods=["POST", "GET"]) 
def update_list_diag_list_view():
    if g.user:
        t_name = request.args['t_name']

        diagnosis_list = db.session.query(
            DiagnosisStore.test_name, DiagnosisStore.charge).filter_by(test_name=t_name).first()
        #print(diagnosis_list)
        db.session.commit()
        return render_template("update_diag_list.html", diag_store=diagnosis_list)
    return redirect(url_for('login'))

#update action
@app.route('/update_diag_list_action', methods=["POST", "GET"])
def update_list_diag_action():
    if g.user:
        if request.method == "POST":
            name = request.form['t']
            t_name = request.form['t_name']
            charge = request.form['cost']
            #print(t_name)
            diagnosis_list = DiagnosisStore.query.filter_by(
                test_name=name).first()
            #print(diagnosis_list)
            diagnosis_list.test_name = t_name
            diagnosis_list.charge = charge
            db.session.commit()
            flash("Successfully updated", "success")
            return redirect(url_for('update_list_diag_input'))
        flash("Not updated", "error")
        return redirect(url_for('update_list_diag_input'))
    return redirect(url_for('login'))


# update the medicine store list names
@app.route('/update_med_list_input') #input of the medicine name
def update_list_med_input():
    if g.user:
        med_list = Medicine_store.query.all()
        return render_template("update_med_list_input.html", diag_store=med_list)
    return redirect(url_for('login'))

#shows previous details of medicine in input
@app.route('/update_med_list_view', methods=["POST", "GET"]) 
def update_list_med_list_view():
    if g.user:
        t_name = request.args['t_name']

        medicine_list = db.session.query(Medicine_store.medicine_name, Medicine_store.rate,
                                         Medicine_store.quantity).filter_by(medicine_name=t_name).first()
        #print(medicine_list)
        db.session.commit()
        return render_template("update_med_list.html", diag_store=medicine_list)
    return redirect(url_for('login'))

#update action
@app.route('/update_med_list_action', methods=["POST", "GET"])
def update_list_med_action():
    if g.user:
        if request.method == "POST":
            name = request.form['t']
            t_name = request.form['t_name']
            charge = request.form['cost']
            q = request.form['q']
            qu = request.form['qu']

            #print(t_name)
            diagnosis_list = Medicine_store.query.filter_by(
                medicine_name=name).first()
            #print(diagnosis_list)
            diagnosis_list.medicine_name = t_name
            diagnosis_list.rate = charge
            diagnosis_list.quantity += int(qu)
            db.session.commit()
            flash("Successfully updated", "success")
            return redirect(url_for('update_list_med_input'))
        flash("Not updated", "error")
        return redirect(url_for('update_list_med_input'))
    return redirect(url_for('login'))
