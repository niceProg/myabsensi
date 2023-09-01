from flask import Blueprint, render_template, session, redirect, url_for
from flask import make_response, request, flash, Response, jsonify, json
from flask import current_app as app
from routes.auth import login_required, user_required
from routes.absensi.recognize_masuk import recognize_masuk
from routes.absensi.recognize_pulang import recognize_pulang
import mysql.connector
from datetime import datetime, timedelta

User = Blueprint (
    name='User',
    import_name=__name__,
    url_prefix='/user',
    template_folder='../../templates/user'
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="myabsensi"
    )

@User.route('/')
@user_required
@login_required
def index():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    user_id = session['user_id']
    print(user_id)
    mycursor.execute("SELECT * FROM karyawan WHERE id_karyawan = %s", (user_id,))
    karyawan = mycursor.fetchone()
    print(karyawan)
    if karyawan:
        nama_karyawan = karyawan[1]
    else:
        nama_karyawan = None

    # Mendapatkan role dari session
    role = session['role']

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    return render_template (
        title="Karyawan",
        template_name_or_list='home_user.html',
        nama=nama_karyawan,
        role=role
    )

@User.route('/absensi/check_for_notification/<id_karyawan>')
@user_required
@login_required
def check_for_notification(id_karyawan):
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    today_date = datetime.now().date()
    ten_minutes_ago_time = (datetime.now() - timedelta(minutes=10)).time()
    
    # Menggunakan tanggal dan waktu untuk memfilter hasil
    mycursor.execute("SELECT * FROM absen_masuk WHERE karyawan_id = %s AND waktu = %s AND waktu_masuk > %s", (id_karyawan, today_date, ten_minutes_ago_time))
    recent_absen = mycursor.fetchone()

    if recent_absen:
        # Jika ada catatan absen dalam 10 menit terakhir
        return jsonify({
            "showNotification": True,
            "title": "Anda telah absen",
            "text": "Terima kasih!"
        })
    else:
        return jsonify({
            "showNotification": False
        })

@User.route('/absensi')
@user_required
@login_required
def absensi():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    user_id = session['user_id']
    print(user_id)
    mycursor.execute("SELECT * FROM karyawan WHERE id_karyawan = %s", (user_id,))
    karyawan = mycursor.fetchone()
    print(karyawan)
    if karyawan:
        nama_karyawan = karyawan[1]
    else:
        nama_karyawan = None

    # Mendapatkan role dari session
    role = session['role']

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    return render_template(
        title="Absensi | My Absensi",
        template_name_or_list="absen_kehadiran.html",
        nama=nama_karyawan,
        role=role,
        id_karyawan=user_id
    )

@User.route("/masuk")
@user_required
@login_required
def recog_masuk():
    response = recognize_masuk()
    if response == "redirect_required":
        return redirect(url_for('User.absensi'))
    
    return Response(
        response, 
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@User.route("/pulang")
@user_required
@login_required
def recog_pulang():
    return Response(
        recognize_pulang(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@User.route('/absenterbaru')
def absen_terbaru():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    # SQL untuk menghitung jumlah total absensi masuk dan pulang untuk hari ini.
    mycursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM absen_masuk WHERE DATE(waktu_masuk) = CURDATE()) AS masuk_count,
            (SELECT COUNT(*) FROM absen_pulang WHERE DATE(waktu_pulang) = CURDATE()) AS pulang_count
    """)
    
    count_masuk, count_pulang = mycursor.fetchone()

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    return jsonify({"countMasukToday": count_masuk, "countPulangToday": count_pulang})

@User.route('/absenload')
def loadData():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    # SQL untuk mengambil detail absensi masuk dan pulang untuk setiap karyawan pada hari ini.
    mycursor.execute("""
        SELECT 
            COALESCE(a.karyawan_id, c.karyawan_id) AS karyawan_id,
            b.nama_lengkap, 
            b.jabatan, 
            DATE_FORMAT(a.waktu_masuk, '%H:%i') AS waktu_masuk,
            CASE 
                WHEN c.waktu_pulang IS NULL THEN 'Belum absen'
                ELSE DATE_FORMAT(c.waktu_pulang, '%H:%i')
            END AS waktu_pulang,
            GREATEST(COALESCE(a.waktu_masuk, '2000-01-01'), COALESCE(c.waktu_pulang, '2000-01-01')) AS waktu_terbaru
        FROM 
            absen_masuk a
        LEFT JOIN 
            karyawan b ON a.karyawan_id = b.id_karyawan
        LEFT JOIN 
            absen_pulang c ON a.karyawan_id = c.karyawan_id AND DATE(a.waktu_masuk) = DATE(c.waktu_pulang)
        UNION
        SELECT 
            COALESCE(a.karyawan_id, c.karyawan_id) AS karyawan_id,
            b.nama_lengkap, 
            b.jabatan, 
            DATE_FORMAT(a.waktu_masuk, '%H:%i') AS waktu_masuk,
            CASE 
                WHEN c.waktu_pulang IS NULL THEN 'belum absen'
                ELSE DATE_FORMAT(c.waktu_pulang, '%H:%i')
            END AS waktu_pulang,
            GREATEST(COALESCE(a.waktu_masuk, '2000-01-01'), COALESCE(c.waktu_pulang, '2000-01-01')) AS waktu_terbaru
        FROM 
            absen_pulang c
        LEFT JOIN 
            karyawan b ON c.karyawan_id = b.id_karyawan
        LEFT JOIN 
            absen_masuk a ON c.karyawan_id = a.karyawan_id AND DATE(c.waktu_pulang) = DATE(a.waktu_masuk)
        WHERE 
            DATE(a.waktu_masuk) = CURDATE() OR DATE(c.waktu_pulang) = CURDATE()
        ORDER BY 
            waktu_terbaru DESC
        LIMIT 1
    """)

    data = mycursor.fetchall()

    # Menutup koneksi
    mycursor.close()
    mydb.close()

    return jsonify({"dataHariIni": data})