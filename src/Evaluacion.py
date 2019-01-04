import threading

import cv2

from src.Extraccion import abrir_video


class Prediccion:
    def __init__(self, video: str, inicio_video: float, capitulo: str, inicio_cap: float, duracion: float):
        self.video = video
        self.inicio_video = inicio_video

        self.capitulo = capitulo
        self.inicio_cap = inicio_cap

        self.duracion = duracion

        self.correcta = False


class VideoThread(threading.Thread):
    def __init__(self, video: cv2.VideoCapture, nombre: str, tiempo: float, duracion: float):
        super().__init__()
        self.video = video
        self.nombre = nombre
        self.video.set(cv2.CAP_PROP_POS_MSEC, tiempo)
        self.duracion = duracion

    def run(self):
        fps = self.video.get(cv2.CAP_PROP_FPS)
        tiempo = 0
        espera_frame = int(1000 / fps)
        tiempo_frame = 1.0 / fps
        cv2.namedWindow(self.nombre)

        while tiempo < self.duracion and self.video.isOpened():
            ret, frame = self.video.read()

            frame = cv2.resize(frame, (640, 358))
            cv2.imshow(self.nombre, frame)

            cv2.waitKey(espera_frame)
            tiempo += tiempo_frame

        return


def comparar_videos(prediccion: Prediccion):
    amv = abrir_video(f'../videos/AMV/{prediccion.video}.mp4')
    cap = abrir_video(f'../videos/Shippuden/{prediccion.capitulo}.mp4')

    amv.set(cv2.CAP_PROP_POS_MSEC, prediccion.inicio_video * 1000)
    cap.set(cv2.CAP_PROP_POS_MSEC, prediccion.inicio_cap * 1000)

    fps1 = amv.get(cv2.CAP_PROP_FPS)
    fps2 = cap.get(cv2.CAP_PROP_FPS)
    tiempo = 0

    tiempo_frame1 = 1.0 / fps1
    tiempo_frame2 = 1.0 / fps2

    siguiente_frame1 = tiempo_frame1
    siguiente_frame2 = tiempo_frame2

    _, frame1 = amv.read()
    _, frame2 = cap.read()
    frame1 = cv2.resize(frame1, (640, 358))
    frame2 = cv2.resize(frame2, (640, 358))

    while tiempo < prediccion.duracion and amv.isOpened() and cap.isOpened():

        if tiempo > siguiente_frame1:
            siguiente_frame1 += tiempo_frame1
            _, frame1 = amv.read()
            frame1 = cv2.resize(frame1, (640, 358))

        if tiempo > siguiente_frame2:
            siguiente_frame2 += tiempo_frame2
            _, frame2 = cap.read()
            frame2 = cv2.resize(frame2, (640, 358))

        img = cv2.hconcat([frame1, frame2])
        cv2.imshow('comparacion resultado', img)

        tiempo += 0.02
        res = cv2.waitKey(20)

        if res & 0xff == ord('y'):
            prediccion.correcta = True
            return

        elif res & 0xff == ord('n'):
            return

    res = cv2.waitKey(0)
    prediccion.correcta = res & 0xff == ord('y')
    return


def evaluar_resultados(video: str):
    carpeta = '../videos/AMV_results'

    predicciones = []
    with open(f'{carpeta}/{video}.txt') as resultados:
        for linea in resultados:
            tiempo_video_inicio, duracion, capitulo, tiempo_cap_inicio = linea.split(' ')
            predicciones.append(
                Prediccion(video, float(tiempo_video_inicio), capitulo, float(tiempo_cap_inicio), float(duracion)))

    correctas = 0
    total = len(predicciones)

    tiempo_detectado = 0
    amv = abrir_video(f'../videos/AMV/{video}.mp4')
    tiempo_total = amv.get(cv2.CAP_PROP_FRAME_COUNT) / amv.get(cv2.CAP_PROP_FPS)

    for prediccion in predicciones:
        comparar_videos(prediccion)

        if prediccion.correcta:
            correctas += 1
            tiempo_detectado += prediccion.duracion

    print(f'aciertos: {correctas / total * 100:.1f}%')
    print(f'tiempo detectado: {tiempo_detectado / tiempo_total * 100:.1f}%')
    return


if __name__ == '__main__':
    evaluar_resultados('top10fights')
