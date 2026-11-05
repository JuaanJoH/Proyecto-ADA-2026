import time
from typing import Callable, Any, Tuple
from contextlib import contextmanager


class Cronometro:
    # Clase simple para cronometrar bloques de código mediante time.perf_counter

    def __init__(self) -> None:
        self.tiempo_inicio: float = 0.0
        self.tiempo_fin: float = 0.0
        self.tiempo_transcurrido: float = 0.0

    def iniciar(self) -> None:
        # Inicia el cronómetro
        self.tiempo_inicio = time.perf_counter()

    def detener(self) -> float:
        # Detiene el cronómetro y retorna el tiempo transcurrido en segundos
        self.tiempo_fin = time.perf_counter()
        self.tiempo_transcurrido = self.tiempo_fin - self.tiempo_inicio
        return self.tiempo_transcurrido


@contextmanager
def medir_tiempo():
    # Context manager para medir el tiempo de ejecución en segundos con time.perf_counter.
    resultado = {"segundos": 0.0}
    inicio = time.perf_counter()
    try:
        yield resultado
    finally:
        fin = time.perf_counter()
        resultado["segundos"] = fin - inicio


def ejecutar_con_tiempo(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Tuple[Any, float]:
    # Ejecuta una función pasando argumentos posicionales y nombrados,
    # retornando una tupla con (resultado_de_la_funcion, tiempo_en_segundos).
    inicio = time.perf_counter()
    resultado = func(*args, **kwargs)
    fin = time.perf_counter()
    return resultado, (fin - inicio)