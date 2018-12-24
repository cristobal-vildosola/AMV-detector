import time

import pyflann
import numpy


class Index:

    def __init__(self, datos: numpy.ndarray, etiquetas: numpy.ndarray, **kwargs):
        self.flann = pyflann.FLANN()

        t0 = time.time()
        self.flann.build_index(datos, **kwargs)
        t1 = time.time()

        self.build_time = t1 - t0
        self.etiquetas = etiquetas

    def search(self, busquedas, k=1, checks=10) -> numpy.ndarray:
        results, _ = self.flann.nn_index(busquedas, num_neighbors=k, checks=checks, cores=1)
        return results


class Linear(Index):
    def __init__(self, datos, etiquetas):
        super().__init__(datos, etiquetas, algorithm="linear")


class KDTree(Index):
    def __init__(self, datos, etiquetas, trees):
        super().__init__(datos, etiquetas, algorithm="kdtree", trees=trees)


class KMeansTree(Index):
    def __init__(self, datos, etiquetas, branching):
        super().__init__(datos, etiquetas, algorithm='kmeans', branching=branching, iterations=-1)
