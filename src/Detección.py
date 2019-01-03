import os
import re
from typing import List


class Frame:
    def __init__(self, video, tiempo, indice):
        self.video = video
        self.indice = indice
        self.tiempo = tiempo


class Cercanos:
    def __init__(self, tiempo: float, frames: List[Frame]):
        self.tiempo = tiempo
        self.frames = frames


def leer_cercanos(video: str) -> List[Cercanos]:
    """
    Lee un archivo que contiene los frames más cercanos a cada frame de un video. Cada linea debe tener el siguiente
    formato: 'tiempo $ comercial # tiempo # indice | comercial # tiempo # indice | ...'.

    :param video: nombre del archivo que contiene la información

    :return: una lista de Cercanos, objeto que almacena la información de una linea.
    """
    cercanos = []

    with open(video, 'r') as log:
        for linea in log:
            # separar tiempo de los frames.
            tiempo, datos = linea.split(' $ ')

            # parsear tiempo y separar frames.
            tiempo = float(tiempo)
            datos = datos.split(' | ')

            # parsear frames.
            frames = []
            for frame in datos:
                video, tiempo_frame, indice = frame.split(' # ')
                frames.append(Frame(video=video, tiempo=float(tiempo_frame), indice=int(indice)))

            # agregar linea parseada a la lista
            cercanos.append(Cercanos(frames=frames, tiempo=tiempo))

    return cercanos


class Candidato:

    def __init__(self, video: str, indice: int, tiempo_inicio: float, tiempo_clip_inicio: float):
        self.video = video
        self.indice = indice

        self.tiempo_inicio = tiempo_inicio
        self.tiempo_clip_inicio = tiempo_clip_inicio
        self.duracion = 0

        self.errores = 0
        self.aciertos = 0
        self.errores_continuos = 0

    def buscar_siguiente(self, cercanos: Cercanos, rango: int = 0):
        self.indice += 1

        for frame in cercanos.frames:

            # buscar índice en el rando
            if self.video == frame.video and (frame.indice - rango) <= self.indice <= (frame.indice + rango):
                self.duracion = cercanos.tiempo - self.tiempo_clip_inicio
                self.errores_continuos = 0
                self.aciertos += 1

                # seguir buscando si no es mayor o igual al índice buscar
                if frame.indice >= self.indice:
                    return

        self.errores_continuos += 1
        self.errores += 1
        return

    def sobrepuesto(self, cand):
        if self.video != cand.video:
            return False

        if self.tiempo_clip_inicio <= cand.tiempo_clip_inicio < self.tiempo_clip_inicio + self.duracion or \
                cand.tiempo_clip_inicio <= self.tiempo_clip_inicio < cand.tiempo_clip_inicio + cand.duracion:
            return True

        return False

    def __str__(self):
        return f'{self.tiempo_clip_inicio:.2f} {self.duracion:.2f} {self.video} {self.tiempo_inicio:.2f}'


def buscar_secuencias(video: str, max_errores_continuos=7, tiempo_minimo=1, rango=0):
    """
    Busca comerciales en un archivo que contiene los k frames más cercanos a cada frame de un video y los registra en
    un archivo.

    :param video: la ubicación del archivo.
    :param max_errores_continuos: máximos errores continuos para determinar que un clip terminó.
    :param tiempo_minimo: tiempo mínimo para afirmar que un clip es válido.
    """

    # nombre del video
    nombre_video = re.split('[/.]', video)[-2]
    print(f'buscando clips en {nombre_video}')

    # leer cercanos del video.
    lista_cercanos = leer_cercanos(video)

    # lista de candidatos para buscar comerciales
    candidatos = []
    clips = []

    # abrir log
    nombre = re.split('[/.]', video)[-2]
    if not os.path.isdir('../videos/AMV_results'):
        os.mkdir('../videos/AMV_results')
    log = open(f'../videos/AMV_results/{nombre}.txt', 'w')

    for cercanos in lista_cercanos:
        # se tiene una lista de comerciales para eliminar (especificos) y comerciales completados para eliminar todos
        # los que coincidan en el nombre (general)
        terminados = []

        # buscar secuencias
        for cand in candidatos:
            cand.buscar_siguiente(cercanos, rango=rango)

            # determinar fin de clip.
            if cand.errores_continuos >= max_errores_continuos:
                terminados.append(cand)

        # eliminar comerciales
        for terminado in terminados:
            candidatos.remove(terminado)

            # determinar que el clip es valido
            if terminado.duracion > tiempo_minimo and \
                    3 * terminado.aciertos >= terminado.errores - max_errores_continuos:
                clips.append(terminado)

        # agregar candidatos. todos?
        for frame in cercanos.frames:

            # chequear que no sea un frame actual en un candidato
            agregar = True
            for cand1 in candidatos:
                if cand1.video == frame.video and cand1.indice == frame.indice:
                    agregar = False
                    break

            if agregar:
                candidatos.append(Candidato(video=frame.video, indice=frame.indice, tiempo_inicio=frame.tiempo,
                                            tiempo_clip_inicio=cercanos.tiempo))

    # filtrar clips
    sobrepuestos = set()
    for cand1 in clips:
        for cand2 in clips:

            # no comparar consigo mismo
            if cand2 == cand1:
                continue

            # si hay superposición dejar el clip de mayor duración
            if cand1.sobrepuesto(cand2):
                if cand1.duracion > cand2.duracion:
                    sobrepuestos.add(cand2)
                else:
                    sobrepuestos.add(cand1)

    # eliminar clips sobrepuestos
    for clip in sobrepuestos:
        clips.remove(clip)

    for clip in clips:
        log.write(f'{clip}\n')
        print(clip)

    # cerrar log
    log.close()
    return


def main():
    tamano = (10, 10)
    fps = 6

    video = 'cantHoldUs'

    buscar_secuencias(f'../videos/AMV_cerc_{tamano}_{fps}/{video}.txt',
                      max_errores_continuos=6, tiempo_minimo=1, rango=0)
    return


if __name__ == '__main__':
    main()
