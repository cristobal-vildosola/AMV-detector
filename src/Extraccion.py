import os
import re
import time
from typing import Tuple

import cv2
import numpy


def abrir_video(archivo: str) -> cv2.VideoCapture:
    """
    Abre un video en el formato de opencv.

    :param archivo: nombre del video
    :return: una captura de cv2
    """
    if not os.path.isfile(archivo):
        raise Exception(f'el archivo {archivo} no existe')

    capture = cv2.VideoCapture(archivo)
    if not capture.isOpened():
        raise Exception(f'no se pudo abrir el video {archivo}')

    return capture


def extraer_caracteristicas(imagen, tamano: Tuple[int, int] = (10, 10)) -> numpy.matrix:
    """
    Extrae caracteristicas de una imagen, reduciendo la dimensión de la imagen al tamaño especificado.

    :param imagen: la imagen de la cuál extraer características, en el formato de cv2 (una matriz)
    :param tamano: el tamaño al cual reducir la dimension de la imagen.

    :return: un vector de caracteristicas correspondiente a la matriz "aplanada".
    """

    # vector de caracteristicas
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    caracteristicas = cv2.resize(imagen_gris, dsize=(tamano[1], tamano[0]), interpolation=cv2.INTER_AREA)

    return caracteristicas.flatten()


def caracteristicas_video(archivo: str, carpeta_log: str, fps_extraccion: int = 6,
                          tamano: Tuple[int, int] = (10, 10)):
    """
    Extrae la caracteristicas de un video y las guarda en un archivo con el mismo nombre del video,
    dentro de la carpeta log. Mide el tiempo que tomó la extracción y la imprime.

    :param archivo: archivo del video.
    :param carpeta_log: carpeta donde guardar las características.
    :param fps_extraccion: número de frames por segundo a extraer.
    :param tamano: el tamaño del mapa al cual reducir la dimension de la imagen.
    """
    # medir tiempo
    t0 = time.time()

    # abrir video
    try:
        video = abrir_video(archivo)
    except:
        return

    # abrir log
    nombre = re.split('[/.]', archivo)[-2]

    if not os.path.isdir(carpeta_log):
        os.mkdir(carpeta_log)
    log = open(f'{carpeta_log}/{nombre}.txt', 'w')

    frame_n = 0  # número de frames
    fps = video.get(cv2.CAP_PROP_FPS)  # frames por segundo (para calcular tiempo)
    salto_frames = round(fps / fps_extraccion)  # frames a saltar

    print(f'extrayendo caracteristicas de video {nombre} ({fps:.2f} FPS)')

    while video.grab():

        # obtener solo 1 de cada n frames
        frame_n += 1
        if frame_n % salto_frames != 0:
            continue

        # sacar frame y asegurarse de que no hay errores
        retval, frame = video.retrieve()
        if not retval:
            continue

        # extraer caracteristicas y guardar en el archivo
        vector = extraer_caracteristicas(frame, tamano=tamano)
        log.write('{} {}\n'.format('%.3f' % (frame_n / fps), ' '.join(vector.astype(str))))

    log.close()
    video.release()
    print(f'la extracción de {int(frame_n / fps)} segundos de video tomo {int(time.time() - t0)} segundos')

    return


def caracteristicas_videos(carpeta: str, fps_extraccion: int = 6,
                           tamano: Tuple[int, int] = (10, 10)):
    """
    Extrae las caracteristicas de todos los archivos dentro de la carpeta especificada
    y los guarda en una nueva carpeta.

    :param carpeta: la carpeta desde la cuál obtener todos los videos.
    :param fps_extraccion: número de frames por segundo a extraer.
    :param tamano: el tamaño del mapa al cual reducir la dimension de cada frame.
    """

    # obtener todos los archivos en la carpeta
    videos = os.listdir(carpeta)

    # extraer la caracteristicas de cada comercial
    for video in videos:
        if video.endswith('.mp4'):
            caracteristicas_video(f'{carpeta}/{video}', f'{carpeta}_car_{tamano}_{fps_extraccion}',
                                  fps_extraccion=fps_extraccion, tamano=tamano)

    return


def main(fps_extraccion, tamano):
    """
    Extrae las caracteristicas de todos los capítulos de Naruto Shippuden.

    :param fps_extraccion: número de frames por segundo a extraer.
    :param tamano: el tamaño del mapa al cual reducir la dimension de cada frame.
    """

    caracteristicas_videos('../videos/AMV', fps_extraccion, tamano)
    # caracteristicas_videos('../videos/Shippuden', fps_extraccion, tamano)
    return


if __name__ == '__main__':
    main(fps_extraccion=6, tamano=(10, 10))
