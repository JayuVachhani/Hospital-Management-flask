import json
import locale
from datetime import datetime
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_,func
from sqlalchemy.sql import label
from config import Config

locale.setlocale(locale.LC_MONETARY, 'en_IN')

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
from models import User, Patient,MedicineDetails,PatientMedicine,TestDetails,PatientTest

migrate = Migrate(app, db)


@app.template_filter()
def currencyFormat(value):
    symbol=locale.localeconv()['currency_symbol']
    ans=((locale.currency(int(value),grouping=True))).replace(symbol,'')
    return ans
    

def calcBills(patientObj):
    # calculate admitdate and dischargedate(currentdate) difference
    bedtotal=0
    days=(datetime.now().date()-patientObj.admitdate).days
    if patientObj.bedtype.lower()=="general":
        bedtotal=days*2000
    elif patientObj.bedtype.lower()=="semi sharing":
        bedtotal=days*4000
    elif patientObj.bedtype.lower()=="single":
        bedtotal=days*8000
    return {"bedtotal":bedtotal,"days":days}
    

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                user.logged_in = datetime.now()
                db.session.commit()
                session['username'] = user.username
                session['role'] = user.role
                if session['role'] == 'admin':
                    return redirect('/admin')
                if session['role'] == 'pharmacist':
                    return redirect('/pharmacist')
                if session['role'] == 'diagnostic':
                    return redirect('/diagnostic')
                return redirect(url_for('login'))
            else:
                flash('Username and password combination does not match', 'danger')
    else:
        if request.method == 'GET':
            if session.get('role') == 'admin':
                return redirect('/admin')
            elif session.get('role') == 'pharmacist':
                return redirect('/pharmacist')
            elif session.get('role') == 'diagnostic':
                return redirect('/diagnostic')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if username and password and role:
            user = User.query.filter_by(username=username).first()
            if user is None:
                user = User(username=username, role=role)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('You have successfully registered! You may now login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('User already exists', 'danger')
    else:
        if session.get('username'):
            return redirect(url_for('login'))
    return render_template('register.html')


# ==========Admin=========================
@app.route('/admin')
def layout():
    return render_template('admin/home.html')


@app.route('/admin/home')
def adminHome():
    if session.get('role') == 'admin':
        return render_template('admin/home.html')
    else:
        return redirect(url_for('login'))





@app.route('/admin/create_patient', methods=['POST', 'GET'])
def create_patient():
    p_message = "Patient Created successfully!"
    if session.get('username') and session.get('role') == 'admin':
        with open('static/state_city.json') as datafile:
            data = json.load(datafile)
        if request.method == 'POST':
            ssnid = request.form['ssnid']
            pname = request.form['pname']
            age = request.form['age']
            address = request.form['address']
            skey = int(request.form['state'])
            ckey = int(request.form['city'])
            state = data['states'][skey]['state']
            city = data['states'][skey]['city'][ckey]
            bedtype = request.form['bedtype']
            admitdate = request.form['admitdate']
            if ssnid and pname and age and address and state and city and bedtype and admitdate:
                patient = Patient.query.filter_by(ssnid=ssnid).first()
                if patient is None:
                    patient = Patient(ssnid=ssnid, pname=pname, age=age, address=address, state=state, city=city,
                                      bedtype=bedtype, admitdate=admitdate)
                    db.session.add(patient)
                    db.session.commit()
                    flash(p_message, "success")
                else:
                    flash("Patient with SSN ID : " + ssnid +" already exists!", "warning")
                return render_template('admin/create_patient.html', data=data,today=datetime.now().date())
        elif request.method == 'GET':
            return render_template('admin/create_patient.html', data=data,today=datetime.now().date())
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))


@app.route('/admin/all_active_patients', methods=['GET', 'POST'])
def all_active_patients():
    if session.get('username') and session.get('role') == 'admin':
        if request.method == 'GET':
            all_active_patients_list = Patient.query.filter_by(pstatus='active').all()
            if all_active_patients_list:
                return render_template('admin/all_active_patients.html', data=all_active_patients_list)
            else:
                flash("There is No Active Patients.", 'danger')
                return render_template('admin/home.html')
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))


@app.route('/admin/search_patients', methods=['GET', 'POST'])
def search_patients():
    if session.get('username'):
        if request.method == 'POST':
            if ('ssnid' in request.form):
                id = request.form['ssnid']
                patient_all = Patient.query.filter_by(ssnid=id).first()
                patient_active=Patient.query.filter_by(ssnid=id,pstatus='active').first()
            elif ('pid' in request.form):
                id = request.form['pid']
                patient_all = Patient.query.filter_by(pid=id).first()
                patient_active=Patient.query.filter_by(pid=id,pstatus='active').first()
            # Here patient_all means irrescpective of its status(1 result)
            if patient_all != None and session.get('role') == 'admin':
                flash("Patient Found!","success")
                return render_template('search.html', data_all=patient_all)
          
            elif patient_active != None and (session.get('role') == 'pharmacist' or session.get('role') == 'diagnostic'):
                flash("Patient Found!","success")
                return render_template('search.html', data_active=patient_active)
            else:
                flash('No patient with ID : ' + id + " found in the records!","danger")
        return render_template('search.html')
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))


