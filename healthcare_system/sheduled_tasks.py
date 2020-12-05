import sqlite3
from time import sleep
import smtplib
from datetime import datetime
import time


list_of_sent_mails = []


def send_mail(sender_mail, msg, mail, connection_obj):

    body = f'Subject: HealthCare Reminder \n\n{msg}'
    connection_obj.sendmail(sender_mail, mail, body)


# conn = psycopg2.connect(
#     host="localhost",
#     database="healthcare",
#     user="postgres",
#     password="Abcd1234")

done = []

def connect_db_and_send_mail():
    conn = sqlite3.connect('db.sqlite3')
    data = list(conn.execute(
        'select id,patient_name, reminder_details,email, reminder_time from reminder'))

    conn.close()
    connection = smtplib.SMTP('smtp.gmail.com', 587)
    sender_mail = 'swathireddy6697@gmail.com'

    pwd = 'osxckskvknfqqbcv'
    connection.ehlo()

    connection.starttls()
    connection.login(sender_mail, pwd)
    connection = smtplib.SMTP('smtp.gmail.com', 587)
    for x in data:
        val = (time.mktime(time.strptime(
            x[-1].replace('\'', ''), '%Y-%d-%m %H:%M')))
        hour = (datetime.fromtimestamp(val).hour)
        minute = (datetime.fromtimestamp(val).minute)
        current_time = datetime.now()
        if x[0] not in done:
            if hour == current_time.hour and minute == current_time.minute:
                send_mail(sender_mail, data[1], data[2], connection)
                done.append(x[0])
    connection.close()



while True:
    connect_db_and_send_mail()
