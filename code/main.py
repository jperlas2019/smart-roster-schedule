from nurse import Nurse
from patient import Patient

from flask import Flask, render_template, redirect, url_for, request, session
from datetime import datetime

import json
import mysql.connector
import os
import bcrypt

# test purpose
import webbrowser

app = Flask(__name__,
            static_url_path="",
            static_folder="./static",
            instance_relative_config=True)

app.config.update(
    TESTING=True,
    TEMPLATES_AUTO_RELOAD=True
)

app.secret_key = os.urandom(12).hex()

db = mysql.connector.connect(
    host="localhost",
    user="charge_nurse",
    passwd="Password",
    database="smartroster",
    auth_plugin="mysql_native_password"
)

cursor = db.cursor()

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

# Login and Mainpage


@app.route("/")
def home():
    if 'loggedin' in session:
        return render_template('mainPage.html', loggedin=session['loggedin'])
    return redirect(url_for('login'))


@app.route("/register", methods=['GET'])
def register():
    if 'loggedin' in session:
        return render_template('register.html', loggedin=session['loggedin'])
    return redirect(url_for('login'))


@app.route("/registerUser", methods=['POST'])
def register_user():
    if 'username' in request.form and 'first_name' in request.form \
            and 'last_name' in request.form and 'password' in request.form \
            and 'password_conf' in request.form:
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        password_conf = request.form['password_conf']

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Username already taken.'
        elif password != password_conf:
            msg = 'Passwords do not match.'
        else:
            encrypted_password = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt())
            cursor.execute(
                'INSERT INTO users (username, password, first_name, last_name) '
                'VALUES (%s, %s, %s, %s)', (username,
                                            encrypted_password, first_name, last_name)
            )
            db.commit()
            return render_template("mainPage.html", loggedin=session['loggedin'])
        return render_template('register.html', msg=msg, loggedin=session['loggedin'])


@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


@app.route('/loginUser', methods=['POST'])
def login_user():
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Backdoor sign in with charge_nurse
        if username == "charge_nurse" and password == "Password":
            session['loggedin'] = True
            session['id'] = "charge_nurse"
            session['username'] = username
            return render_template("mainPage.html", loggedin=session['loggedin'])

        else:
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', (username,)
            )

            account = cursor.fetchone()

            if account and bcrypt.checkpw(password.encode(), account[2].encode()):
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = username
                return render_template("mainPage.html", loggedin=session['loggedin'])
            else:
                return render_template("login.html", msg="Invalid Login")


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Records


@app.route("/nurseRecords", methods=["GET"])
def nurse_records():
    if 'loggedin' in session:
        # Grabs all nurses
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()
        return render_template(
            "./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list
        )
    return redirect(url_for('login'))