@app.route('/admin/billings',methods=['GET', 'POST'])
def patient_billings():
    if session.get('username') and session.get('role') == 'admin':
        if request.method == 'POST':
            id = request.form['pid']
            patient = Patient.query.filter_by(pid=id).first()
            beddata=calcBills(patient)
            medissued=PatientMedicine.query.filter_by(pid=id).all()
            testissued=PatientTest.query.filter_by(pid=id).all()
            medtotal=testtotal=0
            if medissued:
                medsum=db.session.query(PatientMedicine,label('medtotal', func.sum(PatientMedicine.amount))).filter_by(pid=id).first()
                medtotal=medsum.medtotal
            if testissued:
                testsum=db.session.query(PatientTest,label('testtotal', func.sum(PatientTest.charge))).filter_by(pid=id).first()
                testtotal=testsum.testtotal

            testissued=PatientTest.query.filter_by(pid=id).all()
            # billdata=calcBills(patient,medissued,testissued)
            grandtotal=beddata['bedtotal']+medtotal+testtotal
            total=[beddata,medtotal,testtotal,grandtotal]
            if request.form['submit']=='confirm_bills':
                patient.pstatus='discharged'
                db.session.commit()
                flash("Patient discharged succesfully!","success")
                return redirect(url_for("search_patients"))
            return render_template("admin/bills.html",patient_data=patient,medicine_data=medissued,
            test_data=testissued,bill_total=total,today=datetime.now().date())
        return redirect(url_for("search_patients"))
    else:
        flash("Login first as a Desk Executive", "danger")
    return redirect(url_for('login'))
        
            




@app.route('/admin/update', methods=['GET', 'POST'])
def update():
    if session.get('username') and session.get('role') == 'admin':
        with open('static/state_city.json') as datafile:
            dfile = json.load(datafile)
        if request.method == 'POST':
            id = request.form['pid']
            patient = Patient.query.filter_by(pid=id).first()
            
            if request.form['submit']=='update_patient':
                return render_template('admin/update_patient.html',data=patient, 
                statecity=dfile,today=datetime.now().date())
            if request.form['submit']=='confirmupdate':
                pname = request.form['pname']
                age = request.form['age']
                admitdate = request.form['admitdate']
                bedtype = request.form['bedtype']
                address = request.form['address']
                state = None
                city = None
                
                if request.form['state'] is not '':
                    skey = int(request.form['state'])
                    state = dfile['states'][skey]['state']
                    if request.form['city'] is not '':
                        ckey = int(request.form['city'])
                        city = dfile['states'][skey]['city'][ckey]
                if pname:
                    patient.pname = pname
                if age:
                    patient.age = age
                if admitdate:
                    patient.admitdate = admitdate
                if bedtype:
                    patient.bedtype = bedtype
                if address:
                    patient.address = address
                if state:
                    patient.state = state
                if city:
                    patient.city = city
                if pname or age or address or admitdate or bedtype or state or city: 
                    result = db.session.commit()
                    flash("Patient Updated Successfully", "success")
                    return redirect(url_for('all_active_patients'))
                else:
                    flash("No Changes were made", "warning")
        return render_template("search.html")
    else:
        flash("Login first as a Desk Executive", "danger")
    return redirect(url_for('login'))


@app.route('/admin/delete', methods=['GET', 'POST'])
def delete():
    if session.get('username') and session.get('role') == 'admin':
        if request.method == 'POST':
            pid = request.form['pid']
            patient = Patient.query.filter_by(pid=pid).first()
            db.session.delete(patient)
            db.session.commit()
            flash(
                "Patient: ID-{} | Name-{} , deleted succefully!".format(patient.pid, patient.pname),"success")

        return redirect(url_for('search_patients'))
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))

    # ========Pharmacist============

@app.route('/pharmacist')
def pharmalayout():
    return render_template('pharmacist/home.html')
@app.route('/pharmacist/home')
def pharmacistHome():
    if session.get('role') == 'pharmacist':
        return render_template('layout.html')
    else:
        return redirect(url_for('login'))




