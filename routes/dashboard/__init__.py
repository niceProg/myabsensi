from flask import Blueprint, render_template, session, redirect, url_for, make_response, request, flash, Response, jsonify, json
from flask import current_app as app
from routes.auth import login_required
from datetime import date, datetime, timedelta
import calendar
import datetime
from dateutil import parser
from googleapiclient.discovery import build
import mysql.connector
from datetime import datetime
from flask_cors import CORS
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

db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='myabsensi'
)
cursor=db.cursor()

def create_calendar(year, month):
    cal = calendar.monthcalendar(year,month)
    return cal

@Dashboard.route('/', endpoint='index')
@login_required
def index():
    # ADMIN
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    uname=admin[1]

    # Total Karyawan
    cursor.execute("SELECT id_karyawan, nama_lengkap, jabatan, nidn_nipy, jenis_kelamin from karyawan")
    data = cursor.fetchall()
    total_data = len(data)

    # Menghitung siapa saja hari ini yang telah absen dan pulang
    cursor.execute("""
        SELECT DISTINCT absen_masuk.karyawan_id, absen_masuk.waktu,
                   COALESCE(DATE_FORMAT(absen_masuk.waktu_masuk, '%H:%i'), 'Tidak Hadir') AS waktu_masuk,
                   COALESCE(DATE_FORMAT(absen_pulang.waktu_pulang, '%H:%i'), 'Belum Pulang') AS waktu_pulang,
                   karyawan.nama_lengkap
        FROM absen_masuk
        JOIN absen_pulang ON absen_masuk.karyawan_id = absen_pulang.karyawan_id
        JOIN karyawan ON absen_masuk.karyawan_id = id_karyawan
        WHERE DATE(absen_masuk.waktu) = %s
    """, (date.today(),))
    absen = cursor.fetchall()
    print(absen)

    # Laporan kehadiran berupa chart bar
    cursor.execute("""
        SELECT YEAR(waktu_masuk) AS tahun, MONTHNAME(waktu_masuk) AS bulan, COUNT(*) AS jumlah_kehadiran
        FROM absen_masuk
        WHERE DATE(waktu_masuk) = %s
        GROUP BY YEAR(waktu_masuk), MONTH(waktu_masuk)
        ORDER BY YEAR(waktu_masuk), MONTH(waktu_masuk)
    """, (date.today(),))
    laporan_kehadiran = cursor.fetchall()

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
    
    cursor.execute("""
        SELECT COUNT(*) AS total_kehadiran
        FROM absen_masuk
        WHERE DATE(waktu_masuk) = %s
    """, (date.today(),))
    total_kehadiran = cursor.fetchone()[0]

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
    else:
        return redirect(url_for('Auth.login'))

@Dashboard.route('/daftarkaryawan')
@login_required
def daftarkaryawan():
    
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    uname=admin[1]

    cursor.execute("SELECT id_karyawan, nama_lengkap, jabatan, nidn_nipy, jenis_kelamin from karyawan")
    data = cursor.fetchall()

    return render_template (
        title="Daftar Karyawan | Dashboard",
        template_name_or_list='data_karyawan.html',
        data=data,
        admin=uname
    )

