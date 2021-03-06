from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/aboutus", methods=['GET', 'POST'])
def AboutUs():
    return render_template('AboutUs.html')

@app.route("/payrollP", methods=['GET', 'POST'])
def PayrollP():
    return render_template('AddPayroll.html')

@app.route("/attendanceempP", methods=['GET', 'POST'])
def AttendanceEmpP():
    return render_template('attendanceEmp.html')

@app.route("/addtimeP", methods=['GET', 'POST'])
def AddTimeP():
    return render_template('AddTime.html')

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template('GetEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


# =======================================================================================
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        print("===========================")
        print(emp_image_file.filename.split("."))
        print("===========================")
        # Uplaod image file in S3 #
        fileType = emp_image_file.filename.split(".")
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file." + fileType[1]
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(ACL='public-read-write', Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, object_url))
        cursor.execute("INSERT INTO attendance VALUES (%s, %s, %s, %s)", (0, emp_id, "", ""))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():

    emp_id = request.form['emp_id']

    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    adr = (emp_id, )

    try:
        cursor.execute(select_sql, adr) 

        # if SELECT:
        myresult = cursor.fetchone()
        print("===================================================")
        print("========== in db =============")
        print(myresult)
        print("===================================================")

        emp_id = myresult[0]
        first_name = myresult[1]
        last_name = myresult[2]
        pri_skill = myresult[3]
        location = myresult[4]
        image_url = myresult[5]
        
    finally:
        cursor.close()

    return render_template('GetEmpOutput.html', id=emp_id, fname=first_name, lname=last_name, interest=pri_skill, location=location, image_url=image_url)

@app.route("/fetchdataEdit", methods=['GET', 'POST'])
def FetchEmpEdit():

    emp_id = request.form['emp_id']

    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    adr = (emp_id, )

    try:
        cursor.execute(select_sql, adr) 

        # if SELECT:
        myresult = cursor.fetchone()

        emp_id = myresult[0]
        first_name = myresult[1]
        last_name = myresult[2]
        pri_skill = myresult[3]
        location = myresult[4]
        image_url = myresult[5]
        
    finally:
        cursor.close()

    return render_template('EditEmp.html', id=emp_id, fname=first_name, lname=last_name, interest=pri_skill, location=location, image_url=image_url)


