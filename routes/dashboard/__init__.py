from flask import Blueprint, render_template, session, redirect, url_for, make_response, request, flash, Response, jsonify, json
from flask import current_app as app
import hashlib
from routes.auth import login_required, admin_required
from datetime import date, datetime, timedelta
import calendar
import datetime
from dateutil import parser
from googleapiclient.discovery import build
import mysql.connector
from datetime import datetime
import os
import cv2
from PIL import Image
import numpy as np
from functools import wraps
from routes.absensi.training_input import generate_dataset
import requests

Dashboard = Blueprint (
    name='Dashboard',
    import_name=__name__,
    url_prefix='/dashboard',
    template_folder='../../templates/dashboard'
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="myabsensi"
    )

def create_calendar(year, month):
    cal = calendar.monthcalendar(year,month)
    return cal

@Dashboard.route('/', endpoint='index')
@admin_required
@login_required
def index():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    # ADMIN
    mycursor.execute("SELECT * FROM admin")
    admin = mycursor.fetchone()
    uname=admin[1]

    # Total Karyawan
    mycursor.execute("SELECT id_karyawan, nama_lengkap, jabatan, nidn_nipy, jenis_kelamin from karyawan")
    data = mycursor.fetchall()
    total_data = len(data)

    # Menghitung siapa saja hari ini yang telah absen dan pulang
    mycursor.execute("""
        SELECT 
            a.karyawan_id, 
            b.nama_lengkap, 
            DATE_FORMAT(a.waktu_masuk, '%Y-%m-%d') AS tanggal,  -- Mengganti kolom jabatan dengan tanggal
            DATE_FORMAT(a.waktu_masuk, '%H:%i') AS waktu_masuk,
            IF(c.waktu_pulang IS NULL, 'Belum absen', DATE_FORMAT(c.waktu_pulang, '%H:%i')) AS waktu_pulang
        FROM 
            absen_masuk a
        JOIN 
            karyawan b ON a.karyawan_id = b.id_karyawan
        LEFT JOIN 
            absen_pulang c ON a.karyawan_id = c.karyawan_id
        WHERE 
            DATE(a.waktu_masuk) = CURDATE()
        ORDER BY 
            a.waktu_masuk
    """)
    absen = mycursor.fetchall()
    print(absen)

    # Laporan kehadiran berupa chart bar
    mycursor.execute("""
        SELECT YEAR(waktu_masuk) AS tahun, MONTHNAME(waktu_masuk) AS bulan, COUNT(*) AS jumlah_kehadiran
        FROM absen_masuk
        WHERE DATE(waktu_masuk) = %s
        GROUP BY YEAR(waktu_masuk), MONTH(waktu_masuk)
        ORDER BY YEAR(waktu_masuk), MONTH(waktu_masuk)
    """, (date.today(),))
    laporan_kehadiran = mycursor.fetchall()

    # Ekstraksi data untuk plotting
    bulan = [data[1] for data in laporan_kehadiran]
    jumlah_kehadiran = [data[2] for data in laporan_kehadiran]

    # Mengubah data ke format JSON
    data_json = json.dumps({
        'labels': bulan,
        'datasets': [{
            'label': 'Jumlah Kehadiran',
            'data': jumlah_kehadiran,
            'backgroundColor': 'rgba(75, 192, 192, 0.5)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    })
    
    mycursor.execute("""
        SELECT COUNT(*) AS total_kehadiran
        FROM absen_masuk
        WHERE DATE(waktu_masuk) = %s
    """, (date.today(),))
    total_kehadiran = mycursor.fetchone()[0]

    # Mendapatkan bulan dan tahun yang dipilih dari permintaan GET
    selected_month = int(request.args.get('month', 1))
    selected_year = int(request.args.get('year', 2023))

    # Menghitung kalender menggunakan modul calendar
    cal = calendar.monthcalendar(selected_year, selected_month)

    # Mendapatkan nama bulan
    month_name = calendar.month_name[selected_month]
    # year = calendar.y[selected_year]

    # Menentukan hari yang dipilih (misalnya hari ini)
    selected_day = 12  # Ganti dengan logika pemilihan hari yang sesuai

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    if 'user_id' in session:
        user_id = session['user_id']
        print(session)
        return render_template (
            title="Dashboard",
            template_name_or_list='home.html',
            total=total_data,
            user_id=user_id,
            absen=absen,
            admin=uname,
            kehadiran=total_kehadiran,
            calendar=cal,
            selected_month=selected_month,
            selected_year=selected_year,
            month_name=month_name,
            selected_day=selected_day,
            data_json=data_json
        )
        # return redirect(url_for('Dashboard.index', user_id=user_id))
    # else:
    #     return redirect(url_for('Auth.dashboard'))

@Dashboard.route('/daftarkaryawan')
@admin_required
@login_required
def daftarkaryawan():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT * FROM admin")
    admin = mycursor.fetchone()
    uname=admin[1]

    mycursor.execute("SELECT id_karyawan, nama_lengkap, jabatan, nidn_nipy, jenis_kelamin from karyawan")
    data = mycursor.fetchall()

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    return render_template (
        title="Daftar Karyawan | Dashboard",
        template_name_or_list='data_karyawan.html',
        data=data,
        admin=uname
    )

@Dashboard.route('/daftarkehadiran')
@admin_required
@login_required
def daftarkehadiran():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM admin")
    admin = mycursor.fetchone()
    uname=admin[1]

    sekarang = date
    mycursor.execute("""
        SELECT DISTINCT 
            absen_masuk.karyawan_id, 
            DATE(absen_masuk.waktu_masuk) AS tanggal,
            TIME(absen_masuk.waktu_masuk) AS waktu_masuk, 
            IFNULL(TIME(absen_pulang.waktu_pulang), 'Belum absen') AS waktu_pulang, 
            karyawan.nama_lengkap
        FROM absen_masuk
        LEFT JOIN absen_pulang ON absen_masuk.karyawan_id = absen_pulang.karyawan_id
        JOIN karyawan ON absen_masuk.karyawan_id = id_karyawan
        ORDER BY tanggal DESC, waktu_masuk DESC
    """)
    absen = mycursor.fetchall()
    data = [row for row in absen]
    
    print(data)

    hari = set()
    bulan = set()

    for row in data:
        tanggal = row[1]
        hari.add(tanggal.day)
        bulan.add(tanggal.month)

    # convert sets to lists and sort them
    hari = sorted(list(hari))
    bulan = sorted(list(bulan))

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    return render_template (
        title="Daftar Kehadiran | Dashboard",
        template_name_or_list='daftar_kehadiran.html',
        absen=absen,
        hari=hari,
        bulan=bulan,
        admin=uname
    )
    return jsonify(data)

@Dashboard.route('/laporankehadiran')
@admin_required
@login_required
def laporankehadiran():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    mycursor.execute("""
        SELECT k.id_karyawan, k.nama_lengkap, k.jabatan, k.nidn_nipy, k.jenis_kelamin,
            COALESCE(am.waktu, 'Tidak Ada Absen'),
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 1 THEN 1 ELSE 0 END) AS januari,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 2 THEN 1 ELSE 0 END) AS februari,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 3 THEN 1 ELSE 0 END) AS maret,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 4 THEN 1 ELSE 0 END) AS april,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 5 THEN 1 ELSE 0 END) AS mei,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 6 THEN 1 ELSE 0 END) AS juni,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 7 THEN 1 ELSE 0 END) AS juli,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 8 THEN 1 ELSE 0 END) AS agustus,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 9 THEN 1 ELSE 0 END) AS september,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 10 THEN 1 ELSE 0 END) AS oktober,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 11 THEN 1 ELSE 0 END) AS november,
            SUM(CASE WHEN MONTH(am.waktu_masuk) = 12 THEN 1 ELSE 0 END) AS desember
        FROM karyawan k
        LEFT JOIN absen_masuk am ON k.id_karyawan = am.karyawan_id
        GROUP BY k.id_karyawan
    """)
    laporankehadiran = mycursor.fetchall()
    print(laporankehadiran)

    jumlah_hari_kerja = 20
    jumlah_hari_kerja_semester_ganjil = 20 * 6  # Januari-Juni
    jumlah_hari_kerja_semester_genap = 20 * 6  # Juli-Desember

    data_laporan = []
    for row in laporankehadiran:
        total_kehadiran_karyawan = sum(row[6:18])
        persentase_kehadiran_karyawan = (total_kehadiran_karyawan / (jumlah_hari_kerja * 12)) * 100

        total_kehadiran_semester_ganjil = sum(row[6:12])
        total_kehadiran_semester_genap = sum(row[12:18])

        persentase_kehadiran_semester_ganjil = (total_kehadiran_semester_ganjil / jumlah_hari_kerja_semester_ganjil) * 100
        persentase_kehadiran_semester_genap = (total_kehadiran_semester_genap / jumlah_hari_kerja_semester_genap) * 100

        karyawan_data = {
            'id': row[0],
            'nama': row[1],
            'jabatan': row[2],
            'nidn_nipy': row[3],
            'jenis_kelamin': row[4],
            'persentase_kehadiran': persentase_kehadiran_karyawan,
            'persentase_kehadiran_ganjil': persentase_kehadiran_semester_ganjil,
            'persentase_kehadiran_genap': persentase_kehadiran_semester_genap
        }

        data_laporan.append(karyawan_data)


    mycursor.execute("SELECT * FROM admin")
    admin = mycursor.fetchone()
    uname=admin[1]

    # Menutup koneksi
    mycursor.close()
    mydb.close()
    
    return render_template (
        title="Laporan Kehadiran | Dashboard",
        template_name_or_list='laporan_kehadiran.html',
        laporankehadiran=data_laporan,
        admin=uname
        # total_kehadiran=total_kehadiran,
        # persentase_kehadiran=laporankehadiran
        # persentase_kehadiran_semester1=persentase_kehadiran_semester1,
        # persentase_kehadiran_semester2=persentase_kehadiran_semester2
    )

@Dashboard.route('/train_classifier/<id>')
@admin_required
@login_required
def train_classifier(id):
    dataset_dir = "dataset"
 
    path = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir)]
    faces = []
    ids = []
 
    for image in path:
        img = Image.open(image).convert('L');
        imageNp = np.array(img, 'uint8')
        # id = int(os.path.split(image)[1].split(".")[1])
        filename_part = os.path.split(image)[1].split(".")[1]
        if filename_part.isdigit():
            id = int(filename_part)
            faces.append(imageNp)
            ids.append(id)
            print(f"Training with ID: {id}")
        else:
            print(f"Unexpected filename part: {filename_part}")
 
        # faces.append(imageNp)
        # ids.append(id)
    ids = np.array(ids)
 
    # Train the classifier and save
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("routes/absensi/classifier.xml")
 
    return redirect(url_for('Dashboard.addprsn'))

@Dashboard.route('/addprsn')
@admin_required
@login_required
def addprsn():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT IFNULL(MAX(id_karyawan) + 1, 1) AS next_id FROM karyawan")
    row = mycursor.fetchone()
    id = row[0]
    print(int(id))

    mycursor.execute("SELECT * FROM admin")
    admin = mycursor.fetchone()
    uname=admin[1]

    # Menutup koneksi
    mycursor.close()
    mydb.close()
 
    return render_template(
        title="Karyawan | Dashboard",
        template_name_or_list="addkar.html",
        new_id=int(id),
        admin=uname
    )
 
@Dashboard.route('/addprsn_submit', methods=['POST'])
@admin_required
@login_required
def addprsn_submit():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    id_kry = request.form.get('id_kry')
    nidn_nipy = request.form.get('nidn_nipy')
    nama_lgkp = request.form.get('nama_lgkp')
    jabatan = request.form.get('jabatan')
    jn_klm = request.form.get('jn_klm')

    # Data akun user
    username = request.form.get('username')
    password = request.form.get('password')
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
 
    # Menyimpan data karyawan
    mycursor.execute(
        "INSERT INTO karyawan (id_karyawan, nidn_nipy, nama_lengkap, jabatan, jenis_kelamin) VALUES (%s, %s, %s, %s, %s)",
        (id_kry, nidn_nipy, nama_lgkp, jabatan, jn_klm)
    )

    # Menyimpan data akun user
    mycursor.execute(
        "INSERT INTO users (id_karyawan, username, password) VALUES (%s, %s, %s)",
        (id_kry, username, hashed_password)
    )
    mydb.commit()

    # Menutup koneksi
    mycursor.close()
    mydb.close()
 
    # return redirect(url_for('home'))
    return redirect(url_for('Dashboard.vfdataset_page', id=id_kry))
 
@Dashboard.route('/vfdataset_page/<id>')
@admin_required
@login_required
def vfdataset_page(id):
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM admin")
    admin = mycursor.fetchone()
    uname=admin[1]

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    return render_template(
        title="Training",
        template_name_or_list="gendataset.html",
        id=id,
        admin=uname
    )
 
@Dashboard.route('/vidfeed_dataset/<id>')
@admin_required
@login_required
def vidfeed_dataset(id):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(generate_dataset(id), mimetype='multipart/x-mixed-replace; boundary=frame')
