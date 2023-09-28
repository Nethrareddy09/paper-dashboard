from flask import *
import mysql.connector
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from random import *
from flask import session,render_template,flash
import os
import re
from pytube import YouTube
from pathlib import *
from fpdf import *
from app import *
import uuid
import datetime
import pika, os

from dotenv import load_dotenv
current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')
# Load environment variables from the .env file
load_dotenv(dotenv_path)
# initialize first flask

app = Flask(__name__)
mail = Mail(app)
app.secret_key='nethra325reddy@gmail.com'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['RQ_AMQPS']=os.environ.get('RQ_AMQPS')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def db_connection():
  connection = mysql.connector.connect(
  host="mysql-1ed7bbbc-wlmycn-2bde.aivencloud.com",
  user="nethra",
  password="AVNS_VZBjSvRHMNrTujGWv84",
  port="26098",
  database="defaultdb")
  return connection

def rabbitdq_connection():
		d=os.environ.get('RQ_AMQPS')
		url = os.environ.get('CLOUDAMQP_URL', d)
		params = pika.URLParameters(url)
		connection1 = pika.BlockingConnection(params)
		return connection1

@app.route('/validate', methods=['POST'])
def validate_otp(email, otp):
		email = request.form['email']
		otp = request.form['otp']
		connection = db_connection()
		connection_cursor = connection.cursor()
		query = f"SELECT * from login_flask_345 where email = '{email}' and otp = '{otp}'"
		connection_cursor.execute(query)
		user =connection_cursor.fetchall()
		print(len(user))
		if len(user)>0:
			return True
		else:
			return False
		
# @app.route('/profile')
# def profile():
# 			if 'user_id' in session:
# 				connection = db_connection()
# 				connection_cursor = connection.cursor()

# 				user_id = session['user_id']
# 				query=f"SELECT * from login_flask_345 where personid ={user_id}"
# 				print("========")
# 				connection_cursor.execute(query)
# 				users =connection_cursor.fetchone()
# 				print(users)
# 				return render_template('editprofile.html',users=users)
# 			else:
# 				message="You must be logged in"
# 				return render_template('login.html',message=message)


