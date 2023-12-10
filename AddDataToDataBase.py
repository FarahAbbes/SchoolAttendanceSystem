import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://faceattendancerealtime-65539-default-rtdb.firebaseio.com/"
})
ref=db.reference('Students')
data={
    "854217":
        {
            "name":"Fguir Aziza",
            "major":"BIS",
            "Starting_year":2021,
            "Total_Attendence":6,
            "Standing":"G",
            "Year": 3,
            "Last_Attendence_time":"2021-11-12 00:54:33",
        },


    "542398":
        {
             "name": "Abbes Farah",
             "major": "BI",
             "Starting_year": 2020,
             "Total_Attendence": 8,
              "Standing": "G",
              "Year": 4,
              "Last_Attendence_time": "2021-11-12 00:54:33",
},
 "235968":
        {
             "name": "Elon Musk",
             "major": "Pysics",
             "Starting_year": 2018,
             "Total_Attendence": 7,
              "Standing": "B",
              "Year":6,
              "Last_Attendence_time": "2020-11-12 00:57:10",
}

}
for key, value in data.items():
    ref.child(key).set(value)