from flask import Blueprint, render_template, session
from flask import current_app as app
from flask import request, flash, redirect, url_for
import requests
import mysql.connector
from flask_cors import CORS
# import MySQLdb.cursors
import logging
from functools import wraps
# from main import get_db_cursor
# from flask_mysqldb import current_app as mysql
# from flask_mysqldb import MySQL

Auth = Blueprint (
    name='Auth',
    import_name=__name__,
    url_prefix='/auth',
    template_folder='../../templates/home'
)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('Auth.login'))
        return f(*args, **kwargs)
    return wrap

def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('Dashboard.index'))
        return f(*args, **kwargs)
    return wrap
    
@Auth.route('/dashboard/login')
@logout_required
def login():
    return render_template (    
        title="Login | My Absensi",
        template_name_or_list="login.html"
    )

@Auth.route('/dashboard/login', methods=['POST', 'GET'])
def login_proses():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='myabsensi'
    )
    cursor = db.cursor()

    # cursor = get_db_cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM admin WHERE username =  %s AND password = %s", (username, password))
        users = cursor.fetchone()

        if users:
            # Lakukan proses autentikasi dan validasi pengguna
            # Jika berhasil, simpan user_id ke dalam session
            session['loggedin'] = True
            session['user_id'] = users[0]
            # session['username'] = users['username']

            # logging.debug(f"user_id in session: {session.get('user_id')}")

            print('login berhasil',session)
            return redirect(url_for('Dashboard.index'))
        else:
            # Pengguna sudah terotentikasi, redirect ke halaman profil
            if 'user_id' in session:
                return redirect(url_for('Dashboard.index'))
            # Jika gagal menyimpan user_id
            return redirect(url_for('Auth.login', error=True))
    
    # return redirect(url_for('Auth.login', error=False))

@Auth.route('/logout')
def logout():
    session.clear()
    print(session)
    return redirect(url_for('Auth.login'))
