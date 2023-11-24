import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Соединение с google-данными через json-файл с необходимой информацией
certificate_path = "serviceAccountKey.json"
cred = credentials.Certificate(certificate_path)

# Создаём экземпляр приложения
firebase_admin.initialize_app(
    cred,
    {
        'databaseURL': 'Сюда вставить ссыль на DATABASEREALTIME'
    }
)

# reference возвращает ссылку на базу данных по указанному пути в Firebase_realtime
ref = db.reference('Students')

# Данные для записи в формате json-данных
data = {
    "11111":
        {
            "name": "Dzutsev Soslan",
            "major": "Programmer",
            "starting_year": 2018,
            "total_attendance": 5,
            "standing": "G",
            "year": 23,
            "last_attendance_time": "2022-12-11 00:54:34"
        },

    "321654":
        {
            "name": "Murtaza Hassan",
            "major": "Robotics",
            "starting_year": 2017,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },

    "852741":
        {
            "name": "Emly Blunt",
            "major": "Economics",
            "starting_year": 2021,
            "total_attendance": 12,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        },

    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 7,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}

# Записываем данные по ссылке ref в базу данных, где
# каждому дочернему узлу key сопоставляется значение value
# Для наших данных каждом id сопоставляется свой набор данных и записывается в базу данных
# При этом, если дочерний узел уже существует и имеет какое-то значение, то он перезаписывается
for key, value in data.items():
    ref.child(key).set(value)
