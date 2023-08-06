from datetime import datetime
from flask import Response
import face_recognition
import cv2
import pickle
import mysql.connector
import time
from datetime import date

db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='myabsensi'
    )
cursor = db.cursor()

cnt = 0
pause_cnt = 0
justscanned = False

def recognize_pulang():  # generate frame by frame from camera
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)
 
        global justscanned
        global pause_cnt
 
        pause_cnt += 1
 
        coords = []
 
        for (x, y, w, h) in features:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            id, pred = clf.predict(gray_image[y:y + h, x:x + w])
            confidence = int(100 * (1 - pred / 300))
 
            if confidence > 70 and not justscanned:
                global cnt
                cnt += 1
 
                n = (100 / 30) * cnt
                # w_filled = (n / 100) * w
                w_filled = (cnt / 30) * w
 
                cv2.putText(img, str(int(n))+' %', (x + 20, y + h + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (153, 255, 255), 2, cv2.LINE_AA)
 
                cv2.rectangle(img, (x, y + h + 40), (x + w, y + h + 50), color, 2)
                cv2.rectangle(img, (x, y + h + 40), (x + int(w_filled), y + h + 50), (153, 255, 255), cv2.FILLED)
 
                cursor.execute("SELECT a.id_karyawan, b.nama_lengkap, b.jabatan "
                                "FROM dataset a "
                                "LEFT JOIN karyawan b ON a.id_karyawan = b.id_karyawan "
                                "WHERE a.id_dataset = " + str(id))
                row = cursor.fetchone()
                if row is None:
                    print(row)
                    print("No data found for this id")
                else:
                    print(row)
                    idkry = row[0]
                    nama = row[1]
                    jabatan = row[2]
 
                if int(cnt) == 30:
                    cnt = 0

                    try:
                        cursor.execute("SELECT * FROM absen_pulang WHERE karyawan_id = %s AND waktu = %s", (idkry, str(date.today())))
                    except NameError:
                        print("idkry is not defined")

                    # cursor.execute("SELECT * FROM absen_pulang WHERE karyawan_id = %s AND waktu = %s", (idkry, str(date.today())))
                    existing_attendance = cursor.fetchone()

                    if existing_attendance is None:
                        cursor.execute("insert into absen_pulang (waktu, karyawan_id) values('"+str(date.today())+"', '" + str(idkry) + "')")
                        db.commit()
 
                        cv2.putText(img, nama + ' | ' + jabatan, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (153, 255, 255), 2, cv2.LINE_AA)
                        time.sleep(1)
    
                        justscanned = True
                        pause_cnt = 0
                        
                    else:
                        cv2.putText(img, 'Anda telah absen', (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
 
            else:
                if not justscanned:
                    cv2.putText(img, 'UNKNOWN', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
 
                if pause_cnt > 80:
                    justscanned = False
 
            coords = [x, y, w, h]
        return coords
 
    def recognize(img, clf, faceCascade):
        global face_detected
        face_detected = True

        coords = draw_boundary(img, faceCascade, 1.1, 10, (255, 255, 0), "Face", clf)
        return img
 
    faceCascade = cv2.CascadeClassifier("routes/absensi/haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("routes/absensi/classifier.xml")
 
    wCam, hCam = 400, 400
 
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
 
    while True:
        ret, img = cap.read()
        img = recognize(img, clf, faceCascade)
 
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
 
        key = cv2.waitKey(1)
        if key == 27:
            db.close
            break

    