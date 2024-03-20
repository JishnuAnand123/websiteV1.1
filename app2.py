from flask import Flask, render_template, request
from google.auth import credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload,MediaIoBaseUpload
import os
import psycopg2


# postgres://users_8bbd_user:qcnVd4Sb1KEBRssm8KYPRYEtHjGnQ9L0@dpg-cnt70k8l6cac73d4fkr0-a.singapore-postgres.render.com/users_8bbd

from io import BytesIO

app = Flask(__name__)

# Load service account credentials from the JSON key file
credentials_file = './credential/credential.json'
#creds = credentials.Credentials.from_service_account_file(credentials_file)
creds = service_account.Credentials.from_service_account_file(credentials_file)

# Build the Drive service using the service account credentials
drive_service = build('drive', 'v3', credentials=creds)


# PostgreSQL database connection settings
db_host = 'dpg-cnt70k8l6cac73d4fkr0-a.singapore-postgres.render.com'
db_user = 'users_8bbd_user'
db_password = 'qcnVd4Sb1KEBRssm8KYPRYEtHjGnQ9L0'
db_name = 'users_8bbd'



# Function to create the 'resumes' table if it doesn't exist
def create_table():
    conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, dbname=db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            phone_num VARCHAR(20),
            email VARCHAR(255),
            job_role VARCHAR(255),
            file_name VARCHAR(255)
        )
    """)
    conn.commit()
    conn.close()




def insert_data(name, phone_num, email, job_role, file_name):
    conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, dbname=db_name)
    cur = conn.cursor()
    cur.execute("INSERT INTO resumes (name, phone_num, email, job_role, file_id) VALUES (%s, %s, %s, %s, %s)",
                (name, phone_num, email, job_role, file_name))
    conn.commit()
    conn.close()




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

    file_stream = BytesIO()
    uploaded_file.save(file_stream)
    file_stream.seek(0)  

    #temp_file_path = os.path.join(app.root_path, uploaded_file.filename)

    # Process and store the data/file as needed
#https://drive.google.com/drive/folders/1N6od-qw78TCy9v1nGcCg_Qilnyldi3Ad?usp=sharing
    # Upload file to Google Drive using service account credentials
    file_metadata = {
        'name': uploaded_file.filename,
        'parents': ['1N6od-qw78TCy9v1nGcCg_Qilnyldi3Ad']  # Update with your folder ID
    }
    mime_type = 'application/pdf' if uploaded_file.filename.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    #media_body = MediaFileUpload(uploaded_file, resumable=True,mimetype=mime_type)
    #media_body = MediaFileUpload(temp_file_path, resumable=True,mimetype=mime_type)
    media_body = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media_body,fields="id").execute()

    create_table()

    # Insert data into the PostgreSQL database
    insert_data(name, phone_num, email, job_role, uploaded_file.filename)

    return render_template("submit.html")

if __name__ == '__main__':
    app.run(debug=True,port=5004)
