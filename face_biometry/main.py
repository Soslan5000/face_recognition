import os
import pickle
import cv2
import face_recognition
from settings import cap_width, cap_height, k_compression, begin_y_for_video, begin_x_for_video, \
    begin_x_for_mode_pix, begin_y_for_mode_pix, number_of_times_to_upsample_for_face_locations, \
    model_for_face_locations, num_jitters_for_face_encodings
from config import folder_mode_dir, encode_filename, window_name
from class_background import Background
from class_firebase import Firebase
from class_modes import Modes

firebase = Firebase()  # Создаём объект класса Firebase для взаимодействия с базой данных

modes = Modes()  # Создаём объект класса Modes. Через него будем менять правую рамку с информацией

cap = cv2.VideoCapture(0)  # Захват видео (параметр 0 указывает на номер камеры. В данном случае идёт захват основной)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)  # Устанавливаем ширину экрана
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)  # Устанавливаем высоту экрана

# Загрузим изображение из указанного файла и вернём его в переменную img_background в виде объекта numpy.ndarray
# В матрице будет находиться значение каждого пикселя в формате BGR
# Матрица имеет размер равный H*W*3 в виде [[[B, G, R], ..., [B, G, R]], ... [[B, G, R], ..., [B, G, R]]]
background = Background()

# Импорт изображений из папки Mode
mode_path_list = os.listdir(folder_mode_dir)  # Список с названиями файлов в папке Modes
img_mode_list = []  # В этот список будут помещены изображения в виде объектов numpy.ndarray
for p in mode_path_list:  # Проходимся по списку с названиями файлов
    path = os.path.join(folder_mode_dir, p)  # Формируем путь к файлам в папке Modes
    img_mode_list.append(cv2.imread(path))  # Добавляем изображения в список img_mode_list в виде объектов numpy.ndarray

# Загрузка файла с encod'ами лиц и их id
with open(encode_filename, 'rb') as f:
    encode_list_known_with_ids = pickle.load(f)
encode_list_known, ids_list = encode_list_known_with_ids

while True:  # Бесконечный цикл для бесконечного обновления
    # Захват кадра
    # success будет равен True, если кадр захвачен правильно
    # img получает изображение с камеры в виде объекта numpy.ndarray
    success, img = cap.read()

    # Произведём сжатие изображения
    # - В параметре src указываем изображение img, которое будет читаться с нашей камеры и которое мы хотим сжать
    # - Параметр dsize сжимает изображение до указанного размера и имеет приоритет. Если определить его, как None, то
    # он будет проигнорирован.
    # - Параметры fx и fy изменяют изображение в заданных пропорциях. В нашем случае уменьшение будет в 4 раза
    # от исходного
    # - interpolation - здесь указываем алгоритм интерполяции изображения. Для сжатия наилучшим является cv2.INTER_AREA
    # про различные алгоритмы интерполяции и разницу между ними можно почитать здесь
    # https://robocraft.ru/computervision/3956
    imgs = cv2.resize(src=img, dsize=None, fx=1 / k_compression, fy=1 / k_compression, interpolation=cv2.INTER_AREA)

    # Преобразуем матрицу пикселей изображения из формата BGR в формат RGB (face_recognition работает только с RGB или L)
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

    # Выполним обнаружение лиц на изображении
    # Параметры:
    # - img - изображение в формате массива numpy.ndarray
    # - number_of_times_to_upsample - параметр, указывающий, во сколько раз повысить дискретизацию изображения.
    # Увеличение этого параметра увеличивает точность обнаружения, но также увеличивает и время обработки
    # - model - Выбор алгоритма распознавания лиц между "HOG" (Histogram of Oriented Gradients)
    # и "CNN" (Convolutional Neural Networks). По умолчанию стоит HOG.
    # При этом HOG более быстрый, но менее точный, а CNN - наоборот. Выбор зависит от контекста задачи
    # возвращает список кортежей, каждый из которых представляет координаты ограничивающего прямоугольника
    # для обнаруженного лица на изображении.
    # Каждый кортеж содержит четыре значения: верх, право, низ и лево.
    # Эти значения представляют собой пиксельные координаты, указывающие на положение лица на изображении.
    face_current_frame = face_recognition.face_locations(img=imgs,
                                                         number_of_times_to_upsample=number_of_times_to_upsample_for_face_locations,
                                                         model=model_for_face_locations)

    # Преобразует человеческие лица на изображении img в 128-мерные векторы для каждого лица на изображении,
    # где изображения похожих лиц располагаются рядом друг с другом в 128-мерном пространстве признаков,
    # а изображения непохожих лиц далеко друг от друга
    # ссылка на файл модели http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2
    # Параметр num_jitters увеличивает точность распознавания, но увеличивает время работы (линейно)
    # Параметр known_face_locations принимает на вход координаты квадрата положения лица и ускоряет данный процесс
    encode_current_frame = face_recognition.face_encodings(face_image=imgs,
                                                           known_face_locations=face_current_frame,
                                                           num_jitters=num_jitters_for_face_encodings)

    # Заменим кусок изображения img_background на изображение с нашей камеры заменой пикселей в данном куске на пиксели
    # нашего изображения
    background.change_part_background(img=img,
                                      begin_x_pix=begin_x_for_video,
                                      begin_y_pix=begin_y_for_video)

    # Заменим кусок изображения img_background на изображение с режимом заменой пикселей в данном куске на пиксели
    # данного изображения
    background.change_part_background(img=img_mode_list[modes.mode_type],
                                      begin_x_pix=begin_x_for_mode_pix,
                                      begin_y_pix=begin_y_for_mode_pix)

    # Выведем информацию в рамочке справа в зависимости от того, какой пользователь был распознан и в какое время
    # Прочитайте документацию
    modes.action_for_face_current(face_current_frame=face_current_frame,
                                  encode_current_frame=encode_current_frame,
                                  encode_list_known=encode_list_known,
                                  background=background,
                                  ids_list=ids_list,
                                  firebase=firebase,
                                  img_mode_list=img_mode_list)

    cv2.imshow(winname=window_name,
               mat=background.img_background)  # Выводим полученное изображение на экран в окне с названием window_name

    # Показывает кадр в течение как минимум 1 мс
    cv2.waitKey(1)
