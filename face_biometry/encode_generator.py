import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Соединение с google-данными через json-файл с необходимой информацией
certificate_path = "serviceAccountKey.json"
cred = credentials.Certificate(certificate_path)

# Создаём экземпляр приложения (про параметр options читайте в документации)
firebase_admin.initialize_app(
    credential=cred,
    options={
             'databaseURL': 'СЮДА ВСТАВИТЬ ССЫЛЬ НА DATABASE REALTIME',
             'storageBucket': 'СЮДА ВСТАВИТЬ ССЫЛЬ НА STORAGE'
            }
)

# Импорт изображений из папки imges
folder_img_dir = 'imges'  # Путь к папке imges
img_path_list = os.listdir(folder_img_dir)  # Список с названиями файлов в папке imges
img_list = []  # В этот список будут помещены изображения в виде объектов numpy.ndarray
ids_list = []  # В этот список будут помещены id изображений по их названию
for p in img_path_list:  # Проходимся по списку с названиями файлов
    path = os.path.join(folder_img_dir, p)  # Формируем путь к файлам в папке imges
    img_list.append(cv2.imread(path))  # Добавляем изображения в список img_list в виде объектов numpy.ndarray
    ID = os.path.splitext(p)[0]  # Формируем id изображения по названию
    ids_list.append(ID)  # Добавляем id изображения в список ids_list

    file_name = f'{folder_img_dir}/{p}'  # Путь к изображению в БД
    bucket = storage.bucket()  # bucket для соединения и взаимодействия со STORAGE
    blob = bucket.blob(file_name)  # Соединение с путём в БД, куда будем добавлять изображение
    blob.upload_from_filename(file_name)  # Загружаем изображение в БД


def find_encodings(img_list):
    """
    Данная функция принимает на вход список матриц изображений и возвращает список со 128-мерными векторами признаков
    для лиц в каждом изображении
    """

    encode_list = []
    for img in img_list:
        # Преобразуем матрицу пикселей изображения из формата BGR в формат RGB (face_recognition работает только с RGB или L)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Преобразует человеческие лица на изображении img в 128-мерные векторы для каждого лица на изображении,
        # где изображения похожих лиц располагаются рядом друг с другом в 128-мерном пространстве признаков,
        # а изображения непохожих лиц далеко друг от друга
        # ссылка на файл модели http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2
        # Параметр num_jitters увеличивает точность распознавания, но увеличивает время работы (линейно)
        encode = face_recognition.face_encodings(img, num_jitters=10)[0]

        # Добавляем encode лиц на картинке в encode_list
        encode_list.append(encode)

    return encode_list


encode_list_known = find_encodings(img_list)  # Сохраняем, полученные из функции encod'ы лиц
encode_list_known_with_ids = [encode_list_known, ids_list]  # Записываем encod'ы лиц и их id в один список

with open('EncodeFile.p', 'wb') as f:  # Открываем файл EncodeFile.p для записи. Перед записью произойдёт очистка
    pickle.dump(encode_list_known_with_ids, f)  # Сохраняем список encode_list_known_with_ids в файл EncodeFile.p