@app.route('/', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html',message="")
	elif request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		query = f"SELECT * from login_flask_345 where username = '{username}' and password = '{password}';"
		connection = db_connection()
		connection_cursor = connection.cursor()
		connection_cursor.execute(query)
		user = connection_cursor.fetchone()
		print(user)
		print("...))))))..")
		if user is not None:
				if user[4]==username and user[2]==password:
					session['user_id'] = user[0]
					flash("login success")
					return redirect(url_for('editprofile'), )
		else:
			flash("login unsuccessful")
			return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
		message=" "
		if request.method == 'GET':
			return render_template('register.html', message="please fill out the form")
		elif request.method == 'POST':
			print(request.form)
			if 'verify' in request.form:
				print("-------->")
				email = request.form['email']
				print(email)
				otp_req = request.form['otp']
				if validate_otp(email, otp_req):
					return render_template("login.html", message="Successfully Verified... Please Login.")
				else:
					return render_template("verify.html")
				
			if 'register' in request.form:
				print("Register")
				phonenum=request.form['phonenum']
				password = request.form['password']
				email = request.form['email']
				username = request.form['username']
				query= f"SELECT * from login_flask_345 where email = '{email}'"
				connection = db_connection()
				connection_cursor = connection.cursor()
				connection_cursor.execute(query)
				users=connection_cursor.fetchall()
				print(len(users))
				if len(users)>0:
					message = "The email address already exists"
					connection_cursor.close()
					connection.close()
					return render_template('register.html', message=message)
				else:
					otp=randint(000000,999999)
					validation = 0
					query= f"INSERT INTO login_flask_345 (username,email,password,phonenum,otp,validation) VALUES ('{username}','{email}', '{password}','{phonenum}','{otp}','{validation}');"
					connection_cursor.execute(query)
					connection.commit()
					connection_cursor.close()
					connection.close()
					msg = Message(subject='OTP',sender ='nethra325reddy@gmail.com',recipients = [email] )
					msg.body = str(otp)
					mail.send(msg)
					return render_template('verify.html', message='Registration successful', email=email)
			else:
				message = "Please enter an email address"
			return render_template('register.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','mp4','avi','txt','pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
		
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/delete/<int:user_id>/<filename>', methods=['POST'])

def delete_image(user_id,filename):
	session_user_id = session.get('user_id')
	if session_user_id is not None and str(session_user_id) == str(user_id):
		path_to_delete = os.path.join('uploads', str(user_id), filename)
		if os.path.exists(path_to_delete):
			os.remove(path_to_delete)
			connection = db_connection()
			connection_cursor = connection.cursor()
			query = f"DELETE FROM login_flask_upload WHERE user_id='{user_id}' AND filename='{filename}';"
			connection_cursor.execute(query)
			connection.commit()
			connection_cursor.close()
			connection.close()
			return redirect(url_for('gallery'))
		else:
			return "Forbidden", 403
		
@app.route('/delete2/<int:user_id>/<filename>', methods=['POST'])
def delete2(user_id,filename):
	session_user_id = session.get('user_id')
	if session_user_id is not None and str(session_user_id) == str(user_id):
		path_to = os.path.join('uploads', str(user_id), filename)
		print(f"it's filename in deleting post--->{filename}")
		print(f"path_to---->{path_to}")
		if os.path.exists(path_to):
			print("++++++++++++++++++++++++++++++++")
			os.remove(path_to)
			print(f"After delete--->{path_to}")
			connection = db_connection()
			connection_cursor = connection.cursor()
			query2 = f"DELETE FROM login_flask_upload2 WHERE user_id='{user_id}' AND filename='{filename}';"
			print("--------------")
			connection_cursor.execute(query2)
			connection.commit()
			connection_cursor.close()
			connection.close()
			return redirect(url_for('videos'))
		else:
			return "Forbidden", 403

@app.route('/gallery',methods=['POST','GET'])
def gallery():
		if request.method == 'GET':
			if 'user_id'in session:
				user_id=session.get('user_id')
				print(user_id)
				connection = db_connection()
				connection_cursor = connection.cursor()
				query = f" SELECT  user_id,filename from login_flask_upload WHERE user_id='{user_id}';"
				print("========"+query)
				connection_cursor.execute(query)
				files = connection_cursor.fetchall()
				connection_cursor.close()
				connection.close()
				images = [file for file in files if file[1].lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]
				videos = [file for file in files if file[1].lower().endswith(('mp4', 'avi'))]
				print(videos)
				print(images)
			return render_template('gallery.html', images=images, videos=videos)
 
		if request.method == 'POST':
				if 'user_id' in session and 'file' in request.files:
					file=request.files['file']
					print(file)
					user_id=session['user_id']
					print(user_id)
					path = os.getcwd()
					print(f"path----->{path}")
					UPLOAD_FOLDER = os.path.join(path, 'uploads')
					# for file in files
					if file and allowed_file(file.filename):
							filename = secure_filename(file.filename)
							print(f"actual filename------>{filename}")
							os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
							app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
							file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}", filename))
							connection = db_connection()
							connection_cursor = connection.cursor()
							query = f"INSERT INTO login_flask_upload(user_id,filename) VALUE ('{user_id}', '{filename}');"
							print(query)
							connection_cursor.execute(query)
							connection.commit()
							connection_cursor.close()
							connection.close()
				return redirect(url_for('gallery'))

@app.route('/uploads/<user_id>/<filename>',methods=["GET"])
def uploads(user_id, filename):
	session_user_id=session.get('user_id')
	print(session_user_id)
	if session_user_id is not None:
		print(user_id )
		if str(session_user_id)== str(user_id):
			if filename.lower().endswith(('mp4','avi')):
				return send_file(f"uploads/{user_id}/{filename}")
			elif filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
				return send_file(f"uploads/{user_id}/{filename}")
			elif filename.lower().endswith(('txt','pdf')):
				pdf_path=os.path.join('uploads',str(user_id),filename)
				return send_file(pdf_path,as_attachment=False)
		else:
			return "Forbidden", 403

@app.route('/editprofile',methods=["POST","GET"])
def editprofile():	
			if 'user_id' in session:
				user_id=session.get('user_id')
				if request.method=='GET':
					connection = db_connection()
					connection_cursor = connection.cursor()
					query=f"SELECT * FROM login_flask_345 WHERE personid ='{user_id}';"
					connection_cursor.execute(query)
					print(f"----------->{query}")
					user=connection_cursor.fetchone()
					connection.close()
					return render_template('editprofile.html',user=user)
				# if user is None:
				# 		return "User not found"
				#  return render_template('editprofile.html',user=user)
				
				if request.method=="POST":
					new_username=request.form['username']
					new_email=request.form['email']
					new_phonenum=request.form['phonenum']
					print(new_phonenum)
					connection = db_connection()
					connection_cursor = connection.cursor()
					query=f"UPDATE login_flask_345 SET username='{new_username}', email='{new_email}', phonenum='{new_phonenum}' WHERE personid='{user_id}';"
					connection_cursor.execute(query)
					print(query)
					connection.commit()
					connection_cursor.close()
					connection.close()
					return redirect(url_for('editprofile',user_id=user_id))
			
			return "forbidden"

@app.route('/videos', methods=['POST','GET'])

def videos():
    if request.method == 'GET':
        if 'user_id'in session:
            user_id=session.get('user_id')
            connection = db_connection()
            connection_cursor = connection.cursor()
            query = f" SELECT  user_id,filename from login_flask_upload2 WHERE user_id='{user_id}';"
            print(query)
            connection_cursor.execute(query)
            videos = connection_cursor.fetchall()
            print(f"Total videos information ---->{videos}")
            connection_cursor.close()
            connection.close()
        return render_template('videos.html',videos=videos)

    if request.method == 'POST':
        if 'user_id' in session and 'files' in request.files:
            files=request.files.getlist('files')
            print("--------------------------------------------")
            print(type(files))
            user_id=session['user_id']
            print(user_id)
            path = os.getcwd()
            print(f"path----->{path}")
            UPLOAD_FOLDER = os.path.join(path, 'uploads')
            for file in files:
                if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            print(f"actual filename------>{filename}")
                            os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
                            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                            file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}",filename))
                            print("-----------------------------------")
                            connection = db_connection()
                            connection_cursor = connection.cursor()
                            query = f"INSERT INTO login_flask_upload2 (user_id,filename) VALUE ('{user_id}', '{filename}');"
                            print(query)
                            connection_cursor.execute(query)
                            connection.commit()
                            connection_cursor.close()
                            connection.close()
            return redirect(url_for('videos'))

