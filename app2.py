from flask import Flask, render_template, request
from google.auth import credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

app = Flask(__name__)

# Load service account credentials from the JSON key file
credentials_file = './credential/credential.json'
#creds = credentials.Credentials.from_service_account_file(credentials_file)
creds = service_account.Credentials.from_service_account_file(credentials_file)

# Build the Drive service using the service account credentials
drive_service = build('drive', 'v3', credentials=creds)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone_num=request.form.get("phone")
    email = request.form.get('email')
    job_role=request.form.get("job")
    uploaded_file = request.files['file']

    temp_file_path = os.path.join(app.root_path, uploaded_file.filename)

    # Process and store the data/file as needed
#https://drive.google.com/drive/folders/1N6od-qw78TCy9v1nGcCg_Qilnyldi3Ad?usp=sharing
    # Upload file to Google Drive using service account credentials
    file_metadata = {
        'name': uploaded_file.filename,
        'parents': ['1N6od-qw78TCy9v1nGcCg_Qilnyldi3Ad']  # Update with your folder ID
    }
    mime_type = 'application/pdf' if uploaded_file.filename.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    media_body = MediaFileUpload(uploaded_file, resumable=True,mimetype=mime_type)
    #media_body = MediaFileUpload(temp_file_path, resumable=True,mimetype=mime_type)
    file = drive_service.files().create(body=file_metadata, media_body=media_body,fields="id").execute()

    return render_template("submit.html")

if __name__ == '__main__':
    app.run(debug=True,port=5004)
