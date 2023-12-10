
import pickle
import face_recognition
import cv2
import os
import cvzone
import firebase_admin
from firebase_admin import credentials, initialize_app, storage, db
import numpy as np
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-65539-default-rtdb.firebaseio.com/",
    'storageBucket': "gs://faceattendancerealtime-65539.appspot.com"
})

bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('C:/Users/USER/Desktop/face-attendance-system-master/Resources/background.PNG')

folderModePath = 'Resources/Modes'  # Utilisez des barres obliques normales (/) pour le chemin
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

print("Loading Encode File..")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()


encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode file loaded..")
modeType = 1
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    imgBackground[165:165 + 480, 55:55 + 640] = img
    imgBackground[220:220 + 277, 870:870 + 307] = imgModeList[0]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print("matches", matches)
            print("face distances", faceDis)
            matchIndex = np.argmin(faceDis)
            print(" matchIndex", matchIndex)
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading..", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                #blob = bucket.get_blob(r'/C:\Users\USER\PycharmProjects\FaceRecognitionDS\Images/{id}.PNG')
                #blob = bucket.get_blob('Images/{id}.PNG')


                #array = np.frombuffer(blob.download_as_string(), np.uint8)
                #imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                datetimeObject = datetime.strptime(studentInfo['Last_Attendence_time'], "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondElapsed)

                if secondElapsed > 30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['Total_Attendence'] += 1
                        ref.child('Total_Attendence').set(studentInfo['Total_Attendence'])
                        ref.child('Last_Attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                        modeType = 3
                        counter = 0
                        imgBackground[120:120 + 500, 825:825 + 380] = imgModeList[3]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                    imgBackground[220:220 + 346, 870:870 + 228] = imgModeList[2]
                if counter <= 10:
                    imgBackground[56:56 + 647, 797:797 + 424] = imgModeList[1]
                    cv2.putText(imgBackground, str(studentInfo['Total_Attendence']), (861, 130),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 577),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 516),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Standing']), (910, 650),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['Year']), (1025, 650),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['Starting_year']), (1125, 650),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (424 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 460),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    # Ajoutez la vérification ici avant l'assignation
                    #if imgStudent:  # Vérifiez si la liste n'est pas vide
                    #imgBackground[175:175 + 235, 909:909 + 235] = imgStudent

                counter += 1
                if counter >= 20:
                    modeType = 0
                    counter = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[220:220 + 277, 870:870 + 307] = imgModeList[0]

    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)