from django.shortcuts import render,redirect
from django.template import RequestContext
from django.contrib import messages
# import pymysql
import sqlite3
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import time
import datetime
import smtplib
from email.message import EmailMessage
from django.views.decorators.cache import cache_control



def session_deco(fun):
    def logged_in(request, *args, **kwargs):
        if 'username' in request.session:
            print(request.session['username'])
            return fun(request, *args, **kwargs)
        else:
            return redirect('Login')
    return logged_in

def index(request):
    if request.method == 'GET':
       return render(request, 'healthcareapp/index.html', {})


def Login(request):
    if 'username' in request.session:
        return redirect('check_logged_in')
    if request.method == 'GET':
       return render(request, 'healthcareapp/Login.html', {})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def check_user_and_redirect(request):
    current_user_type = request.session['type'].lower()
    if current_user_type == "doctor":
        return redirect('doctor_home_page')
    elif current_user_type == 'patient':
        return redirect('patient_home_page')
    else:
        return redirect('medical_services_home_page')

def logout(request):
    try:
        if 'username' in request.session:
            del request.session['username']
            del request.session['type']
    except:
        pass
    return redirect('Login')

def Register(request):
    if request.method == 'GET':
       return render(request, 'healthcareapp/Register.html', {})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def SetReminder(request):
    print('came')
    if request.method == 'GET':
       return render(request, 'healthcareapp/SetReminder.html', {})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def ViewMedicineDetails(request):
    if request.method == 'GET':
       return render(request, 'healthcareapp/ViewMedicineDetails.html', {})

def ViewMap(request):
    if request.method == 'GET':
        lat = request.GET['lat']
        lon = request.GET['lon']
        html = ''
        html+='<input type=\"hidden\" name=\"t1\" id=\"t1\" value='+lat+'>'
        html+='<input type=\"hidden\" name=\"t2\" id=\"t2\" value='+lon+'>'
        context= {'data':html}
        return render(request, 'healthcareapp/ViewMap.html', context)

