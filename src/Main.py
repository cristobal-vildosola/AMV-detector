import time

from src.BusquedaKNN import frames_mas_cercanos_video, agrupar_caracteristicas
from src.Deteccion import buscar_secuencias
from src.Evaluacion import evaluar_resultados
from src.Extraccion import caracteristicas_video
from src.Indices import KDTree


def buscar_clips_amv(video: str):
    carpeta = '../videos/AMV'

    tamano = (10, 10)
    fps = 6

    # extracción de caracteísticas
    caracteristicas_video(f'{carpeta}/{video}.mp4', f'{carpeta}_car_{tamano}_{fps}',
                          fps_extraccion=fps, tamano=tamano)

    # busqueda de vecinos mas cercanos
    t0 = time.time()
    etiquetas, caracteristicas = agrupar_caracteristicas(f'../videos/Shippuden_car_{tamano}_{fps}',
                                                         recargar=True, tamano=tamano)
    print(f'la agrupación de datos tomó {int(time.time() - t0)} segundos')

    indice = KDTree(datos=caracteristicas, etiquetas=etiquetas, trees=10)
    print(f'la construcción del índice tomó {indice.build_time:.1f} segundos')

    frames_mas_cercanos_video(f'../videos/AMV_car_{tamano}_{fps}/{video}.txt',
                              f'../videos/AMV_cerc_{tamano}_{fps}',
                              indice=indice, checks=500, k=20)

    # detección de secuencias
    buscar_secuencias(f'../videos/AMV_cerc_{tamano}_{fps}/{video}.txt',
                      max_errores_continuos=12, tiempo_minimo=1, max_offset=0.15)

    # evaluación
    evaluar_resultados(video)
    return


if __name__ == '__main__':
    buscar_clips_amv('top10fights')
