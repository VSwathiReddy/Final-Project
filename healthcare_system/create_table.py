import sqlite3

conn = sqlite3.connect('db.sqlite3')


conn.execute('create table register(username varchar(30) primary key, password varchar(30), contact varchar(12), email varchar(30), address varchar(40), usertype varchar(40));')
conn.execute('create table medicinedetails(medicine_name varchar(50), dosage varchar(50), formula varchar(50), details varchar(200), side_effects varchar(200), address varchar(100), latitude varchar(50), longitude varchar(50));')
conn.execute('create table prescription(patient_name varchar(50), doctor_name varchar(50), query varchar(200), prescription varchar(300), prescribe_date timestamp);')
conn.execute('create table reminder(id integer primary key autoincrement,patient_name varchar(50), reminder_details varchar(300),email varchar(30), reminder_time timestamp);')
    