def ViewMedicineDetailsAction(request):
    if request.method == 'POST':
        name = str(request.POST.get('medicine_name', False))
        output = ''
        # con = sqlite3.connect("db.sqlite3")
        con = sqlite3.connect("db.sqlite3")
        with con:
            cur = con.cursor()
            cur.execute("select * FROM medicinedetails where medicine_name='"+name+"'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size=3 color=white>'+row[0]+'</font></td>'
                output+='<td><font size=3 color=white>'+row[1]+'</font></td>'
                output+='<td><font size=3 color=white>'+str(row[2])+'</font></td>'
                output+='<td><font size=3 color=white>'+str(row[3])+'</font></td>'
                output+='<td><font size=3 color=white>'+str(row[4])+'</font></td>'
                output+='<td><font size=3 color=white>'+str(row[5])+'</font></td>'
                output+='<td><font size=3 color=white>'+str(row[6])+'</font></td>'
                output+='<td><font size=3 color=white>'+str(row[7])+'</font></td>'
                output+='<td><a href=\'ViewMap?lat='+str(row[6])+"&lon="+str(row[7])+'\'><font size=3 color=white>Click Here</font></a></td></tr>'
        context= {'data':output}
        return render(request, 'healthcareapp/ViewMedicineDetailsPage.html', context)      
    

def ChatData(request):
    if request.method == 'GET':
        question = request.GET.get('mytext', False)
        sender = request.GET.get('sender', False)
        receiver = request.GET.get('receiver', False)
        return HttpResponse(question, content_type="text/plain")

# def Chat(request):
#     if request.method == 'GET':
#         sender = request.GET.get('sender', False)
#         receiver = request.GET.get('receiver', False)
#         html = ''
#         html+='<input type=\"text\" name=\"sender\" id=\"sender\" value='+sender+'>'
#         html+='<input type=\"text\" name=\"receiver\" id=\"receiver\" value='+receiver+'>'
#         context= {'data':html}
#         return render(request, 'healthcareapp/Chat.html', context)

def Chat(request, room_name):
    with open('patient.txt', 'r') as p:
        patient = p.readline()
    with open('doctor.txt', 'r') as d:
        doctor = d.readline()
    context = {'doctor': doctor, 'patient': patient, 'room_name': room_name}
    return render(request, 'healthcareapp/chat_real.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def ViewPatientRequest(request):
    if request.method == 'GET':
        con = sqlite3.connect("db.sqlite3")
        user=request.session["username"]
        with con:
            cur = con.cursor()
            cur.execute("select patient_name,doctor_name,query,prescription,prescribe_date FROM  prescription where doctor_name='"+user+"'")
            rows = cur.fetchall()
            
        context= {'rows':rows}
        print(context)
        print("hello")
        return render(request, 'healthcareapp/ViewPatientRequest.html', context)     

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def ViewReminder(request):
    if request.method == 'GET':
        user = ''
        output = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        con = sqlite3.connect("db.sqlite3")
        with con:
            cur = con.cursor()
            cur.execute("select * FROM reminder where patient_name='"+request.session['username']+"'")
            rows = cur.fetchall()
        context= {'row':list(rows)}
        print(context)
        return render(request, 'healthcareapp/ViewReminder.html', context)              

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def SetReminderAction(request):
    if request.method == 'POST':
        dd = time.strftime('%Y/%m/%d %H:%M:%S')
        details = request.POST.get('details', False)
        reminder_time = request.POST.get('time', False)
        date_ = request.POST.get('datefilter', False)
        email_ =request.POST.get('email_address', False)
        patinent_name = request.POST.get('patient_name', False)
        print(date_)
        print(details)
        print(reminder_time)
        tt = str(datetime.datetime.strptime(date_ + " " + reminder_time.split()[0], "%m/%d/%Y %H:%M").strftime("'%Y-%m-%d %H:%M'"))
        print(tt)
        # with open("session.txt", "r") as file:
        #     for line in file:
        #         user = line.strip('\n')
        db_connection = sqlite3.connect("db.sqlite3")
        # db_cursor = db_connection.cursor()
        student_sql_query = """INSERT INTO reminder(patient_name,reminder_details,reminder_time, email) 
            values(? ,?,?,?)
        """
        # student_sql_query+="VALUES('"+user+"','"+details+"','"+rt+"')"
        db_connection.execute(student_sql_query, (patinent_name, details, tt, email_))
        db_connection.commit()
        db_connection.close()
        # print(db_cursor.rowcount, "Record Inserted")
        context= {'data':'Reminder set successfully'}
        return redirect('SetReminderAction')    
    else:
        return redirect('ViewReminder')    
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def MedicineDetails(request):
    if request.method == 'GET':
       return render(request, 'healthcareapp/MedicineDetails.html', {})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def SendQuery(request):
    if request.method == 'GET':
        user = ''
        with open("doctor.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        strs = '<tr><td><b>Patient&nbsp;Name</b></td><td><input type=\"text\" name=\"t1\" size=\"30\" value='+user+' readonly/></td></tr>'
        strs+='<tr><td><b>Choose&nbsp;Doctor</b></td><td><select name="t2">'
        con = sqlite3.connect("db.sqlite3")
        with con:
            cur = con.cursor()
            cur.execute("select username FROM register where usertype='Doctor'")
            rows = cur.fetchall()
        context= {'data1':list(rows), 'user_name': user}
        return render(request, 'healthcareapp/SendQuery.html', context)        

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def SendQueryRequest(request):
    if request.method == 'POST':
        print('post')
        print(request.POST)
        dd = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        patient = str(request.POST.get('patient_name', False))
        doctor = str(request.POST.get('selected_doctor', False))
        query = str(request.POST.get('query_string', False))
        db_connection = sqlite3.connect("db.sqlite3")
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO prescription(patient_name,doctor_name,query,prescription,prescribe_date) "
        student_sql_query+="VALUES('"+patient+"','"+doctor+"','"+query+"','none','"+dd+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        context= {'data':'Query sent to doctor '+doctor}
        return render(request, 'healthcareapp/SendQuery.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def ViewPrescription(request):
    if request.method == 'GET':
        user = ''
        output = ''
        doctor = ''
        with open("patient.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        with open("doctor.txt", "r") as file:
            for line in file:
                doctor = line.strip('\n')         
        con = sqlite3.connect("db.sqlite3")
        with con:
            cur = con.cursor()
            cur.execute("select * FROM prescription where patient_name='"+user+"'")
            rows = cur.fetchall()
        context= {'rows':list(rows),}
        
        return render(request, 'healthcareapp/ViewPrescription.html', context= context)            
    

def Signup(request):
    if 'username' not in request.session:
        if request.method == 'POST':
            fname = request.POST.get('fname', False)
            lname = request.POST.get('lname', False)
            username = request.POST.get('username', False)
            password = request.POST.get('password', False)
            contact = request.POST.get('contact', False)
            email = request.POST.get('email', False)
            address = request.POST.get('address', False)
            usertype = request.POST.get('type', False)
            db_connection = sqlite3.connect("db.sqlite3")
            index = 0
            with db_connection:
                cur = db_connection.cursor()
                cur.execute("select username FROM register")
                rows = cur.fetchall()
                for row in rows:
                    if row[0] == username:
                        index = 1
                        break
            if index == 0:
                db_cursor = db_connection.cursor()
                student_sql_query = "INSERT INTO register(username,password,contact,email,address,usertype) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"','"+usertype+"')"
                db_cursor.execute(student_sql_query)
                db_connection.commit()
                print(db_cursor.rowcount, "Record Inserted")
                context= {'data':'Signup Process Completed'}
                return render(request, 'healthcareapp/Register.html', context)
            else:
                context= {'data':username+' Username already exists'}
                return render(request, 'healthcareapp/Register.html', context)
    else:
        return redirect('check_logged_in')
    
def getEmail(user):
    email = ''
    con = sqlite3.connect("db.sqlite3")
    with con:
        cur = con.cursor()
        cur.execute("select * FROM register")
        rows = cur.fetchall()
        for row in rows:
            if row[0] == user:
                email = row[3]
                break
    return email            


def SendPrescription(request):
    if request.method == 'GET':
        patient = "Akhil"
        html = '<table align=center>'
        html+='<tr><td>Patient Name</td><td><input type=\"text\" name=\"t1\" value='+patient+' readonly></td></tr>'
        html+='<tr><td>Prescription</td><td><textarea name=\"t2\" id=\"t2\" rows="5" cols="60"></textarea></td></tr>'
        context= {'data1':html}
        return render(request, 'healthcareapp/Prescription.html', context)   


def sendEmail(emailid,msgs):
    msg = EmailMessage()
    msg.set_content(msgs)
    msg['Subject'] = 'Message From Online Digital Health System'
    msg['From'] = "kaleem202120@gmail.com"
    msg['To'] = emailid
    
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("kaleem202120@gmail.com", "offenburg")
    s.send_message(msg)
    s.quit()
    #text.insert(END,"Email Message Sent To Authorities")    

def PrescriptionAction(request):
    if request.method == 'POST':
        patient = request.POST.get('t1', False)
        prescription = request.POST.get('t2', False)
        # email = getEmail(patient)
        # sendEmail(email,prescription)
        db_connection = sqlite3.connect("db.sqlite3")
        db_cursor = db_connection.cursor()
        student_sql_query = "update prescription set prescription='"+prescription+"' where prescription='none' and patient_name='"+patient+"'";
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record updated")
        
        with open('doctor.txt', 'r') as d:
            doctor = d.readline()
        context= {'data':'Prescription sent to '+patient+'successfully!', 'doctor': doctor}
        return render(request, 'healthcareapp/Prescription.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def patient_logged_in(request):
    return render(request, 'healthcareapp/PatientScreen.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def doctor_logged_in(request):
    return render(request, 'healthcareapp/DoctorScreen.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def medical_services_logged_in(request):
    return render(request, 'healthcareapp/MedicalScreen.html')



def UserLogin(request):
    if 'username' not in request.session:
        if request.method == 'POST':
            username = request.POST.get('username', False)
            password = request.POST.get('password', False)
            usertype = request.POST.get('type', False)
            print(usertype)
            utype = 'none'
            con = sqlite3.connect("db.sqlite3")
            with con:
                cur = con.cursor()
                cur.execute("select * FROM register")
                rows = cur.fetchall()
                for row in rows:
                    if row[0] == username and row[1] == password and row[5] == usertype:
                        utype = 'success'
                        break

            if utype == 'success' and usertype == 'Doctor':
                file = open('session.txt','w')
                file.write(username)
                file.close()
                file = open('doctor.txt','w')
                file.write(username)
                file.close()
                request.usertype = 'doctor'
                context= {'data':'welcome '+username}
                request.session['username'] = username
                request.session['type'] = usertype
                return redirect('check_logged_in')

            elif utype == 'success' and usertype == 'Patient':
                file = open('session.txt','w')
                file.write(username)
                file.close()
                file = open('patient.txt','w')
                file.write(username)
                file.close()
                request.session['username'] = username
                request.session['type'] = usertype
                context= {'data':'welcome '+username}
                print('inside patient')
                return redirect('check_logged_in')
            elif utype == 'success' and usertype == 'Medical Services':
                file = open('session.txt','w')
                file.write(username)
                file.close()
                request.session['username'] = username
                request.session['type'] = usertype
                context= {'data':'welcome '+username}
                return redirect('check_logged_in')
            if utype == 'none':
                context= {'data':'Invalid login details'}
                return redirect('check_logged_in')
        else:
            return render(request, 'healthcareapp/Login.html')
    else:
        return redirect('check_logged_in')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@session_deco
def AddMedicineDetails(request):
    if request.method == 'POST':
        name = request.POST.get('medicine_name', False)
        dosage = request.POST.get('recommended_dosage', False)
        formula = request.POST.get('medicine_formula', False)
        details = request.POST.get('medicine_details', False)
        sideeffects = request.POST.get('side_effects', False)
        address = request.POST.get('medical_address', False)
        latitude = request.POST.get('latitude', False)
        longitude = request.POST.get('longitude', False)
        db_connection = sqlite3.connect("db.sqlite3")
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO medicinedetails(medicine_name,dosage,formula,details,side_effects,address,latitude,longitude) "
        student_sql_query+="VALUES('"+name+"','"+dosage+"','"+formula+"','"+details+"','"+sideeffects+"','"+address+"','"+latitude+"','"+longitude+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        context= {'data':'Medicine details added'}
        return render(request, 'healthcareapp/MedicineDetails.html', context)
