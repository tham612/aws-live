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


# @app.route("/addemp", methods=['POST'])
# def AddEmp():
#     emp_id = request.form['emp_id']
#     first_name = request.form['first_name']
#     last_name = request.form['last_name']
#     pri_skill = request.form['pri_skill']
#     location = request.form['location']
#     emp_image_file = request.files['emp_image_file']

#     insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
#     cursor = db_conn.cursor()

#     if emp_image_file.filename == "":
#         return "Please select a file"

#     try:

#         cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
#         db_conn.commit()
#         emp_name = "" + first_name + " " + last_name
#         # Uplaod image file in S3 #
#         emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
#         s3 = boto3.resource('s3')

#         try:
#             print("Data inserted in MySQL RDS... uploading image to S3...")
#             s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
#             bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
#             s3_location = (bucket_location['LocationConstraint'])

#             if s3_location is None:
#                 s3_location = ''
#             else:
#                 s3_location = '-' + s3_location

#             object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
#                 s3_location,
#                 custombucket,
#                 emp_image_file_name_in_s3)

#         except Exception as e:
#             return str(e)

#     finally:
#         cursor.close()

#     print("all modification done...")
#     return render_template('AddEmpOutput.html', name=emp_name)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=80, debug=True)

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
            s3.Bucket(custombucket).put_object_acl(ACL='private'|'public-read', Key=emp_image_file_name_in_s3, Body=emp_image_file)
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
                s3.Bucket(custombucket).put_object_acl(ACL='private'|'public-read', Key=emp_image_file_name_in_s3, Body=emp_image_file)
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






























if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
# =======================================================================================

#time and attendance

#view time
@app.route('/viewtime')
def UserAdmin():
    cur = db_conn.cursor()
    result = cur.execute("SELECT * FROM worktime")
    employee = cur.fetchall()
    return render_template('ViewTime.html', employee=employee)

#add time
@app.route("/addtime", methods=['POST'])
def AddTime():
    emp_id = request.form['emp_id']
    working_date = request.form['work_date']
    time_in = request.form['time_in']
    time_out = request.form['time_out']

    insert_sql = "INSERT INTO worktime VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, working_date, time_in, time_out))
        db_conn.commit()

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddTimeOutput.html', id=emp_id, date=working_date, start=time_in, end=time_out)

#get time
@app.route("/gettime", methods=['GET', 'POST'])
def GetEmp():
    return render_template('ViewTime.html')

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
        print("===================================================")
        print("========== in db =============")
        print(myresult)
        print("===================================================")

        start_time = myresult[0]
        end_time = myresult[1]
        work_date = myresult[2]
        emp_id = myresult[3]
        
    finally:
        # close the database after use the database
        cursor.close()

    # some text display, but not in html page
    print("all modification done...")

    return render_template('GetEmpOutput.html', id=emp_id, stime=start_time, etime=end_time, wdate=work_date) #image_url


 
#update time
@app.route('/updatetime', methods=['POST'])
def UpdateTime():
        pk = request.form['pk']
        name = request.form['name']
        value = request.form['value']
        cur = db_conn.cursor()

        if name == 'employeeid':
           cur.execute("UPDATE worktime SET employeeid = %s WHERE id = %s ", (value, pk))
        elif name == 'date':
           cur.execute("UPDATE worktime SET work_date = %s WHERE id = %s ", (value, pk))
        elif name == 'start_time':
           cur.execute("UPDATE worktime SET start_time = %s WHERE id = %s ", (value, pk))
        elif name == 'end_time':
           cur.execute("UPDATE worktime SET end_time = %s WHERE id = %s ", (value, pk))
        
        mysql.connection.commit()
        cur.close()
        return json.dumps({'status':'OK'})




































