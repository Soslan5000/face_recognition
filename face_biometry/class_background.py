import cv2
import cvzone
from settings import WHITE


class Background:
    """Класс для работы с изображением"""

    background_path = r'resourses/background.png'  # Путь к изображению заднего фона

    def __init__(self):
        # Загрузим изображение из указанного файла и вернём его в переменную img_background в виде объекта numpy.ndarray
        # В матрице будет находиться значение каждого пикселя в формате BGR
        # Матрица имеет размер равный H*W*3 в виде [[[B, G, R], ..., [B, G, R]], ... [[B, G, R], ..., [B, G, R]]]
        self.img_background = cv2.imread(Background.background_path)

    def change_part_background(self, img, begin_x_pix, begin_y_pix):
        """Данная функция предназначена для замены части изображения на картинку img
        @param img - 3-мерный массив со значениями пикселей изображения
        @param begin_x_pix - левая координата x начала замены
        @param begin_y_pix - верхняя координата y начала замены"""

        part_height = img.shape[0]  # Высота картинки img
        part_width = img.shape[1]  # Ширина картинки img

        end_coord_x = begin_x_pix + part_width  # Правая координата x для замены
        end_coord_y = begin_y_pix + part_height  # Нижняя координата y для замены

        # Если нижняя координата y для замены выходит за границы img_background, то
        if self.img_background.shape[0] <= end_coord_y:
            # Нижнюю координату y для замены делаем равной последней координате y img_background
            end_coord_y = self.img_background.shape[0]

        # Если правая координата x для замены выходит за границы img_background, то
        if self.img_background.shape[1] <= end_coord_x:
            # Правую координату ч для замены делаем равной последней координате x img_background
            end_coord_x = self.img_background.shape[1]

        # Заменим кусок изображения img_background на изображение с нашей камеры заменой пикселей в данном куске на пиксели
        # нашего изображения
        self.img_background[begin_y_pix: end_coord_y, begin_x_pix: end_coord_x] = img[0:end_coord_y-begin_y_pix,
                                                                                      0:end_coord_x-begin_x_pix]

    def print_info_text_on_background(self, text, coord_left_bot, font=cv2.FONT_HERSHEY_COMPLEX, font_scale=1,
                                      color=WHITE, thickness=1):
        """Функция для вывода текста на экран
        @param text - текст, выводимый на экран
        @param coord_left_bot - координаты левой нижней границы текста на изображении
        @param font - шрифт
        @param font_scale - размер шрифта
        @param color - цвет шрифта RGB
        @param thickness - толщина шрифта"""

        cv2.putText(img=self.img_background,
                    text=str(text),
                    org=coord_left_bot,
                    fontFace=font,
                    fontScale=font_scale,
                    color=color,
                    thickness=thickness)

    def draw_rect_on_bg(self, bbox, thickness_corner=0):
        """Данная функция рисует прямоугольник
        @param bbox - кортеж с информацией о прямоугольнике (левая координата x, верхняя координата y, ширина и высота)
        @thickness_corner - толщина сторон прямоугольника"""

        self.img_background = cvzone.cornerRect(img=self.img_background, bbox=bbox, rt=thickness_corner)
