import os
import re
import time
from typing import Tuple

import numpy

from src.Indices import Index, KDTree


def leer_caracteristicas(archivo: str) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Lee los datos de un archivo y las retorna en 2 arreglos de numpy, 1 para características y otro para etiquetas.

    :param archivo: el archivo a leer.

    :return: 2 arreglos de numpy, uno para etiquetas y otro para características, en ese orden.
    """
    # nombre e índice de frame
    nombre = re.split('[/.]', archivo)[-2]
    i = 1

    # leer archivo y pasar a listas
    etiqueta_list = []
    caracteristicas_list = []
    with open(archivo, "r") as log:
        for linea in log:
            datos = linea.split(" ")
            etiqueta_list.append(f'{nombre} # {datos[0]} # {i}')
            caracteristicas_list.append([int(x) for x in datos[1:]])
            i += 1

    # transformar listas a arreglos y agregar a los arreglos existentes
    etiqueta = numpy.array(etiqueta_list)
    caracteristicas = numpy.array(caracteristicas_list, dtype=numpy.int32)

    return etiqueta, caracteristicas


def agrupar_caracteristicas(carpeta: str, recargar: bool = True, tamano=(10, 10)
                            ) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Agrupa todos los datos de la carpeta dada en 2 arreglos de numpy, 1 para características y otro para etiquetas.
    Finalmente los guarda en archivos para reutilizarlos si se vuelve a intentar agrupar la misma carpeta.

    :param carpeta: carpeta donde están las características que agrupar.
    :param recargar: determina si se deben recargar los archivos previamente generados (si es que existen).
    :param tamano: tamaño del vector de características.

    :return: 2 arreglos de numpy, uno para etiquetas y otro para características, en ese orden.
    """
    # reutilizar archivos si ya se hizo agrupación antes
    if os.path.isfile(f'{carpeta}/caracteristicas.npy') and os.path.isfile(f'{carpeta}/etiqueta.npy') and recargar:
        caracteristicas = numpy.load(f'{carpeta}/caracteristicas.npy')
        etiqueta = numpy.load(f'{carpeta}/etiqueta.npy')

        return etiqueta, caracteristicas

    # obtener todos los archivos en la carpeta
    archivos = os.listdir(carpeta)

    etiqueta = numpy.empty(0, dtype=numpy.str)
    caracteristicas = numpy.empty((0, tamano[0] * tamano[1]), dtype=numpy.int32)

    # leer las caracteristicas de todos los videos y agruparlas
    i = 0
    for archivo in archivos:
        if not archivo.endswith('.txt'):
            continue

        # leer características y juntar con los arreglos.
        etiqueta_video, caracteristicas_video = leer_caracteristicas(f'{carpeta}/{archivo}')
        etiqueta = numpy.concatenate((etiqueta, etiqueta_video))
        caracteristicas = numpy.concatenate((caracteristicas, caracteristicas_video))

        i += 1
        print(f'{etiqueta.shape[0]:,d} lineas leídas en {i} archivos')

    # guardar archivos
    numpy.save(f'{carpeta}/caracteristicas.npy', caracteristicas)
    numpy.save(f'{carpeta}/etiqueta.npy', etiqueta)

    return etiqueta, caracteristicas


def frames_mas_cercanos_video(archivo: str, carpeta_log: str, indice: Index, k: int = 5, checks=100):
    """
    Encuentra los k frames más cercanos a cada frame del video dado, dentro de todos los frames en una lista de Videos,
    registra esta información en un log txt.

    :param archivo: el archivo del cuál buscar frames cercanos.
    :param carpeta_log: la carpeta en la cual guardar el log.
    :param indice: el índice de busqueda a usar.
    :param k: el número de frames cercanos a buscar.
    :param checks: el número de checks a realizar en la búsqueda.
    """

    # medir tiempo
    t0 = time.time()

    # leer caracteristicas del video
    etiqueta_video, caracteristicas_video = leer_caracteristicas(archivo)

    # abrir log
    nombre = re.split('[/.]', archivo)[-2]
    if not os.path.isdir(carpeta_log):
        os.mkdir(carpeta_log)
    log = open(f'{carpeta_log}/{nombre}.txt', 'w')

    print(f'buscando {k} frames más cercanos para {nombre}')

    # buscar los frames más cercanos de cada frame
    for i in range(caracteristicas_video.shape[0]):
        cercanos = indice.search(caracteristicas_video[i], k=k, checks=checks)[0]
        cercanos_str = ' | '.join([f'{indice.etiquetas[frame]}' for frame in cercanos])

        # registrar resultado
        tiempo = re.split(' # ', etiqueta_video[i])[1]
        log.write(f'{tiempo} $ {cercanos_str}\n')

    log.close()
    print(f'la búsqueda de {k} frames más cercanos tomó {int(time.time() - t0)} segundos')
    return


def main():
    fps = 6
    tamano = (10, 10)
    video = 'cantHoldUs'

    t0 = time.time()
    etiquetas, caracteristicas = agrupar_caracteristicas(f'../videos/Shippuden_car_{tamano}_{fps}',
                                                         recargar=True, tamano=tamano)
    print(f'la agrupación de datos tomó {int(time.time() - t0)} segundos')

    indice = KDTree(datos=caracteristicas, etiquetas=etiquetas, trees=10)
    print(f'la construcción del índice tomó {indice.build_time:.1f} segundos')

    frames_mas_cercanos_video(f'../videos/AMV_car_{tamano}_{fps}/{video}.txt',
                              f'../videos/AMV_cerc_{tamano}_{fps}',
                              indice=indice, checks=100, k=20)


if __name__ == '__main__':
    main()
