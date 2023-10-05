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
import boto3

from dotenv import load_dotenv
current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')
# Load environment variables from the .env file
load_dotenv(dotenv_path)

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=S3_REGION)

def db_connection():
  connection = mysql.connector.connect(
  host="mysql-1ed7bbbc-wlmycn-2bde.aivencloud.com",
  user="nethra",
  password="AVNS_VZBjSvRHMNrTujGWv84",
  port="26098",
  database="defaultdb")
  return connection

e=os.environ.get('RQ_AMQPS')
url = os.environ.get('CLOUDAMQP_URL', e)
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
                bucket_name=payload["bucket_name"]
                print(f"+++++++++++++++{user_id}")
                print(f"+++++++++++++++{filename}")
                s3_key=payload["key"]
                path = os.getcwd()

                UPLOAD_FOLDER = os.path.join(path, 'uploads')
                # Extract the base name without extension from the S3 key
                base = os.path.basename(s3_key)
                c = os.path.splitext(base)[0]
                pdf_path = os.path.join(UPLOAD_FOLDER, f"{user_id}/{c}.pdf")
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

                s3_client.download_file(bucket_name, s3_key, pdf_path)

                if os.path.exists(pdf_path):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=15)
                    with open(pdf_path, "r") as text_file:
                        for line in text_file:
                            pdf.cell(200, 10, txt=line, ln=1, align="C")
                    pdf.output(pdf_path)

                    s3_client.upload_file(pdf_path, bucket_name, f"uploads/{user_id}/pdf/{filename}.pdf", ExtraArgs = {
                          "ContentDisposition": "inline",
                          "ContentType": "application/pdf"
                    })

                    os.remove(pdf_path)

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