@app.route("/editempE", methods=['GET', 'POST'])
def EditEmpFunc():

    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']
    emp_image_file_hide = request.form['emp_image_file_hide']

    update_sql = "UPDATE employee SET emp_id = %s, first_name = %s, last_name = %s, pri_skill = %s, location = %s, image_url = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:

        if emp_image_file.filename != "":
            print("===========================")
            print(emp_image_file.filename.split("."))
            print("===========================")
            # Uplaod image file in S3 #
            fileType = emp_image_file.filename.split(".")
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file." + fileType[1]
            s3 = boto3.resource('s3')

            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(ACL='public-read-write', Key=emp_image_file_name_in_s3, Body=emp_image_file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

            except Exception as e:
                return str(e)
        else:
           object_url = emp_image_file_hide

        cursor.execute(update_sql, (emp_id, first_name, last_name, pri_skill, location, object_url, emp_id))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        
    finally:
        cursor.close()

    return render_template('AddEmpOutput.html', name=emp_name)


# =======================================================================================

#add time
@app.route("/addtime", methods=['POST'])
def AddTime():
    emp_id = request.form['emp_id']
    working_day = request.form['work_day']
    time_in = request.form['time_in']
    time_out = request.form['time_out']

    insert_sql = "INSERT INTO worktime VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (0, emp_id, working_day, time_in, time_out))
        db_conn.commit()

    finally:
        cursor.close()

    timeS = emp_id + " " + working_day + " " + time_in + " " + time_out

    print("all modification done...")
    return render_template('AddTimeOutput.html', timeOut=timeS)


#Fetch time ok
@app.route("/fetchtime", methods=['GET', 'POST'])
def FetchTime():

    emp_id = request.form['emp_id']

    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM worktime WHERE emp_id = %s"
    adr = (emp_id, )

    try:
        cursor.execute(select_sql, adr) 

        # if SELECT:
        myresult = cursor.fetchone()

        emp_id = myresult[1]
        working_day = myresult[2]
        time_in = myresult[3]
        time_out = myresult[4]
        
    finally:
        # close the database after use the database
        cursor.close()

    # some text display, but not in html page
    print("all modification done...")

    return render_template('GetTimeOutput.html', id=emp_id, working_day=working_day, time_in=time_in, time_out=time_out)

# Fetch Time Edit
@app.route("/fetchdatatimeEdit", methods=['GET', 'POST'])
def FetchTimeEdit():

    emp_id = request.form['emp_id']

    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM worktime WHERE emp_id = %s"
    adr = (emp_id, )

    try:
        cursor.execute(select_sql, adr) 

        # if SELECT:
        myresult = cursor.fetchone()

        emp_id = myresult[1]
        working_day = myresult[2]
        time_in = myresult[3]
        time_out = myresult[4]
        
    finally:
        cursor.close()

    return render_template('EditTime.html', id=emp_id, working_day=working_day, time_in=time_in, time_out=time_out)



#edit time
@app.route("/edittimeE", methods=['POST'])
def EditTime():
    emp_id = request.form['emp_id']
    working_day = request.form['working_day']
    time_in = request.form['time_in']
    time_out = request.form['time_out']

    update_sql = "UPDATE worktime SET emp_id = %s, working_day = %s, time_in = %s, time_out = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (emp_id, working_day, time_in, time_out, emp_id))
        db_conn.commit()

    finally:
        cursor.close()

    timeS = emp_id + " " + working_day + " " + time_in + " " + time_out

    print("all modification done...")
    return render_template('AddTimeOutput.html', timeOut=timeS)

# =======================================================================================

# edit attendance - check in
@app.route("/check_in", methods=['POST'])
def CheckIn():
    emp_id = request.form['emp_id']

    update_sql = "UPDATE attendance SET check_in = current_timestamp() WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (emp_id))
        db_conn.commit()

    finally:
        cursor.close()

    checkinout = "Check In"
    empID = emp_id

    print("all modification done...")
    return render_template('attendanceOutput.html', checkinout=checkinout, empID=empID)

# edit attendance - check out
@app.route("/check_out", methods=['POST'])
def CheckOut():
    emp_id = request.form['emp_id']

    update_sql = "UPDATE attendance SET check_out = current_timestamp() WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (emp_id))
        db_conn.commit()

    finally:
        cursor.close()

    checkinout = "Check Out"
    empID = emp_id

    print("all modification done...")
    return render_template('attendanceOutput.html', checkinout=checkinout, empID=empID)


#Fetch Attendance ok
@app.route("/fetchattendance", methods=['GET', 'POST'])
def FetchAttendance():

    emp_id = request.form['emp_id']

    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM attendance WHERE emp_id = %s"
    adr = (emp_id, )

    try:
        cursor.execute(select_sql, adr) 

        # if SELECT:
        myresult = cursor.fetchone()

        emp_id = myresult[1]
        check_in = myresult[2]
        check_out = myresult[3]
        
    finally:
        # close the database after use the database
        cursor.close()

    # some text display, but not in html page
    print("all modification done...")

    return render_template('attendancePage.html', id=emp_id, check_in=check_in, check_out=check_out)

# =======================================================================================


#add payroll
@app.route("/addpayroll", methods=['POST'])
def AddPayroll():
    emp_id = request.form['emp_id']
    pay_hour = request.form['pay_hour']
    otpay_hour = request.form['otpay_hour']
    totalh_work = request.form['totalh_work']
    totalhot_work = request.form['totalhot_work']


    insert_sql = "INSERT INTO payroll VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (0, emp_id, pay_hour, otpay_hour, totalh_work, totalhot_work))
        db_conn.commit()

    finally:
        cursor.close()

    id = emp_id

    print("all modification done...")
    return render_template('AddPayrollOutput.html', id=id)


#Fetch payroll ok
@app.route("/fetchpayroll", methods=['GET', 'POST'])
def FetchPayroll():

    emp_id = request.form['emp_id']

    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM payroll WHERE emp_id = %s"
    adr = (emp_id, )

    try:
        cursor.execute(select_sql, adr) 

        # if SELECT:
        myresult = cursor.fetchone()

        emp_id = myresult[1]
        pay_hour = myresult[2]
        otpay_hour = myresult[3]
        totalh_work = myresult[4]
        totalhot_work = myresult[5]
        
    finally:
        # close the database after use the database
        cursor.close()

    # some text display, but not in html page
    print("all modification done...")

    return render_template('GetPayrollOutput.html', id=emp_id, pay_hour=pay_hour, otpay_hour=otpay_hour, totalh_work=totalh_work, totalhot_work=totalhot_work)

# Fetch payroll Edit
@app.route("/fetchdatapayrollEdit", methods=['GET', 'POST'])
def FetchPayrollEdit():

    emp_id = request.form['emp_id']

    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM payroll WHERE emp_id = %s"
    adr = (emp_id, )

    try:
        cursor.execute(select_sql, adr) 

        # if SELECT:
        myresult = cursor.fetchone()

        emp_id = myresult[1]
        pay_hour = myresult[2]
        otpay_hour = myresult[3]
        totalh_work = myresult[4]
        totalhot_work = myresult[5]
        
    finally:
        cursor.close()

    return render_template('EditPayroll.html', id=emp_id, pay_hour=pay_hour, otpay_hour=otpay_hour, totalh_work=totalh_work, totalhot_work=totalhot_work)



#edit payroll
@app.route("/editpayrollE", methods=['POST'])
def EditPayroll():
    emp_id = request.form['emp_id']
    pay_hour = request.form['pay_hour']
    otpay_hour = request.form['otpay_hour']
    totalh_work = request.form['totalh_work']
    totalhot_work = request.form['totalhot_work']

    update_sql = "UPDATE payroll SET emp_id = %s, pay_hour = %s, ot_hour = %s, total_hour_work = %s, total_ot_work = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (emp_id, pay_hour, otpay_hour, totalh_work, totalhot_work, emp_id))
        db_conn.commit()

    finally:
        cursor.close()

    id = emp_id

    print("all modification done...")
    return render_template('AddPayrollOutput.html', id=id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)