@app.route("/download", methods=["GET","POST"])
def download():      
	mesage = ''
	errorType = 0
	if request.method == 'POST' and 'video_url' in request.form:
		youtubeUrl = request.form["video_url"]
		print(youtubeUrl)
		if(youtubeUrl):
			validateVideoUrl = (r'(https?://)?(www\.)?''(youtube|youtu|youtube-nocookie)\.(com|be)/''(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
			validVideoUrl = re.match(validateVideoUrl, youtubeUrl)
			if validVideoUrl:
				url = YouTube(youtubeUrl)
				video = url.streams.get_highest_resolution()
				filename = f"{session['user_id']}_{url.title}.mp4"
				user_id=session['user_id']
				path=os.getcwd()
				UPLOAD_FOLDER = os.path.join(path, 'uploads')
				app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
				downloadFolder = str(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}"))
				video.download(downloadFolder, filename=filename)
				connection=db_connection()
				connection_cursor=connection.cursor()
				query = f"INSERT INTO login_flask_upload2 (user_id, filename) VALUES ('{user_id}', '{filename}');"
				connection_cursor.execute(query)
				connection.commit()
				connection_cursor.close()
				connection.close()
				mesage = 'Video Downloaded and Added to Your Profile Successfully!'
				errorType = 1
				return redirect(url_for('videos'))
			else:
				mesage = 'Enter Valid YouTube Video URL!'
				errorType = 0        
		else:
			mesage='enter Youtube video url'
			errorType=0
	return render_template('download.html', mesage = mesage, errorType = errorType)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        otp = str(randint(100000, 999999))
        msg = Message(subject='Forgot Password OTP', sender='your_email@gmail.com', recipients=[email])
        msg.body = f'Your OTP for resetting the password is:{otp}'
        mail.send(msg)
        session['reset_password_otp'] = otp
        session['reset_password_email'] = email
        return redirect(url_for('verify_otp'))
    return render_template('forgot_password.html')
 
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
	if request.method == 'POST':
		entered_otp = request.form['otp']
		new_password = request.form['new_password']
		confirm_password=request.form['confirm_password']
		if 'reset_password_otp' in session and 'reset_password_email' in session:
			if entered_otp == session['reset_password_otp']:
				if new_password==confirm_password:
					email = session['reset_password_email']
					connection = db_connection()
					connection_cursor = connection.cursor()
					query = f"UPDATE login_flask_345 SET password = '{new_password}' WHERE email = '{email}';"
					connection_cursor.execute(query)
					connection.commit()
					connection_cursor.close()
					connection.close()
					flash('Password reset successful. Please log in with your new password.')
					return redirect(url_for('login'))
				else:
					flash='passwords donot match'
					return render_template('verify_otp.html',flash=flash)
			else:
				flash='Incorrect otp.Please try again'
				return render_template('verify_otp.html',flash=flash)
		else:
		    return render_template('verify_otp.html')
	return render_template('verify_otp.html')

@app.route('/text_to_pdf', methods=['GET', 'POST'])
def text_to_pdf():
		if request.method == 'GET':
			if 'user_id'in session:
				user_id=session.get('user_id')
				print(user_id)
				connection = db_connection()
				connection_cursor = connection.cursor()
				query = f" SELECT user_id,filename from login_flask_upload2 WHERE user_id='{user_id}';"
				print("========"+query)
				connection_cursor.execute(query)
				files = connection_cursor.fetchall()
				print("==========")
				print(files)
				connection_cursor.close()
				connection.close()
				pdf_files=[file for file in files if file[1].lower().endswith(('pdf','txt'))]
				print(pdf_files)
				return render_template('text_to_pdf.html', pdf_files=pdf_files)
			
		elif request.method == 'POST':
			print(request.files)
			message=""
			errorType = 1
			if 'user_id' in session and 'text_file' in request.files:
				text_file=request.files['text_file']
				print(f"===={text_file}")
				connection = db_connection()
				connection_cursor = connection.cursor()
				rmq_conn = rabbitdq_connection()
				rmq_channel = rmq_conn.channel()
				rmq_channel.queue_declare(queue="text_to_pdf_queue", durable=True)
				for text_file in request.files.getlist('text_file'):
					if allowed_file(text_file.filename):
						user_id=session['user_id']
						path=os.getcwd()
						print(path)
						UPLOAD_FOLDER=os.path.join(path,'uploads')
						app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
						filename = secure_filename(text_file.filename)
						os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
						pdf_path=text_file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}", filename))
						print(pdf_path)

						timestamp = datetime.datetime.now()
						status="queued"
						id=uuid.uuid1()
						
						query=f"INSERT INTO login_flask_queue2(job_id,job_name,user_id,time_stamp,job_status) VALUES ('{id}', '{filename}','{user_id}','{timestamp}','{status}');"
						connection_cursor.execute(query)
						connection.commit()

						payload={
							"job_id": str(id),
							"job_name": filename,
							"user_id": user_id,
							"time_stamp": str(timestamp)
						}
						print(payload)
						rmq_channel.basic_publish(body=str(payload), exchange="", routing_key="text_to_pdf_queue")

				message = 'File downloaded successfully'
				errorType = 1
				connection_cursor.close()
				connection.close()
				rmq_channel.close()
				rmq_conn.close()
			# connection_cursor.close()
			# connection.close()
			# rmq_channel.close()
			# rmq_conn.close()
			return render_template('text_to_pdf.html',message=message,errorType = errorType)

	
			
