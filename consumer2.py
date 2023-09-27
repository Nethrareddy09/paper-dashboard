
import mysql.connector
from werkzeug.utils import secure_filename
from random import *
import os
import re
from pytube import YouTube
from pathlib import *
from fpdf import *
from app import *
import uuid
import datetime
import pika, os


def db_connection():
  connection = mysql.connector.connect(
  host="mysql-1ed7bbbc-wlmycn-2bde.aivencloud.com",
  user="nethra",
  password="AVNS_VZBjSvRHMNrTujGWv84",
  port="26098",
  database="defaultdb")
  return connection


url = os.environ.get('CLOUDAMQP_URL', 'amqps://bveiocbd:vAnbunpOezRO4FIFw81RuZyzx-SK4akN@puffin.rmq2.cloudamqp.com/bveiocbd')
params = pika.URLParameters(url)
connection1 = pika.BlockingConnection(params)
rq_channel = connection1.channel()
rq_channel.queue_declare(queue="speech_queue", durable=True)
rmq_channel = connection1.channel()
rmq_channel.queue_declare(queue="text_to_pdf_queue", durable=True)
connection = db_connection()
connection_cursor = connection.cursor()

def download_txt_to_pdf(ch, method, properties, body):
                print(body.decode().replace("'","\""))
                payload = json.loads(body.decode().replace("'","\""))
                print(payload)
                job_id = payload["job_id"]
                filename = payload["job_name"]
                user_id = payload["user_id"]
                print(f"+++++++++++++++{user_id}")
                print(f"+++++++++++++++{filename}")


                path = os.getcwd()
                UPLOAD_FOLDER = os.path.join(path, 'uploads')
                print(f"--------->{UPLOAD_FOLDER}")
                base = os.path.basename(filename)
                c = os.path.splitext(base)[0]
                
                if not os.path.exists(os.path.join(UPLOAD_FOLDER, str(user_id))):
                      os.makedirs(os.path.join(UPLOAD_FOLDER, str(user_id)))
                      file_path = os.path.join(UPLOAD_FOLDER, str(user_id), os.path.basename(filename))
                      with open(file_path, 'wb') as file:
                             file.write(body)

       
                

                # text_content = filename.read()
                pdf=FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=15)
                f=open((f"uploads/{user_id}/{filename}"),"r")
                for x in f:
                        pdf.cell(200,10,txt=x,ln=1,align="C")
                pdf.output(f"uploads/{user_id}/{c}.pdf")
                

                query = f"INSERT INTO login_flask_upload2 (user_id, filename) VALUES ('{user_id}','{c}.pdf');"
                connection_cursor.execute(query)
                connection.commit()


                query2 = f"UPDATE login_flask_queue2 SET job_status = 'completed' where job_id='{job_id}';"
                print(query2)
                connection_cursor.execute(query2)
                connection.commit()
                     
rmq_channel.basic_consume(queue="text_to_pdf_queue",on_message_callback=download_txt_to_pdf,auto_ack=True)
rmq_channel.start_consuming()
connection_cursor.close()
connection.close()
# rmq_channel.close()
