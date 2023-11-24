import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
import cv2


class Firebase:
    """Класс, через который осуществляется взаимодействие с базой данных google.firebase
    Сcылка https://firebase.google.com/"""

    certificate_path = "serviceAccountKey.json"  # Путь до json файла с информацией для соединения
    # Словарь со значениями ссылок на соответствующие базы данных. Эти ключи необходимо копировать на сайте
    # databaseURL - ссылка на Realtime Database
    # storageBucket - ссылка на Storage
    # Также допустимы ключи projectId, databaseAuthVariableOverride, serviceAccountId, httpTimeout
    # Читайте в документации к firebase_admin.initialize_app
    app_options = {
        'databaseURL': 'СЮДА ВСТАВИТЬ ССЫЛЬ НА DATABASEREALTIME',
        'storageBucket': 'СЮДА ВСТАВИТЬ ССЫЛЬ НА STORAGE'
    }

    real_time_db_dir = 'Students/'  # Путь к таблице с информацией о людях в БД
    imges_db_dir = 'imges/'  # Путь к картинкам с людьми в БД

    last_attendance_time_key = 'last_attendance_time'  # Название поля с информацией о времени последней маркировки
    year_key = 'year'  # Название поля с информацией о годе рождения
    standing_key = 'standing'  # Название поля с информацией о профессии
    total_attendance_key = 'total_attendance'  # Название поля с информацией о количестве маркировок
    starting_year_key = 'starting_year'  # Название поля с информацией о годе поступления
    major_key = 'major'  # Название поля с информацией о статусе
    name_key = 'name'  # Название поля с информацией об имени

    def __init__(self):
        # Соединение с google-данными через json-файл с необходимой информацией
        self.cred = credentials.Certificate(Firebase.certificate_path)

        # Создаём экземпляр приложения (про параметр options читайте в документации)
        firebase_admin.initialize_app(
            credential=self.cred,
            options=Firebase.app_options
        )

        # Создаём переменную взаимодействия с Google Cloud Storage
        self.bucket = storage.bucket()

    def get_student_info(self, student_id):
        """Данная функция возвращает информацию о пользователе по его student_id в виде словаря"""

        return db.reference(f'{Firebase.real_time_db_dir}{student_id}').get()

    def get_student_image(self, student_id):
        """Данная функция возвращает фотографию пользователя по его student_id"""

        blob = self.bucket.get_blob(f'{Firebase.imges_db_dir}{student_id}.png')
        array = np.frombuffer(blob.download_as_string(), np.uint8)
        return cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

    def get_reference(self, student_id):
        """Данная функция возвращает соединение с Realtime Database с
        определённым студентом из базы по его student_id,
        через которое осуществляется взаимодействие с информацией о нём"""

        return db.reference(f'{Firebase.real_time_db_dir}{student_id}')

    def set_child(self, ref, child_name, value):
        """Данная функция устанавливает для поля child_name значение value в рамках соединения ref
        @param ref - соединение, получаемое из метода get_reference с информацией о пользователе из БД
        @param child_name - Название поля для замены
        @param value - Значение, устанавливаемое для поля child_name в БД"""
        ref.child(child_name).set(value)
