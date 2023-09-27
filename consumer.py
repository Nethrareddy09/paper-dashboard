import pika
import json
import os
import mysql.connector
from pytube import YouTube
import re

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
rmq_channel = connection1.channel()
rmq_channel.queue_declare(queue="text_to_pdf_queue", durable=True)

db_conn = db_connection()
db_cursor = db_conn.cursor()
def download_youtube_video(ch, method, properties, body):
                print(body.decode().replace("'","\""))
                payload = json.loads(body.decode().replace("'","\""))
                job_id = payload["job_id"]
                video_url = payload["job_url"]
                user_id = payload["user_id"]
                print(job_id,video_url,user_id)
                utube = YouTube(video_url)
                video = utube.streams.get_highest_resolution()
                file = f"{user_id}_{utube.title}.mp4"
                filename = re.sub(r'[\\/*?:"<>|()\']',"",file)
                path = os.getcwd()
                UPLOAD_FOLDER = os.path.join(path, 'uploads')
                os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
                # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                downloadFolder = str(os.path.join(f"{UPLOAD_FOLDER}/{user_id}"))
                video.download(downloadFolder, filename=filename)
                query = f"INSERT INTO login_flask_upload2 (user_id, filename) VALUES ('{user_id}', '{filename}');"
                print(query)
                db_cursor.execute(query)

                query2 = f"UPDATE login_flask_queue SET job_status = 'completed' where job_id='{job_id}';"
                print(query2)
                db_cursor.execute(query2)
                db_conn.commit()
                
              
                
rmq_channel.basic_consume(queue="text_to_pdf_queue",on_message_callback=download_youtube_video,auto_ack=True)
rmq_channel.start_consuming()
# rmq_channel.close()
#rmq_conn.close()
db_cursor.close()