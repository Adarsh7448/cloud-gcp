from flask import Flask, request, render_template, redirect, jsonify
from google.cloud import storage
# import sqlite3
import pymysql
import random
import os

app = Flask(__name__)
# DB_NAME = 'blogs.db'
# BUCKET_NAME = "test-bucket-03052000"

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_BUCKET = os.environ.get('DB_BUCKET')

def get_connection():
    return pymysql.connect( # user, password, database, connection
        unix_socket = DB_HOST,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME,
        cursorclass = pymysql.cursors.DictCursor
    )

def upload_file(s_file, d_file_name):
    client = storage.Client()
    bucket = client.bucket(DB_BUCKET)
    blob = bucket.blob(d_file_name)
    blob.upload_from_file(s_file)
    return blob.public_url

def generate_name_tag(name):
    number = random.randint(100000, 999999)
    return f"{name}_{number}"

    

# Initialize database and create table if not exists
# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS blogs (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT NOT NULL,
#             image_url TEXT NOT NULL,
#             content TEXT NOT NULL,
#             author TEXT NOT NULL
#         )
#     ''')
#     conn.commit()
#     conn.close()

@app.route('/', methods=['GET'])
def get_blogs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blogs;')
    blogs = cursor.fetchall()
    conn.close()
    return render_template('blogs.html', blogs = blogs), 200

@app.route('/blogs', methods=['GET','POST'])
def create_blog():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author')
        image = request.files.get('image')

        if not title or not content or not author or not image:
            return jsonify({'error': 'Missing required fields'}), 400

        image_url = upload_file(image, generate_name_tag(author))

        conn = get_connection()
        cursor = conn.cursor()
        # cursor.execute('INSERT INTO blogs (title, image_url, content, author) VALUES (?, ?, ?, ?);', (title, image_url, content, author))
        cursor.execute('INSERT INTO blogs (title, image_url, content, author) VALUES (%s, %s, %s, %s)', (title, image_url, content, author))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('create_blogs.html')

if __name__ == '__main__':
    # init_db()
    app.run(host="0.0.0.0", port=8080)