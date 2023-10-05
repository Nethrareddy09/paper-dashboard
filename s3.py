from flask import *
import boto3
from botocore.exceptions import NoCredentialsError
import os

from dotenv import load_dotenv

current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
S3_REGION= 'ap-south-1'
AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the File Upload App"

@app.route("/s3", methods=["GET","POST"])
def upload_file():
        uploaded_files = request.files.getlist("file")
        for file in uploaded_files:
            if file.filename=='':
                 redirect(url_for('index'))

            s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=S3_REGION)
            bucket_name = "s3-flask-demo"
            s3.upload_fileobj(file, bucket_name, file.filename)
        return render_template("s3.html",msg="File uploaded successfully to S3")
        

if __name__ == "__main__":
    app.run(debug=True)