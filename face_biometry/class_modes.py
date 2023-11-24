import face_recognition
import numpy as np
from datetime import datetime
from settings import k_compression, tolerance_for_compare_faces, begin_x_for_video, begin_y_for_video, \
    begin_x_for_mode_pix, begin_y_for_mode_pix, begin_y_for_photo, begin_x_for_photo, name_coord_on_bg, \
    year_coord_on_bg, major_coord_on_bg, standing_coord_on_bg, starting_year_coord_on_bg, student_id_coord_on_bg, \
    total_attendance_coord_on_bg, standing_color, student_id_color, starting_year_color, starting_year_scale, \
    standing_font_scale, student_id_font_scale, major_font_scale, year_font_scale, name_font_scale, \
    total_attendance_font_scale, name_color, year_color, major_color, total_attendance_color
from class_firebase import Firebase


class Modes:
    """Данный класс предназначен для вывода необходимой информации в окошке справа на изображении и смене режимов
    вывода информации"""

    mode_0 = 0  # Метка для 0-го режима (Режим поиска лица на видео)
    mode_1 = 1  # Метка для 1-го режима (Режим вывода информации для распознанного человека)
    mode_2 = 2  # Метка для 2-го режима (Режим вывода информации о том, что пользователь был промаркирован)
    mode_3 = 3  # Метка для 3-го режима (Режим вывода информации о том, что пользователь уже был промаркирован)
    max_seconds_ellapsed = 30  # Количество секунд до следующей допустимой маркировки человека
    mode_1_duration = 10  # Количество секунд, которое выводится информация о распознанном человеке
    mode_2_duration = 10  # Количество секунд, которое выводится информация о том, что человек был промаркирован

    def __init__(self):
        self.__count = 0  # Вспомогательный счётчик для переключения режимов
        self.mode_type = Modes.mode_0  # Вспомогательная переменная для выбора картинки из папки Modes в пределах режима
        self.mode_time_begin = 0  # Вспомогательная переменная для фиксации начала 1-го и 2-го режимов

    def action_for_face_current(self, face_current_frame, encode_current_frame, encode_list_known, background,
                                ids_list, firebase, img_mode_list):
        """В данной функции происходит запуск необходимых функций в зависимости от значений счётчика и режима
        @param face_current_frame Список кортежей с найденными лицами на изображении (верх, право, низ, лево)
        @param encode_current_frame Список 128-мерной расшифровки одного из лиц, найденных на изображении
        @param encode_list_known Список со 128-мерными расшифровками знакомых лиц
        @param background объект класса Background
        @param ids_list список id пользователей, где каждый id соответствует расшифровке в encode_list_known
        @param firebase объект класса Firebase
        @param img_mode_list список изображений лиц, людей"""

        if face_current_frame:  # Если в списке face_current_frame есть распознанные лица, то
            # Вызовем функцию, которая выделит знакомое лицо на видео прямоугольником и выдаст информацию о нём
            # в виде student_id, которое затем используем для запроса изображения человека и изменения его данных в базе
            # и словаря student_info, который затем используем для прикрепления информации о распознанном человеке
            # на изображении. Также счётчик self.__count станет равен 1,
            # а self.mode_type = mode_0, если self.__count был равен 0
            student_id, student_info = self.begin_action(face_current_frame=face_current_frame,
                                                         encode_current_frame=encode_current_frame,
                                                         encode_list_known=encode_list_known,
                                                         background=background,
                                                         ids_list=ids_list,
                                                         firebase=firebase)

            # Если счётчик не равен 0 (лицо распознано) и информация о нём найдена, то
            if self.__count != 0 and student_id is not None:
                # Если счётчик равен 1, то
                if self.__count == 1:
                    # В данной функции обнулим счётчик, если человек был распознан меньше, чем max_seconds_ellapsed
                    # секунд назад, устанавливаем self.mode_type в режим 3 и выводим пользователю информацию о том, что
                    # он отмаркирован, а иначе, увеличим total_attendance пользователя на 1, обновим время маркировки
                    # last_attendance_time на текущее и внесём обновления в базу данных, при этом self.mode_type
                    # перейдёт в режим mode_1
                    self.marked_or_unmarked_action(firebase=firebase,
                                                   student_id=student_id,
                                                   background=background,
                                                   img_mode_list=img_mode_list,
                                                   student_info=student_info)

                # Если mode_type не является 3-им режимом, то
                if self.mode_type != Modes.mode_3:

                    # Фиксируем время, когда это условие запустилось первый раз за последнее время
                    if self.mode_time_begin == 0:
                        self.mode_time_begin = datetime.now() # Устанавливаем время первого запуска равным текущему времени

                    # Рассчитываем в секундах, сколько прошло времени после первого запуска условия
                    duration = (datetime.now() - self.mode_time_begin).total_seconds()

                    # Если прошло времени меньше, чем должен работать первый режим, то
                    if duration <= self.mode_1_duration:
                        # Активируем первый режим
                        self.activate_mode_1(background=background,
                                             img_mode_list=img_mode_list,
                                             student_info=student_info,
                                             firebase=firebase,
                                             student_id=student_id)

                    # Если прошло времени больше, чем должен работать первый режим, но меньше, чем второй, то
                    elif duration <= self.mode_1_duration + self.mode_2_duration:
                        # Активируем второй режим
                        self.activate_mode_2(background=background,
                                             img_mode_list=img_mode_list)

                    # Если время работы двух режимов превысило все лимиты, то обнуляем время mode_time_begin и счётчик
                    # __count, чтобы всё либо повторилось заново, если пользователь будет всё ещё в кадре
                    else:
                        self.mode_time_begin = 0
                        self.__count = 0

            # Увеличиваем каждый раз счётчик на 1, чтобы функция marked_or_unmarked_action не запускалась повторно
            self.__count += 1

        # Иначе если знакомое лицо не было обнаружено, обнуляем все счётчики и устанавливаем режим mode_0
        else:
            self.mode_time_begin = 0
            self.mode_type = Modes.mode_0
            self.__count = 0

    def begin_action(self, face_current_frame, encode_current_frame, encode_list_known, background, ids_list, firebase):
        """Данная функция обнаруживает лицо на изображении и сравнивает его со знакомыми лицами.
        Если лицо найдено среди знакомых, возвращает его id и информацию о нём, а также изменяет значения счётчиков"""

        # Проходимся по всем face_location и encode_face в списках face_current_frame и encode_current_frame
        for face_location, encode_face in zip(face_current_frame, encode_current_frame):
            # Метод compare_faces используется для сравнения двух лиц на схожесть
            # - known_face_encodings - список известных кодировок лиц для сравнения
            # - face_encoding_to_check - текущая кодировка лица для сравнения с известными лицами
            # - tolerance - степень точности распознавания
            # Метод возвращает список булевых значений,
            # где каждое значение указывает на схожесть соответствующего лица
            # в known_face_encodings с face_encoding_to_compare.
            # Лицо считается схожим, когда расстояние векторов признаков между ними меньше либо равно tolerance
            matches = face_recognition.compare_faces(known_face_encodings=encode_list_known,
                                                     face_encoding_to_check=encode_face,
                                                     tolerance=tolerance_for_compare_faces)

            # Метод face_distance используется для вычисления "расстояния" между лицами на основе их кодировок в 128-мерном пространстве.
            # Это расстояние показывает степень различия между двумя лицами. Чем меньше значение, тем более схожи лица.
            # - face_encodings: Список кодировок (encoding) лиц, для которых нужно вычислить расстояние.
            # - face_to_compare: Кодировка (encoding) лица, с которым сравниваются кодировки в face_encodings
            # Метод возвращает массив чисел, представляющих расстояние между лицами от 0 до 1.
            # Если расстояние близко к 0, это означает, что лица более схожи, в противном случае расстояние будет больше вплоть до 1.
            face_distance = face_recognition.face_distance(face_encodings=encode_list_known,
                                                           face_to_compare=encode_face)

            match_index = np.argmin(face_distance)  # Находим индекс минимального значение дистанции в полученном списке

            # Выделение знакомого лица прямоугольником
            if matches[match_index]:  # Если данному значению дистанции соответствует True (лицо найдено), то
                y1, x2, y2, x1 = [k_compression * num for num in face_location]  # Получаем координаты нашего лица до сжатия

                # Положение Bounding box определяется координатами левого нижнего угла, шириной и высотой
                bbox = begin_x_for_video + x1, begin_y_for_video + y1, x2 - x1, y2 - y1

                # cornerRect рисует на изображении img_background прямоугольник с параметрами bbox
                # rt - толщина прямоугольника без угловых линий. Чтобы оставить только угловые линии, устанавливаем rt=0
                background.draw_rect_on_bg(bbox=bbox)

                student_id = ids_list[match_index]  # id найденного человека
                student_info = firebase.get_student_info(student_id=student_id)  # Информация о найденном человеке

                if self.__count == 0:  # Если счётчик равен 0, то
                    self.__count = 1  # Установим его в режим 1, чтобы лицо считалось распознанным

                return student_id, student_info # Вернём id человека и информацию о нём

        return None, None  # Если информация не была найдена, то вернём None, None

    def marked_or_unmarked_action(self, firebase, student_id, background, img_mode_list, student_info):
        """Данная функция выводит информацию о том, что пользователь уже был отмаркирован в ближайшее время
        или маркирует пользователя в зависимости от того, когда была произведена последняя маркировка"""

        # Из словаря с информацией о человеке, достаём, время, когда он последний раз был промаркирован
        # и превращаем данное значение в объект datetime
        datetime_obj = datetime.strptime(student_info[Firebase.last_attendance_time_key],
                                         '%Y-%m-%d %H:%M:%S')

        # Рассчитываем количество секунд, пройденных от момента последней маркировки до текущего момента
        seconds_ellapsed = (datetime.now() - datetime_obj).total_seconds()

        if seconds_ellapsed >= Modes.max_seconds_ellapsed:  # Если время больше определённого лимита, то
            # Устанавливаем соединение с информацией о пользователе по student_id в базе данных
            ref = firebase.get_reference(student_id=student_id)
            # Увеличиваем значение total_attendance_key в словаре student_info на 1, который соответствует
            # количеству распознаваний пользователя
            student_info[Firebase.total_attendance_key] += 1
            # Обновляем значение total_attendance в базе данных
            firebase.set_child(ref=ref,
                               child_name=Firebase.total_attendance_key,
                               value=student_info[Firebase.total_attendance_key])
            # Обновляем поле last_attendance_time, соответствующее времени последней маркировки на текущее
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            firebase.set_child(ref=ref,
                               child_name=Firebase.last_attendance_time_key,
                               value=now)
            student_info[Firebase.last_attendance_time_key] = datetime.now()  # Обновляем информацию в словаре

            self.mode_type = Modes.mode_0  # Устанавливаем режим в положение mode_0
        else:  # Иначе, если ещё не прошло достаточно времени с последней маркировки
            self.mode_type = Modes.mode_3  # Устанавливаем режим в положение mode_3
            self.__count = 0  # Обнуляем счётчик
            # Выводим информацию о том, что пользователь отмаркирован на изображение
            background.change_part_background(img=img_mode_list[self.mode_type],
                                              begin_x_pix=begin_x_for_mode_pix,
                                              begin_y_pix=begin_y_for_mode_pix)
        return student_info  # Возвращаем обновлённую информацию о пользователе

    def activate_mode_2(self, background, img_mode_list):
        """Данная функция выводит информацию о том, что пользователь был успешно отмаркирован"""
        self.mode_type = Modes.mode_2  # Устанавливаем режим в положение mode_2
        # Выдаём информацию о том, что пользователь был отмаркирован
        background.change_part_background(img=img_mode_list[self.mode_type],
                                          begin_x_pix=begin_x_for_mode_pix,
                                          begin_y_pix=begin_y_for_mode_pix)

    def activate_mode_1(self, background, img_mode_list, student_info, firebase, student_id):
        """Данная функция выводит информацию о пользователе, который был распознан"""

        self.mode_type = Modes.mode_1  # Устанавливаем режим в положение mode_1

        # Выводим шаблон рамки, поверх которой затем будет выведена информация о пользователе
        background.change_part_background(img=img_mode_list[self.mode_type],
                                          begin_x_pix=begin_x_for_mode_pix,
                                          begin_y_pix=begin_y_for_mode_pix)

        # Выводим информацию о количестве предыдущих маркировок в углу рамки
        background.print_info_text_on_background(text=student_info[Firebase.total_attendance_key],
                                                 coord_left_bot=total_attendance_coord_on_bg,
                                                 font_scale=total_attendance_font_scale,
                                                 color=total_attendance_color)

        # Выводим информацию о профессии пользователя
        background.print_info_text_on_background(text=student_info[Firebase.major_key],
                                                 coord_left_bot=major_coord_on_bg,
                                                 font_scale=major_font_scale,
                                                 color=major_color)

        # Выводим id пользователя
        background.print_info_text_on_background(text=student_id,
                                                 coord_left_bot=student_id_coord_on_bg,
                                                 font_scale=student_id_font_scale,
                                                 color=student_id_color)

        # Выводим статус
        background.print_info_text_on_background(text=student_info[Firebase.standing_key],
                                                 coord_left_bot=standing_coord_on_bg,
                                                 font_scale=standing_font_scale,
                                                 color=standing_color)

        # Выводим количество полных лет пользователя
        background.print_info_text_on_background(text=student_info[Firebase.year_key],
                                                 coord_left_bot=year_coord_on_bg,
                                                 font_scale=year_font_scale,
                                                 color=year_color)

        # Выводим год поступления пользователя
        background.print_info_text_on_background(text=student_info[Firebase.starting_year_key],
                                                 coord_left_bot=starting_year_coord_on_bg,
                                                 font_scale=starting_year_scale,
                                                 color=starting_year_color)

        # Выводим имя пользователя
        background.print_info_text_on_background(text=student_info[Firebase.name_key],
                                                 coord_left_bot=name_coord_on_bg,
                                                 font_scale=name_font_scale,
                                                 color=name_color)

        # Из базы данных достаём фотографию пользователя по id
        img_student = firebase.get_student_image(student_id=student_id)

        # Выводим фотографию пользователя
        background.change_part_background(img=img_student,
                                          begin_x_pix=begin_x_for_photo,
                                          begin_y_pix=begin_y_for_photo)
