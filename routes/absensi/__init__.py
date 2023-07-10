from flask import Blueprint, render_template, session, Response
from flask import current_app as app
from flask import request, flash, redirect, url_for, jsonify
import mysql.connector
from flask_cors import CORS
import os
import cv2
from PIL import Image
import numpy as np
import logging
from functools import wraps
from routes.absensi.recognize_masuk import recognize_masuk
from routes.absensi.recognize_pulang import recognize_pulang

Absensi = Blueprint (
    name='Absensi',
    import_name=__name__,
    url_prefix='/absensi',
    template_folder='../../templates/'
)

db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="myabsensi"
    )
cursor = db.cursor()

# def gen(camera):
#     while True:
#         frame=camera.gen_frames()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@Absensi.route('/masuk')
def recog_masuk():
    return Response(recognize_masuk(),
    mimetype='multipart/x-mixed-replace; boundary=frame'
)
@Absensi.route('/pulang')
def recog_pulang():
    return Response(recognize_pulang(),
    mimetype='multipart/x-mixed-replace; boundary=frame'
)

@Absensi.route('/')
def absensi():
    cursor.execute("select a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, a.accs_added "
                     "  from accs_hist a "
                     "  left join prs_mstr b on a.accs_prsn = b.prs_nbr "
                     " where a.accs_date = curdate() "
                     " order by 1 desc")
    data = cursor.fetchall()

    

    return render_template(
        title="Absensi | My Absensi",
        template_name_or_list="absen.html",
        data=data
    )

# @Absensi.route('/check_attendance', methods=['GET'])
# def check_attendance():
#     attendance_detected = app.config['attendance_detected']

#     if attendance_detected:
#         return jsonify({'attendance_detected': True})

#     return jsonify({'attendance_detected': False})
    # if justscanned:
    #     performAction()

    # return jsonify({"attendance_detected": attendance_detected})

@Absensi.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    attendance_detected = app.config['attendance_detected']

    if not attendance_detected:
        app.config['attendance_detected'] = True

        cursor.execute("SELECT * FROM karyawan")
        row2 = cursor.fetchone()
        # print(row2)
        nama_lgkap = row2[1]
        jabatan2 = row2[2]
        nidn_nipy = row2[3]
        jkl = row2[4]

        data_karyawan = {
            'nama': nama_lgkap,
            'jabatan': jabatan2,
            'nidn_nipy': nidn_nipy,
            'jkl': jkl
        }

        return jsonify({
            'success': True,
            'data_karyawan': data_karyawan
        })
    
    return jsonify({'success': False,
                    'message': 'Karyawan sudah absen sebelumnya'})

@Absensi.route('/countTodayScan')
def countTodayScan():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="myabsensi"
    )
    cursor = mydb.cursor()
 
    cursor.execute("select count(*) "
                     "  from accs_hist "
                     " where accs_date = curdate() ")
    row = cursor.fetchone()
    rowcount = row[0]
 
    return jsonify({'rowcount': rowcount})

@Absensi.route('/loadData', methods = ['GET', 'POST'])
def loadData():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="myabsensi"
    )
    cursor = mydb.cursor()
 
    cursor.execute("select a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, date_format(a.accs_added, '%H:%i:%s') "
                     "  from accs_hist a "
                     "  left join prs_mstr b on a.accs_prsn = b.prs_nbr "
                     " where a.accs_date = curdate() "
                     " order by 1 desc")
    data = cursor.fetchall()
 
    return jsonify(response = data)

