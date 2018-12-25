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


def leer_cercanos(archivo: str) -> List[Cercanos]:
    """
    Lee un archivo que contiene los frames más cercanos a cada frame de un video. Cada linea debe tener el siguiente
    formato: 'tiempo $ comercial # tiempo # indice | comercial # tiempo # indice | ...'.

    :param archivo: nombre del archivo que contiene la información

    :return: una lista de Cercanos, objeto que almacena la información de una linea.
    """
    cercanos = []

    with open(archivo, 'r') as log:
        for linea in log:
            # separar tiempo de los frames.
            tiempo, datos = linea.split(' $ ')

            # parsear tiempo y separar frames.
            tiempo = float(tiempo.split(' # ')[1])
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
        self.tiempo_fin = tiempo_inicio

        self.tiempo_clip_inicio = tiempo_clip_inicio
        self.tiempo_clip_fin = tiempo_clip_inicio

        self.errores = 0
        self.aciertos = 0
        self.errores_continuos = 0

    def buscar_siguiente(self, cercanos: Cercanos, rango: int = 0):
        self.indice += 1

        for frame in cercanos.frames:

            # buscar índice en el rando
            if self.video == frame.video and (frame.indice - rango) <= self.indice <= (frame.indice + rango):
                self.tiempo_fin = frame.tiempo
                self.tiempo_clip_fin = cercanos.tiempo
                self.errores_continuos = 0
                self.aciertos += 1

                # seguir buscando si no es mayor o igual al índice buscar
                if frame.indice >= self.indice:
                    return

        self.errores_continuos += 1
        self.errores += 1
        return


def buscar_secuencias(archivo: str, max_errores_continuos=3, tiempo_minimo=1):
    """
    Busca comerciales en un archivo que contiene los k frames más cercanos a cada frame de un video y los registra en
    un archivo 'respuesta.txt'

    :param archivo: la ubicación del archivo.
    :param max_errores_continuos: máximos errores continuos para determinar que un clip terminó.
    :param tiempo_minimo: tiempo mínimo para afirmar que un clip es válido.
    """

    # nombre del video
    nombre_video = re.split('[/.]', archivo)[-2]
    print(f'buscando comerciales en {nombre_video}')

    # leer cercanos del video.
    lista_cercanos = leer_cercanos(archivo)

    # lista de candidatos para buscar comerciales
    candidatos = []

    # TODO abrir log
    # log = open('respuesta.txt', 'a')

    for cercanos in lista_cercanos:
        # se tiene una lista de comerciales para eliminar (especificos) y comerciales completados para eliminar todos
        # los que coincidan en el nombre (general)
        terminados = []

        # buscar secuencias
        for cand in candidatos:
            cand.buscar_siguiente(cercanos, rango=1)

            # determinar fin de clip.
            if cand.errores_continuos >= max_errores_continuos:
                terminados.append(cand)

        # eliminar comerciales
        for terminado in terminados:
            candidatos.remove(terminado)

            # TODO determinar que el clip es valido (tiempo?)
            if terminado.tiempo_fin - terminado.tiempo_inicio > tiempo_minimo and \
                    2 * terminado.aciertos >= terminado.errores:
                print(f'clip detectado: {terminado.tiempo_clip_inicio} {terminado.tiempo_clip_fin} '
                      f'{terminado.video} {terminado.tiempo_inicio} {terminado.tiempo_fin}')

        # agregar candidatos. todos?
        for frame in cercanos.frames:

            # chequear que no sea un frame actual en un candidato
            agregar = True
            for candidato in candidatos:
                if candidato.video == frame.video and candidato.indice == frame.indice:
                    agregar = False
                    break

            if agregar:
                candidatos.append(Candidato(video=frame.video, indice=frame.indice, tiempo_inicio=frame.tiempo,
                                            tiempo_clip_inicio=cercanos.tiempo))

    # cerrar log
    # log.close()
    return


def main():
    tamano = (10, 10)
    salto = 4

    archivo = 'top10handToHand'
    max_errores_continuos = 35
    tiempo_minimo = 2

    buscar_secuencias(f'../videos/AMV_cerc_{tamano}_{salto}/{archivo}.txt', max_errores_continuos, tiempo_minimo)
    return


if __name__ == '__main__':
    main()
