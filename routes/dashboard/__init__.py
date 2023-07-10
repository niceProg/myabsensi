from flask import Blueprint, render_template, session, redirect, url_for, make_response, request, flash, Response
from flask import current_app as app
from routes.auth import login_required
import mysql.connector
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

@Dashboard.route('/', endpoint='index')
@login_required
def index():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='myabsensi'
    )
    cursor = db.cursor()
    # cursor = get_db_cursor()
    user_id = session['user_id']

    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    username = cursor.fetchone()[0]

    cursor.execute("select prs_nbr, prs_name, prs_skill, prs_active, prs_added from prs_mstr")
    data = cursor.fetchall()

    if 'user_id' in session:
        user_id = session['user_id']
        print(session)
        return render_template (
            title="Dashboard",
            template_name_or_list='home.html',
            user_id=user_id,
            data=data
        )
        # return redirect(url_for('Dashboard.index', user_id=user_id))
    else:
        return redirect(url_for('Auth.login'))

@Dashboard.route('/daftarkaryawan')
@login_required
def daftarkaryawan():
    
    # cursor = db.cursor()

    cursor.execute("select prs_nbr, prs_name, prs_skill, prs_active, prs_added from prs_mstr")
    data = cursor.fetchall()

    return render_template (
        title="Daftar Karyawan | Dashboard",
        template_name_or_list='daftar_karyawan.html',
        data=data
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
    cursor.execute("select ifnull(max(id_karyawan) + 1, 1) from karyawan")
    row = cursor.fetchone()
    id = row[0]
    print(int(id))
 
    return render_template(
        title="Karyawan | Dashboard",
        template_name_or_list="addkar.html",
        new_id=int(id)
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
    return render_template(
        title="Training",
        template_name_or_list="gendataset.html",
        id=id
    )
 
@Dashboard.route('/vidfeed_dataset/<id>')
@login_required
def vidfeed_dataset(id):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(generate_dataset(id), mimetype='multipart/x-mixed-replace; boundary=frame')