@app.route('/pharmacist/resupply', methods=['GET', 'POST'])
def resupply_medicines():
    if session.get('role') == 'pharmacist':
        if request.method == 'POST':
            if request.form['submit'] == 'add':
               
                medid = request.form['addmedid']
                medname = request.form['addmedname']
                medicine = MedicineDetails.query.filter(
                    or_(MedicineDetails.medid == medid, MedicineDetails.medname.like(medname))).all()
                
                quantity = request.form['addquantity']
                rate = request.form['addrate']
                
                if not medicine:
                    medicine = MedicineDetails(
                        medid=medid, medname=medname, quantity=quantity, rate=rate)
                    db.session.add(medicine)
                    db.session.commit()
                    flash("New Medicine added succefully!", "success")
                else:
                    flash("Medicine with Id : {} or Name: {} ,already exist, use update quantity to resupply!".format(
                        medid,medname),"warning")
            elif request.form['submit']=='update':
                medid=request.form['updatemedid']
                quantity=int(request.form['updatequantity'])
                
                medicine=MedicineDetails.query.filter_by(medid=medid).first()
                medicine.quantity+=quantity
                db.session.commit()
                flash("Medicine Id : {},Quantity updated to : {}".format(
                    medid, medicine.quantity), "success")
        medicine = MedicineDetails.query.filter().all()
        return render_template('pharmacist/resupply.html', med_data=medicine)
    else:
        return redirect(url_for('login'))

@app.route('/pharmacist/search_patients',methods=['GET','POST'])
def pharma_search_patients():
    if session.get('role')=='pharmacist':
        return search_patients()
    else:
        return redirect(url_for('login'))

@app.route('/pharmacist/issuemedicine', methods=['GET', 'POST'])
def issuemed_search():
    if session.get('role')=='pharmacist':
        
        if request.method=='POST':
            pid=request.form['pid']
            patient=Patient.query.filter_by(pid=pid).first()
            if request.form['submit']=='issuemed_add':
                medname=request.form['medname']
                quantity=int(request.form['quantity'])
                medfind=MedicineDetails.query.filter_by(
                    medname=medname).first()
                
                if(medfind is not None and quantity<=medfind.quantity):
                    patientmedfind=PatientMedicine.query.filter_by(pid=pid,
                        medname=medname).first()
                    if(patientmedfind is None):
                        patientmedicine = PatientMedicine(
                            pid=pid, medid=medfind.medid, medname=medfind.medname, quantity=quantity, rate=medfind.rate)
                        db.session.add(patientmedicine)
                    else:
                        patientmedfind.quantity += quantity
                    db.session.commit()
                    medfind.quantity -= quantity
                    db.session.commit()
                    flash("Medicine issued Succefully!", "success")
                else:
                    flash(
                        "Either Medicine name or invalid Quantity is entered. Refer medecine available table!", "danger")
            medicine = MedicineDetails.query.filter().all()
            med_issued = PatientMedicine.query.filter_by(
                pid=pid).all()
            return render_template('pharmacist/issuemedicine.html', data_medissue=med_issued, data_allmed=medicine, patient_data=patient)
        return redirect(url_for('pharma_search_patients'))
    else:
        return redirect(url_for('login'))


# ========Diagnostic============
@app.route('/diagnostic')
def dialayout():
    return render_template('diagnostic/home.html')


@app.route('/diagnostic/home')
def diagnosticHome():
    if request.method == 'GET' and session.get('role') == 'diagnostic':
        return render_template('diagnostic/home.html')
    else:
        return redirect(url_for('login'))

@app.route('/diagnostic/search_patients',methods=['GET','POST'])
def diagnostic_search_patients():
    if session.get('role')=='diagnostic':
        return search_patients()
    else:
        return redirect(url_for('login'))

@app.route('/diagnostic/issuetest',methods=['GET','POST'])
def issuetest_search():
    if session.get('role')=='diagnostic':
        if request.method=='POST':
            pid=request.form['pid']
            patient=Patient.query.filter_by(pid=pid).first()
            if request.form['submit']=='issuetest_add':
                testname=request.form['testname']
                charge=request.form['charge']
                testfind=TestDetails.query.filter_by(testname=testname).first()
                
                if(testfind is not None):
                        patientTest=PatientTest(pid=pid,testid=testfind.testid,testname=testname,charge=charge)
                        db.session.add(patientTest)
                        db.session.commit()
                        flash("Test issued Succefully!","success")
                else:
                    flash("Invalid Diagnostic Test Chosen!","danger")
            test=TestDetails.query.filter().all()
            testDict={}
            for row in test:
                testDict[row.testname]=float(row.charge)
            test_issued=PatientTest.query.filter_by(pid=pid).all()
            return render_template('diagnostic/issuetest.html',data_testissue=test_issued,data_alltest=testDict,patient_data=patient)
        return redirect(url_for('pharma_search_patients'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)