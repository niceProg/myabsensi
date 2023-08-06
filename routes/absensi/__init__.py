from flask import Blueprint, render_template, session, Response
from flask import current_app as app
from flask import request, flash, redirect, url_for, jsonify
import mysql.connector
from flask_cors import CORS
import cv2
from PIL import Image
import numpy as np
import logging
from functools import wraps
from routes.absensi.recognize_masuk import recognize_masuk
from routes.absensi.recognize_pulang import recognize_pulang

Absensi = Blueprint(
    name="Absensi",
    import_name=__name__,
    url_prefix="/absensi",
    template_folder="../../templates/",
)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="myabsensi"
)
cursor = db.cursor()

@Absensi.route("/")
def absensi():
    return render_template(
        title="Absensi | My Absensi",
        template_name_or_list="absen.html"
    )

@Absensi.route("/masuk")
def recog_masuk():
    return Response(
        recognize_masuk(), 
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@Absensi.route("/pulang")
def recog_pulang():
    return Response(
        recognize_pulang(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# from flask import request

# @Absensi.route('/gps', methods=['POST'])
# def absen():
#     data = request.get_json()
#     user_lat = data['lat']
#     user_lon = data['lon']
#     # ...
#     recognize_masuk(user_lat, user_lon)

@Absensi.route("/latestRecordMasuk", methods=["GET"])
def latestRecordMasuk():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="myabsensi"
    )
    cursor = db.cursor()

    cursor.execute("""
        SELECT a.karyawan_id, b.nama_lengkap, b.jabatan, 
               IF(a.waktu_masuk IS NULL, 'Belum absen', DATE_FORMAT(a.waktu_masuk, '%H:%i')) AS waktu_masuk,
               IF(c.waktu_pulang IS NULL, 'Belum absen', DATE_FORMAT(c.waktu_pulang, '%H:%i')) AS waktu_pulang
        FROM absen_masuk a
        LEFT JOIN karyawan b ON a.karyawan_id = b.id_karyawan
        LEFT JOIN absen_pulang c ON a.karyawan_id = c.karyawan_id
        ORDER BY a.waktu_masuk DESC, b.id_karyawan DESC LIMIT 1
    """)
    data = cursor.fetchone()

    return jsonify({"latestRecordMasuk": data})

@Absensi.route("/latestRecordPulang", methods=["GET"])
def latestRecordPulang():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="myabsensi"
    )
    cursor = db.cursor()

    cursor.execute("""
        SELECT a.karyawan_id, b.nama_lengkap, b.jabatan, 
               IF(c.waktu_masuk IS NULL, 'Belum absen', DATE_FORMAT(c.waktu_masuk, '%H:%i')) AS waktu_masuk,
               IF(a.waktu_pulang IS NULL, 'Belum absen', DATE_FORMAT(a.waktu_pulang, '%H:%i')) AS waktu_pulang
        FROM absen_pulang a
        LEFT JOIN karyawan b ON a.karyawan_id = b.id_karyawan
        LEFT JOIN absen_masuk c ON a.karyawan_id = c.karyawan_id
        ORDER BY a.waktu_pulang DESC LIMIT 1
    """)
    data = cursor.fetchone()

    return jsonify({"latestRecordPulang": data})
