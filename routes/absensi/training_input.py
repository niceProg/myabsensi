from datetime import datetime
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

def generate_dataset(nbr):
    face_classifier = cv2.CascadeClassifier("routes/absensi/haarcascade_frontalface_default.xml")
 
    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        # scaling factor=1.3
        # Minimum neighbor = 5
 
        if faces is ():
            return None
        for (x, y, w, h) in faces:
            cropped_face = img[y:y + h, x:x + w]
        return cropped_face
 
    cap = cv2.VideoCapture(0)
 
    cursor.execute("select ifnull(max(id_dataset), 0) from dataset")
    row = cursor.fetchone()
    lastid = row[0]
 
    img_id = lastid
    max_imgid = img_id + 50
    count_img = 0
 
    while True:
        ret, img = cap.read()
        if face_cropped(img) is not None:
            count_img += 1
            img_id += 1
            face = cv2.resize(face_cropped(img), (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
 
            file_name_path = "dataset/"+nbr+"."+ str(img_id) + ".jpg"
            cv2.imwrite(file_name_path, face)
            cv2.putText(face, str(count_img), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
 
            cursor.execute("""INSERT INTO `dataset` (`id_dataset`, `id_karyawan`) VALUES
                                ('{}', '{}')""".format(img_id, nbr))
            db.commit()
 
            frame = cv2.imencode('.jpg', face)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
 
            if cv2.waitKey(1) == 13 or int(img_id) == int(max_imgid):
                break
                cap.release()
                cv2.destroyAllWindows()
