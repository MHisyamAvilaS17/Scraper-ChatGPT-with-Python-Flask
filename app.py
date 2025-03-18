import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session
import secrets
import os
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
import uuid
from datetime import datetime


# Muat environment variables dari .env file
load_dotenv()

app = Flask(__name__)

# Coba ambil SECRET_KEY dari .env, atau buat jika tidak ada
secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))  # Jika tidak ada, generate baru

# Gunakan secret_key untuk Flask sessions
app.secret_key = secret_key

print(f'Secret Key: {os.getenv("SECRET_KEY")}')


# Koneksi ke database MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",  # sesuaikan dengan user MySQL Anda
    password="",  # sesuaikan dengan password MySQL Anda
    database="implementasi"  # sesuaikan dengan nama database
)

# Route untuk login (seperti yang sudah dibuat sebelumnya)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Cek kredensial di database
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()  # Ambil hasil query

        cursor.close()  # Tutup cursor setelah mengambil hasil

        if user:
            # Login berhasil, simpan user_id ke session
            session['username'] = user['username']
            session['user_id'] = user['user_id']  # Simpan user_id di session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            # Login gagal
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/')
def home():
    if 'username' in session:
        # Ambil user_id dari session
        user_id = session.get('user_id')

        # Ambil data scraping untuk user ini dari database
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT conversation_id, url, created_at, preprocess 
            FROM scraping_results 
            WHERE user_id=%s
        """
        cursor.execute(query, (user_id,))
        scraping_results = cursor.fetchall()

        # Cek apakah scraping_results berisi data
        print(scraping_results)  # atau gunakan logging

        # Filter URL untuk menghilangkan duplikasi
        unique_results = []
        seen_urls = set()

        for result in scraping_results:
            if result['conversation_id'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['conversation_id'])

        return render_template('home.html', username=session['username'], results=unique_results)

    return redirect(url_for('login'))


import uuid

@app.route('/result', methods=['POST'])
def result():
    if 'user_id' not in session:
        flash('You must be logged in to scrape a URL.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        input_url = request.form['url']
        preprocess_choice = request.form.get('preprocess')  # Mendapatkan pilihan preprocess dari form

        # Set up Selenium WebDriver
        driver = webdriver.Chrome()
        driver.get(input_url)
        time.sleep(5)  # Tunggu beberapa detik untuk memastikan halaman termuat sepenuhnya
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Mencari semua pertanyaan dan respons
        questions = soup.find_all('div', {'class': 'whitespace-pre-wrap'})
        responses = soup.find_all('div', {'class': 'flex w-full flex-col gap-1 empty:hidden first:pt-[3px]'})

        # Ambil user_id dari session
        user_id = session.get('user_id')

        # Buat Conversation ID yang unik untuk sesi scraping ini
        conversation_id = str(uuid.uuid4())

        # Waktu saat ini
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Siapkan data untuk disimpan ke database
        data_to_save = []
        for question, response in zip(questions, responses):
            # Ambil teks asli dari question dan response
            question_text = question.get_text().strip().replace('\n', '\n ')  # Mengganti \n dengan spasi
            response_text = response.get_text().strip().replace('\n', '\n ')  # Mengganti \n dengan spasi

            # Lakukan preprosesing berdasarkan pilihan pengguna
            if preprocess_choice == 'lower':
                question_preprocessed = question_text.lower()
                response_preprocessed = response_text.lower()
            elif preprocess_choice == 'upper':
                question_preprocessed = question_text.upper()
                response_preprocessed = response_text.upper()
            else:
                question_preprocessed = None  # Jika pilihan None, tidak ada preproses
                response_preprocessed = None

            # Insert data ke database
            cursor = db.cursor()
            query = """
            INSERT INTO scraping_results (user_id, url, question, response, created_at, conversation_id, preprocess, question_preprocess, response_preprocess)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                user_id,
                input_url,
                question_text,
                response_text,
                datetime.now(),
                conversation_id,
                preprocess_choice,
                question_preprocessed,
                response_preprocessed
            ))
            db.commit()

        # Ambil conversation_id untuk ditampilkan di halaman result
        return redirect(url_for('view_result', conversation_id=conversation_id))

@app.route('/view_result/<conversation_id>')
def view_result(conversation_id):
    # Mengambil data dari database berdasarkan conversation_id
    cursor = db.cursor()
    query = '''
        SELECT question, response, question_preprocess, response_preprocess 
        FROM scraping_results WHERE conversation_id = %s
    '''
    cursor.execute(query, (conversation_id,))
    data = cursor.fetchall()

    # Tampilkan data di template HTML
    return render_template('view_result.html', data=data)

# Rute untuk menghapus data
@app.route('/delete/<string:conversation_id>', methods=['POST'])
def delete(conversation_id):
    cursor = db.cursor()
    
    # SQL query to delete the record based on conversation_id
    query = "DELETE FROM scraping_results WHERE conversation_id = %s"
    cursor.execute(query, (conversation_id,))
    
    # Commit the transaction
    db.commit()
    
    # Close the cursor
    cursor.close()
    
    # Redirect back to the home page
    return redirect(url_for('home', conversation_id=conversation_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Cek apakah username sudah terdaftar
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username=%s"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Username sudah terdaftar
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register'))
        else:
            # Simpan pengguna baru ke database
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, password))
            db.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))

    # Jika metode GET, tampilkan halaman register
    return render_template('register.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)  # Hapus user_id dari session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)