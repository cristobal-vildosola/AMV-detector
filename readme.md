# AMV-detector

AMV detector es un proyecto de recuperación de información 
 multimedia que busca detectar a qué capítulos y segundos
 específicos pertenece cada segmento de un AMV. Esto se
 puede generalizar a buscar a qué video y segundos
 específicos pertenece cada segmento de una
 compilación.

Para ello realiza extracción de características de un set de
 videos de dónde se sacaron los segmentos de la
 compilzación, en este caso, los capítulos del animé.

Luego, utilizando un índice KDTree se realizan búsquedas
 aproximadas de los vecinos más cercanos de los frames
 de la compilación.

Finalmente, se buscan secuencias continuas dentro de los
 vecinos más cercanos de los frames de la compilación, una
 secuencia de largo mayor a T segundos se considera un
 segmento válido y se registra como tal.
