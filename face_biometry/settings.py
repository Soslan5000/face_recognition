from colors import WHITE, GRAY

cap_width = 640  # Ширина видео
cap_height = 480  # Высота видео

k_compression = 4  # Коэффициент сжатия изображения для обработки

# Параметр функции face_locations. Чем больше данный параметр, тем более мелкие лица будут распознаны
number_of_times_to_upsample_for_face_locations = 1

# Модель, при помощи которой происходит распознавание в face_locations.
# Доступны HOG и CNN. HOG быстрее, а CNN точнее
model_for_face_locations = "HOG"

# Параметр функции face_encodings. Чем большее значение, тем больше точность, но и длительность работы увеличивается
# прямо-пропорционально
num_jitters_for_face_encodings = 1

# Параметр функции compare_faces. Значение должно быть от 0 до 1. Чем меньше значение, тем большие требования к
# совпадению лиц. 0.6 - оптимальное значение
tolerance_for_compare_faces = 0.6

begin_y_for_video = 162  # номер пикселя по вертикали для начала замены (верхний левый угол) для видео
begin_x_for_video = 55  # номер пикселя по горизонтали для начала замены (верхний левый угол) для видео

begin_y_for_mode_pix = 44  # номер пикселя по горизонтали для начала замены (верхний левый угол) для рамки с инф-ей
begin_x_for_mode_pix = 808  # номер пикселя по вертикали для начала замены (верхний левый угол) для рамки с инф-ей

total_attendance_coord_on_bg = (861, 125)  # Координаты для вывода параметра total_attendance
total_attendance_font_scale = 1  # Величина шрифта
total_attendance_color = WHITE  # Цвет шрифта

major_coord_on_bg = (1006, 550)  # Координаты для вывода параметра major
major_font_scale = 0.5  # Величина шрифта
major_color = WHITE  # Цвет шрифта

student_id_coord_on_bg = (1006, 493)  # Координаты для вывода параметра student_id
student_id_font_scale = 0.5  # Величина шрифта
student_id_color = WHITE  # Цвет шрифта

standing_coord_on_bg = (910, 625)  # Координаты для вывода параметра standing
standing_font_scale = 0.6  # Величина шрифта
standing_color = GRAY  # Цвет шрифта

year_coord_on_bg = (1025, 625)  # Координаты для вывода параметра year
year_font_scale = 0.6  # Величина шрифта
year_color = GRAY  # Цвет шрифта

starting_year_coord_on_bg = (1125, 625)  # Координаты для вывода параметра starting_year
starting_year_scale = 0.6  # Величина шрифта
starting_year_color = GRAY  # Цвет шрифта

name_coord_on_bg = (886, 445)  # Координаты для вывода параметра name
name_font_scale = 1  # Величина шрифта
name_color = GRAY  # Цвет шрифта

begin_x_for_photo = 909  # номер пикселя по горизонтали для начала замены (верхний левый угол) для фото
begin_y_for_photo = 175  # номер пикселя по вертикали для начала замены (верхний левый угол) для фото
