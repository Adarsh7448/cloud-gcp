from flask import Flask, request, render_template, redirect, jsonify
from google.cloud import storage
import sqlite3
import random

app = Flask(__name__)
DB_NAME = 'blogs.db'
BUCKET_NAME = "test-bucket-03052000"

def upload_file(s_file, d_file_name):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(d_file_name)
    blob.upload_from_file(s_file)
    return blob.public_url

def generate_name_tag(name):
    number = random.randint(100000, 999999)
    return f"{name}_{number}"

# Initialize database and create table if not exists
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            image_url TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def get_blogs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, image_url, content, author FROM blogs')
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

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO blogs (title, image_url, content, author) VALUES (?, ?, ?, ?)', (title, image_url, content, author))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('create_blogs.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)