@app.route("/addNurseRecords", methods=["POST"])
def add_nurse_records():
    if 'nurse_name' in request.form and 'nurse_area' in request.form and 'nurse_rotation' in request.form and 'nurse_fte' in request.form and 'nurse_a_trained' in request.form and 'nurse_skill' in request.form and 'nurse_transfer' in request.form and 'nurse_adv_role' in request.form and 'nurse_restrictions' in request.form and 'nurse_iv' in request.form:
        nurse_name = request.form['nurse_name']
        nurse_area = request.form['nurse_area']
        nurse_rotation = request.form['nurse_rotation']
        nurse_fte = request.form['nurse_fte']
        nurse_a_trained = request.form['nurse_a_trained']
        nurse_skill = request.form['nurse_skill']
        nurse_transfer = request.form['nurse_transfer']
        nurse_adv_role = request.form['nurse_adv_role']
        nurse_restrictions = request.form['nurse_restrictions']
        nurse_iv = request.form['nurse_iv']

    query = "insert into smartroster.nurses( nurse_name, nurse_area, nurse_rotation, nurse_fte, nurse_a_trained, nurse_skill, nurse_transfer, nurse_adv_role, nurse_restrictions, nurse_iv) " \
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    arguments = (nurse_name, nurse_area, nurse_rotation, nurse_fte, nurse_a_trained,
                 nurse_skill, nurse_transfer, nurse_adv_role, nurse_restrictions, nurse_iv)

    try:
        cursor.execute(query, arguments)
        db.commit()

    except Exception as error:
        print(error)

    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()
    return render_template("./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list)



@app.route("/editNurseRecords", methods=["POST"])
def edit_nurse_records():
    if 'edit_nurse_id' in request.form and 'edit_nurse_name' in request.form and 'edit_nurse_area' in request.form and 'edit_nurse_rotation' in request.form and 'edit_nurse_fte' in request.form and 'edit_nurse_a_trained' in request.form \
         and 'edit_nurse_skill' in request.form and 'edit_nurse_transfer' in request.form and 'edit_nurse_adv_role' in request.form and 'edit_nurse_restrictions' in request.form and 'edit_nurse_iv' in request.form:
        nurse_id = request.form['edit_nurse_id']
        nurse_name = request.form['edit_nurse_name']
        nurse_area = request.form['edit_nurse_area']
        nurse_rotation = request.form['edit_nurse_rotation']
        nurse_fte = request.form['edit_nurse_fte']
        nurse_a_trained = request.form['edit_nurse_a_trained']
        nurse_skill = request.form['edit_nurse_skill']
        nurse_transfer = request.form['edit_nurse_transfer']
        nurse_adv_role = request.form['edit_nurse_adv_role']
        nurse_restrictions = request.form['edit_nurse_restrictions']
        nurse_iv = request.form['edit_nurse_iv']

    query = "UPDATE smartroster.nurses SET nurse_name = %s, nurse_area = %s, nurse_rotation = %s, nurse_fte = %s, nurse_a_trained = %s, " \
        " nurse_skill = %s, nurse_transfer = %s, nurse_adv_role = %s, nurse_restrictions = %s, nurse_iv = %s WHERE nurse_id = %s"

    arguments = (nurse_name, nurse_area, nurse_rotation, nurse_fte, nurse_a_trained,
                 nurse_skill, nurse_transfer, nurse_adv_role, nurse_restrictions, nurse_iv, nurse_id)

    try:
        cursor.execute(query, arguments)
        db.commit()

    except Exception as error:
        print(error)

    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()

    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()
    return render_template(
        "./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list
    )


@app.route("/deleteNurseRecords", methods=["POST"])
def delete_nurse_records():
    nurse_id = request.form['remove_nurse_id']

    query = "DELETE FROM smartroster.nurses WHERE nurse_id = %s" % (nurse_id)

    try:
        cursor.execute(query)
        db.commit()
    except Exception as error:
        print(error)

    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()
    return render_template("./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list)


@app.route("/patientRecords", methods=["GET"])
def patient_records():
    # Table variables
    patient_headers = ["Patient ID", "Name", "Bed", "Acuity Level",
                       "Date Admitted", "Date Discharged", "A-trained Req", "IV"]
    # Grabs all patients
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template(
        "./Records/patientRecord.html",
        loggedin=session['loggedin'],
        patientList=patient_list,
        patientHeaders=patient_headers
    )


@app.route("/addPatientRecords", methods=["POST"])
def add_patient_records():    
    #Checks for required fields
    if 'patient_name' in request.form and 'patient_bed' in request.form and 'patient_acuity' in request.form and 'patient_date_admitted' in request.form and 'patient_a_trained' in request.form and 'patient_transfer' in request.form:
        patient_name = request.form['patient_name']
        patient_bed = request.form['patient_bed']
        patient_acuity = request.form['patient_acuity']
        patient_date_admitted = request.form['patient_date_admitted']
        patient_a_trained = request.form['patient_a_trained']
        patient_transfer = request.form['patient_transfer']

    query = "insert into smartroster.patients( patient_name, patient_bed, patient_acuity, patient_date_admitted, patient_a_trained, patient_transfer)" \
        "VALUES (%s,%s,%s,%s,%s,%s)"
    arguments = (patient_name, patient_bed, patient_acuity,
                 patient_date_admitted, patient_a_trained, patient_transfer)
    
    try:
        cursor.execute(query, arguments)
        db.commit()
    except Exception as error:
        print(error)

    # Grabs all patients
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template("./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list)


@app.route("/editPatientRecords", methods=["POST"])
def edit_patient_records():
    #Grabs discharge data so it knows if the patient has been discharged
    patient_date_discharged = request.form['edit_patient_date_discharge']

    if patient_date_discharged == '':
        #update if not changing discharge
        if 'edit_patient_id' in request.form and 'edit_patient_name' in request.form and 'edit_patient_bed' in request.form and 'edit_patient_acuity' in request.form and 'edit_patient_date_admitted' in request.form and 'edit_patient_a_trained' in request.form and 'edit_patient_IV' in request.form:
            patientid = request.form['edit_patient_id']
            patient_name = request.form['edit_patient_name']
            patient_bed = request.form['edit_patient_bed']
            patient_acuity = request.form['edit_patient_acuity']
            patient_date_admitted = request.form['edit_patient_date_admitted']
            patient_a_trained = request.form['edit_patient_a_trained']
            patient_transfer = request.form['edit_patient_IV']

            query = "UPDATE smartroster.patients SET patient_name = %s, patient_bed = %s, patient_acuity = %s, patient_date_admitted = %s, patient_a_trained = %s, patient_transfer = %s" \
                "WHERE patientid = %s"
            arguments = (patient_name, patient_bed, patient_acuity, patient_date_admitted, patient_a_trained, patient_transfer, patientid)
    else:
            #update if changing discharge
        if 'edit_patient_id' in request.form and 'edit_patient_name' in request.form and 'edit_patient_bed' in request.form and 'edit_patient_acuity' in request.form and 'edit_patient_date_admitted' in request.form and 'edit_patient_date_discharge' in request.form and 'edit_patient_a_trained' in request.form and 'edit_patient_IV' in request.form:
            patientid = request.form['edit_patient_id']
            patient_name = request.form['edit_patient_name']
            patient_bed = request.form['edit_patient_bed']
            patient_acuity = request.form['edit_patient_acuity']
            patient_date_admitted = request.form['edit_patient_date_admitted']
            patient_date_discharged = request.form['edit_patient_date_discharge']
            patient_a_trained = request.form['edit_patient_a_trained']
            patient_transfer = request.form['edit_patient_IV']

            query = "UPDATE smartroster.patients SET patient_name = %s, patient_bed = %s, patient_acuity = %s, patient_date_admitted = %s, patient_date_discharged = %s, patient_a_trained = %s, patient_transfer = %s" \
                "WHERE patientid = %s"
            arguments = (patient_name, patient_bed, patient_acuity, patient_date_admitted, patient_date_discharged, patient_a_trained, patient_transfer, patientid)

    try:
        cursor.execute(query, arguments)
        db.commit()
    except Exception as error:
        print(error)

    # Grabs all patients
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template("./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list)


@app.route("/deletePatientRecords", methods=["POST"])
def delete_patient_records():
    #grabs patient id
    patient_id = request.form['remove_patient_id']

    query = "DELETE FROM smartroster.patients WHERE patientid = %s" % (patient_id)

    try:
        cursor.execute(query)
        db.commit()
    
    except Exception as error:
        print(error)

     # Grabs all patients

    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template("./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list)


@app.route("/patientRecordsSubmit", methods=['POST'])
def patient_records_submit():
    return

# Account


@app.route("/profile", methods=['GET'])
def profile():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE username = %s',
                       (session['username'],))
        account = cursor.fetchone()
        return render_template(
            './Account/profile.html', account=account, loggedin=session['loggedin']
        )
    return redirect(url_for('login'))


@app.route("/settings")
def settings():
    return render_template("./Account/settings.html", loggedin=session['loggedin'])


# Assignment Sheets


@app.route("/currentCAASheet")
def current_CAASheet():
    return render_template("./Assignment Sheets/cur_caaSheet.html", loggedin=session['loggedin'])


@app.route("/currentPNSheet")
def current_PNSheet():
    return render_template("./Assignment Sheets/cur_pnSheet.html", loggedin=session['loggedin'])


@app.route("/pastCAASheet")
def past_CAASheet():
    return render_template("./Assignment Sheets/past_caaSheet.html", loggedin=session['loggedin'])


@app.route("/pastPNSheet")
def past_PNSheet():
    return render_template("./Assignment Sheets/past_pnSheet.html", loggedin=session['loggedin'])


@app.route('/assign', methods=['GET'])
def assign_nurse_patient() -> dict:
    """ Assign nurses to patients"""

    cursor.execute("SELECT * FROM variables")
    variables = cursor.fetchall()

    assignments = {}

    # Create "pod" data structure that stores: num_patients, how many transfers, skill level counts, how many a-trained

    num_clinical_areas = 6 # variables[0]
    clinical_areas ={}

    for _ in range(num_clinical_areas):
        clinical_areas[chr(num_clinical_areas + 65)] = {"patients": 0,"transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0, "picc": 0}

    # pods = {
    #     "A": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
    #     "B": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
    #     "C": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
    #     "D": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
    #     "E": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
    #     "F": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0}
    # }

    cursor.execute("SELECT * FROM patients WHERE current=True")  # We can modularize this. This gets all patients.
    patient_list = cursor.fetchall()

    # ---------------
    # Maybe we can turn each nurse and patients into objects, then we can have a list of nurse objects and a list of patient objects?
    
    # Initialize patient and nurse lists
    patients = []
    nurses = []

    # append current Patient objects into patients list
    for row in patient_list:
        x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                         row[12], row[13], row[14])
        patients.append(x)
    print(patients)

    cursor.execute("SELECT * FROM nurses WHERE current=True")  # We can also modularize this.
    nurse_list = cursor.fetchall()

    # append current Patient objects into patients list
    for row in nurse_list:
        x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                         row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19])
        nurses.append(x)
    print(nurses)


    # filling in pod info
    for row in patient_list:
        clinical_areas[row[3]]["patients"] += 1  # row[2] points to the bed column in patient list
        # row[2][0] points to the first letter in bed column which is the pod.
        # pods[#][0] points to the num_patients of the pod object.

        clinical_areas[row[3]]["level"][row[5]] += 1  # Increment skill level counts
        if row[6]:
            clinical_areas[row[3]]["a-trained"] += 1  # Increment amount of a-trained in pod object if patient needs a-trained
        if row[7]:
            clinical_areas[row[3]]["transfers"] += 1  # Increment amount of transfers in pod object if patient needs transfer
        if row[8]:
            clinical_areas[row[3]]["picc"] += 1  # Increment amount of picc in pod object if patient needs picc

    print(clinical_areas)

    # hard match nurses with patients they've been with (regardless of pod)
    #   In the case of multiple previous patients:
    #       - check skill-level
    #       - check geography (if needed)

    # previous_patients = {
    #     "1": {name, timestamp of admission, timestamp of discharge},
    #     "69": {anothern ame, timestapm, timestamp}
    # }

    matched_patients = []

    for n in nurses:
        prev_p = n.get_previous_patients()
        for p in patients:
            if prev_p.get(p.get_id(), False):
                assignments[n.get_id()] = p.get_id()
                n.set_assigned(True)
                # matched_patients.append(p.get_id())


    # assess all previous patients and pair
        # check if same clinical area (try to assign all to same nurse)
        # check recency. Favour most recent
        # check skill level (favour highest skill level first. Reject if not enough)

    # for nurse in nurse_list:

    #     if (nurse[13][0] in patient_list) and (nurse[18] is not True): # check if the latest patient the nurse has been with exists in patient list, and check if the nurse is not assigned
    #         assignments[nurse[1] + nurse[2]] = nurse[13][0] # hard match nurse with the latest previous patient entry (assuming previous patients is stored as list)
    #         nurse[18] = True # mark them as assigned

    # A trained nurses go to "Rabbit Pod" as much as needed
    for ca in clinical_areas.keys():
        # allocate ceil(clinical_areas[ca]["a_trained"]/2) a_trained nurses

        # check skill level
        # assign

    for pod in pods:
        if pod has a_trained patient:
            num_a_trained = 8
            allocate 8/2 ceiling a trained 
            allocate nurses with a_Trained to this pod

    for nurse in nurse_list:
        if nurse[9]:
            nurse[3] = 'F'  # Sets nurse pod to MBC clinical area
            nurse[10] = True  # Marks the nurse as assigned

    # split the remaining nurses according to "pod's needs"
    #       - A-trained

    ##################### PSEUDO CODE #########################
    ## Adds nurse to pod with a_trained ##
    # for pod in pods:
    #   count = pod["a_trained"]
    #   for _ in range(count):
    #       for nurse in nurse_list:
    #           if nurse[10] == False and nurse[6] == True:
    #               nurse[3] = pod  # Sets nurse to pod
    #               nurse[10] = True
    ###########################################################

    #       - transfer available for patient who needs it

    ##################### PSEUDO CODE #########################
    ## Adds nurse to pod with transfer ##
    # for pod in pods:
    #   count = pod["transfers"]
    #   for _ in range(count):
    #       for nurse in nurse_list:
    #           if nurse[10] == False and nurse[7] == True:
    #               nurse[3] = pod  # Sets nurse to pod
    #               nurse[10] = True
    ###########################################################

    #       - number of patients in a pod
    #       - Ensure enough skill level per pod
    #       - ensure PICC match

    # Special Role Assignments (note: not assigned to a pod/patient)

    # Assign nurses to patients
    #       - 1:1 (we think) hard constraint
    #       - A-trained match
    #       - Transfer match
    #       - PICC match
    #       - sort by skill level and pair the lower skill-level nurses first

    # Match first valid pair
    # for i in patients.keys():
    #     for j in nurses.keys():
    #         if (nurses[j][2] < 1) and (patients[i][2] < 1):
    #             if nurses[j][1] >= patients[i][1]:
    #                 try:
    #                     assignments[nurses[j][0]] = patients[i][0]
    #                     nurses[j][2] += 1
    #                     patients[i][2] += 1
    #                 except IndexError:
    #                     assignments["null" + str(i)] = patients[i][0]

    try:
        response = app.response_class(
            status=200, response=json.dumps(assignments))
    except ValueError as error:
        response = app.response_class(status=400, response=str(error))

    return response


if __name__ == "__main__":
    # Testing
    webbrowser.open("http://localhost:5000/", new=1, autoraise=True)
    app.run()


# Patient #5
# - transfer - False
# - atrained - True
# - acuity - 3
# - picc - False
# - one-to-one - False
# - clinical area - C
# - twin - 'other person'

# nurses:
# - transfer - doesn't matter
# - atrained - True
# - skill level - 3 or more
# - num_patients - 0
# - clinical area (soft) - B (2)
# - prev_patients - #5, #6, #1 (1)

# iterate by patients
# 1st iteration (num_patients = 0)
#  select statement in current nurses
# 2nd iteration (num_patients = 1)
# 3rd iteration (num_patients = 2)