@Dashboard.route('/daftarkehadiran')
@login_required
def daftarkehadiran():
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    uname=admin[1]

    sekarang = date
    cursor.execute("""
        SELECT DISTINCT absen_masuk.karyawan_id, absen_masuk.waktu, TIME(absen_masuk.waktu_masuk) AS waktu_masuk, TIME(absen_pulang.waktu_pulang) AS waktu_pulang, karyawan.nama_lengkap
        FROM absen_masuk
        JOIN absen_pulang ON absen_masuk.karyawan_id = absen_pulang.karyawan_id
        JOIN karyawan ON absen_masuk.karyawan_id = id_karyawan
    """)
    absen = cursor.fetchall()
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
@login_required
def laporankehadiran():
    cursor.execute("""
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
    laporankehadiran = cursor.fetchall()
    print(laporankehadiran)

    total_kehadiran = 0
    for row in laporankehadiran:
        for i in range(6, 18):
            total_kehadiran += row[i]
    jumlah_hari_kerja = 20
    persentase_kehadiran = (total_kehadiran / (jumlah_hari_kerja * len(laporankehadiran))) * 100

    print("Total Kehadiran Seluruh Karyawan: ", total_kehadiran)
    print("Jumlah Hari Kerja: ", jumlah_hari_kerja)
    print("Persentase Kehadiran: ", persentase_kehadiran, "%")
    
    # Menghitung total kehadiran untuk setiap semester
    total_kehadiran_semester1 = 0
    total_kehadiran_semester2 = 0
    for row in laporankehadiran:
        for i in range(6, 10):  # Semester 1, kolom Januari-April
            total_kehadiran_semester1 += row[i]
        for i in range(10, 14):  # Semester 2, kolom Mei-Agustus
            total_kehadiran_semester2 += row[i]
    # Menghitung persentase kehadiran untuk setiap semester
    jumlah_hari_kerja_semester1 = 80  # Jumlah hari kerja dalam semester 1
    jumlah_hari_kerja_semester2 = 80  # Jumlah hari kerja dalam semester 2
    persentase_kehadiran_semester1 = (total_kehadiran_semester1 / (jumlah_hari_kerja_semester1 * len(laporankehadiran))) * 100
    persentase_kehadiran_semester2 = (total_kehadiran_semester2 / (jumlah_hari_kerja_semester2 * len(laporankehadiran))) * 100
    # print(laporankehadiran)

    # api_key = "AIzaSyCPZq8IXMMCilPLNuZxiiCdAUASUtvdqEk"
    # # Inisialisasi objek Google Calendar API
    # service = build("calendar", "v3", developerKey=api_key)
    # # Daftar tanggal libur atau tanggal merah
    # tanggal_libur = []
    # # Mendapatkan acara-acara dari kalender publik dengan kata kunci "holiday"
    # events = service.events().list(calendarId="id.indonesian#holiday@group.v.calendar.google.com").execute()
    # for event in events['items']:
    #     start_date = datetime.strptime(event['start']['date'], "%Y-%m-%d").date()
    #     tanggal_libur.append(start_date)

    # # Menghitung jumlah hari kerja dalam rentang waktu tertentu
    # start_date = datetime(2023, 7, 1).date()  # Tanggal awal
    # end_date = datetime(2023, 7, 31).date()  # Tanggal akhir

    # jumlah_absensi = 0
    # # Mengambil data kehadiran
    # for data in laporankehadiran:
    #     absensi = data[5]  # Kolom absensi dalam query Anda
    #     print(data)
    #     if absensi != 'Tidak Ada Absen':
    #         jumlah_absensi += 1

    # current_date = start_date
    # jumlah_hari_kerja = 0

    # while current_date <= end_date:
    #     # Periksa apakah tanggal bukan hari libur dan merupakan hari kerja (Senin-Jumat)
    #     if current_date.weekday() < 5 and current_date not in tanggal_libur:
    #         jumlah_hari_kerja += 1

    #     current_date += timedelta(days=1)

    # print("Jumlah Hari Kerja: ", jumlah_hari_kerja)
    
    # persentase_kehadiran_total = (jumlah_absensi / jumlah_hari_kerja) * 100
    # print("Persentase Kehadiran: {:.0f}%".format(persentase_kehadiran_total))

    # # Membuat dictionary untuk menyimpan jumlah absensi setiap karyawan
    # jumlah_absensi_per_karyawan = {}
    # # Mengambil data kehadiran
    # for data in laporankehadiran:
    #     karyawan_id = data[0]  # Kolom ID Karyawan dalam query Anda
    #     absensi = data[5]  # Kolom absensi dalam query Anda
    #     if karyawan_id not in jumlah_absensi_per_karyawan:
    #         jumlah_absensi_per_karyawan[karyawan_id] = 0
    #     if absensi != 'Tidak Ada Absen':
    #         jumlah_absensi_per_karyawan[karyawan_id] += 1
    # # Menghitung persentase kehadiran untuk setiap karyawan
    # persentase_kehadiran_per_karyawan = {}
    # for karyawan_id, jumlah_absensi in jumlah_absensi_per_karyawan.items():
    #     persentase_kehadiran_per_karyawan[karyawan_id] = (jumlah_absensi / jumlah_hari_kerja) * 100
    # # Menampilkan persentase kehadiran untuk setiap karyawan
    # for karyawan_id, persentase_kehadiran in persentase_kehadiran_per_karyawan.items():
    #     print("Karyawan ID: ", karyawan_id)
    #     print("Persentase Kehadiran: {:.2f}%".format(persentase_kehadiran))
    #     print()

    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    uname=admin[1]
    
    return render_template (
        title="Laporan Kehadiran | Dashboard",
        template_name_or_list='laporan_kehadiran.html',
        laporankehadiran=laporankehadiran,
        admin=uname,
        total_kehadiran=total_kehadiran,
        persentase_kehadiran=persentase_kehadiran,
        persentase_kehadiran_semester1=persentase_kehadiran_semester1,
        persentase_kehadiran_semester2=persentase_kehadiran_semester2
        # persentase_kehadiran=persentase_kehadiran_total,
        # persentase_karyawan=persentase_kehadiran_per_karyawan
    )

@Dashboard.route('/train_classifier/<id>')
@login_required
def train_classifier(id):
    dataset_dir = "dataset"
 
    path = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir)]
    faces = []
    ids = []
 
    for image in path:
        img = Image.open(image).convert('L');
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])
 
        faces.append(imageNp)
        ids.append(id)
    ids = np.array(ids)
 
    # Train the classifier and save
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("routes/absensi/classifier.xml")
 
    return redirect(url_for('Dashboard.addprsn'))

@Dashboard.route('/addprsn')
@login_required
def addprsn():
    cursor.execute("SELECT IFNULL(MAX(id_karyawan) + 1, 1) AS next_id FROM karyawan")
    row = cursor.fetchone()
    id = row[0]
    print(int(id))

    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    uname=admin[1]
 
    return render_template(
        title="Karyawan | Dashboard",
        template_name_or_list="addkar.html",
        new_id=int(id),
        admin=uname
    )
 
@Dashboard.route('/addprsn_submit', methods=['POST'])
@login_required
def addprsn_submit():
    id_kry = request.form.get('id_kry')
    nidn_nipy = request.form.get('nidn_nipy')
    nama_lgkp = request.form.get('nama_lgkp')
    jabatan = request.form.get('jabatan')
    jn_klm = request.form.get('jn_klm')
 
    cursor.execute("""INSERT INTO `karyawan` (`id_karyawan`, `nidn_nipy`, `nama_lengkap`, `jabatan`, `jenis_kelamin`) VALUES
                    ('{}', '{}', '{}', '{}', '{}')""".format(id_kry, nidn_nipy, nama_lgkp, jabatan, jn_klm))
    db.commit()
 
    # return redirect(url_for('home'))
    return redirect(url_for('Dashboard.vfdataset_page', id=id_kry))
 
@Dashboard.route('/vfdataset_page/<id>')
@login_required
def vfdataset_page(id):
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    uname=admin[1]

    return render_template(
        title="Training",
        template_name_or_list="gendataset.html",
        id=id,
        admin=uname
    )
 
@Dashboard.route('/vidfeed_dataset/<id>')
@login_required
def vidfeed_dataset(id):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(generate_dataset(id), mimetype='multipart/x-mixed-replace; boundary=frame')