@app.route("/bulkdownload", methods=["GET","POST"])
def bulkdownload():      
	mesage = ''
	errorType = 0
	if request.method == 'POST' and 'video_url' in request.form:
		youtubeUrls = request.form.get("video_url")
		youtubeUrls = youtubeUrls.split("\n")

		connection = db_connection()
		connection_cursor = connection.cursor()
		rmq_conn = rabbitdq_connection()
		rmq_channel = rmq_conn.channel()
		rmq_channel.queue_declare(queue="youtube_download_queue", durable=True)

		user_id = session['user_id']		
		timestamp = datetime.datetime.now()
		status="queued"

		for url in youtubeUrls:
			id = uuid.uuid1()
			print(id)
			query2=f"INSERT INTO login_flask_queue(job_id,job_url,user_id,time_stamp,job_status) VALUES ('{id}', '{url}','{user_id}','{timestamp}','{status}');"
			print(f"++++++++++++++++++++++{query2}")
			connection_cursor.execute(query2)
			connection.commit()

			payload={
				"job_id": str(id),
				"job_url": url,
				"user_id": user_id,
				"timestamp": str(timestamp)
			}
			print(payload)
			rmq_channel.basic_publish(body=str(payload), exchange="", routing_key="text_to_pdf_queue")

		mesage = 'Video Downloaded and Added to Your Profile Successfully!'
		
		errorType = 1
		connection_cursor.close()
		connection.close()
		rmq_channel.close()
		rmq_conn.close()

	return render_template('bulkdownload.html', mesage = mesage, errorType = errorType)


if __name__=="__main__":
	app.run(debug= True)









