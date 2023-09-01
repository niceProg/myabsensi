from flask import Blueprint, render_template, session
from flask import current_app as app
from flask import request, flash, redirect, url_for
import hashlib
import requests
import mysql.connector
from flask_cors import CORS
import logging
from functools import wraps

Auth = Blueprint (
    name='Auth',
    import_name=__name__,
    url_prefix='/auth',
    template_folder='../../templates/auth'
)

# Koneksi db
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="myabsensi"
    )
# global login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Harap login terlebih dahulu.', 'error')

            # Cek role yang ada dalam session untuk menentukan arah redirect
            role = session.get('role', None)
            if role == 'admin':
                return redirect(url_for('Auth.admin_login'))
            elif session['role'] == 'user':  # Default ke user karyawan jika role tidak ditemukan
                return redirect(url_for('Auth.karyawan_login'))
        return f(*args, **kwargs)
    return wrap

# global logout
def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' in session:
            if session['role'] == 'admin':
                flash('Silahkan logout terlebih dahulu.', 'error')
                return redirect(url_for('Dashboard.index'))
            elif session['role'] == 'user':
                return redirect(url_for('User.index'))
        return f(*args, **kwargs)
    return wrap

# Karyawan
# auth user
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'role' not in session or session['role'] != 'user':
            flash('Halaman ini hanya untuk karyawan.', 'error')
            return redirect(url_for('Auth.karyawan_login'))
        return f(*args, **kwargs)
    return wrap

@Auth.route('/karyawan/login')
@logout_required
def karyawan_login():
    return render_template(
        title="Login Karyawan | My Absensi",
        template_name_or_list="login_user.html"  # misal template login sama untuk keduanya
    )
@Auth.route('/karyawan/login', methods=['GET', 'POST'])
def karyawan_login_proses():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    if request.method == 'POST':
        # Proses autentikasi untuk karyawan di sini
        username = request.form['username']
        password = request.form['password']

        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()

        mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        users = mycursor.fetchone()
        print(hashed_input_password)
        print(users)

        if users and hashed_input_password == users[3]:
            session['user_id'] = users[0] # misalkan user[0] adalah ID pengguna
            session['role'] = 'user' # menandakan ini adalah karyawan
            print(session)
            flash('Login berhasil sebagai Karyawan!', 'success')
            return redirect(url_for('User.index'))
        else:
            flash('Login gagal. Coba lagi.', 'error')
            return redirect(url_for('Auth.karyawan_login'))

# ADMIN
# auth admin
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Halaman ini hanya untuk admin.', 'error')
            return redirect(url_for('Auth.admin_login'))
        return f(*args, **kwargs)
    return wrap

@Auth.route('/dashboard/login')
@logout_required
def admin_login():
    return render_template (    
        title="Login | My Absensi",
        template_name_or_list="login_admin.html"
    )
@Auth.route('/dashboard/login', methods=['GET', 'POST'])
def admin_login_proses():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifikasi dengan database
        mycursor.execute("SELECT * FROM admin WHERE username =  %s AND password = %s", (username, password))
        admin = mycursor.fetchone()

        if admin:
            session['user_id'] = admin[0] # misalkan admin[0] adalah ID admin
            session['role'] = 'admin' # menandakan ini adalah admin
            print('login berhasil', session)
            flash('Login berhasil sebagai Admin!', 'success')
            return redirect(url_for('Dashboard.index'))

        else:
            flash('Login gagal. Coba lagi.', 'error')
            return redirect(url_for('Auth.admin_login'))

@Auth.route('/logout')
def logout():
    role = session.get('role')
    
    # Menghapus session
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('role', None)
    session.clear

    # Jika sebelumnya role-nya adalah admin, arahkan ke halaman login admin
    if role == 'admin':
        return redirect(url_for('Auth.admin_login'))
    elif role == 'user':
    # Jika tidak, arahkan ke halaman login user karyawan
        return redirect(url_for('Auth.karyawan_login'))

# @Auth.route('/dashboard/login')
# @logout_required
# def dashboard():
    # return render_template (    
    #     title="Login | My Absensi",
    #     template_name_or_list="login_admin.html"
    # )
# @Auth.route('/dashboard/login', methods=['POST', 'GET'])
# def login_proses():
#     mydb = get_db_connection()
#     mycursor = mydb.cursor()

#     # cursor = get_db_cursor()
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

        # mycursor.execute("SELECT * FROM admin WHERE username =  %s AND password = %s", (username, password))
        # admin = mycursor.fetchone()

#         if admin:
#             # Lakukan proses autentikasi dan validasi pengguna
#             # Jika berhasil, simpan user_id ke dalam session
#             session['loggedin'] = True
#             session['user_id'] = admin[0]
#             # session['message'] = 'Login Berhasil'
#             flash('Login berhasil!', 'success')
            
#             # Menutup koneksi
#             mycursor.close()
#             mydb.close()
            
#             print('login berhasil',session)
#             return redirect(url_for('Dashboard.index'))
#         else:
#             # Pengguna sudah terotentikasi, redirect ke halaman profil
#             if 'user_id' in session:
#                 return redirect(url_for('Dashboard.index'))
#             # Jika gagal menyimpan user_id
#             flash('Login gagal. Coba lagi.', 'error')
#             return redirect(url_for('Auth.dashboard'))

# @Auth.route('/logout/dashboard')
# def logout_dashboard():
#     # session.clear()
#     session.pop('loggedin', None)
#     session.pop('user_id', None)
#     session.pop('_flashes', None)
#     # session.pop('message', None)  # Menghapus pesan
#     flash('Anda telah logout', 'warning')
#     print(session)
#     return redirect(url_for('Auth.dashboard'))
