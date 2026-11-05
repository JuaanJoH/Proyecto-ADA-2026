from dataclasses import dataclass
from typing import Union


@dataclass

class Etapa:  
    id: Union[int, str]
    nombre: str
    duracion_original: int
    costo_aceleracion: int
    reduccion_tiempo: int

    def __post_init__(self) -> None:
        """Valida las invariantes del dominio."""
        if self.duracion_original <= 0:
            raise ValueError(f"La duración original de la etapa {self.id} debe ser > 0.")
        if self.costo_aceleracion <= 0:
            raise ValueError(f"El costo de aceleración de la etapa {self.id} debe ser > 0.")
        if self.reduccion_tiempo <= 0:
            raise ValueError(f"La reducción de tiempo de la etapa {self.id} debe ser > 0.")
        if self.reduccion_tiempo >= self.duracion_original:
            raise ValueError(
                f"La reducción de tiempo ({self.reduccion_tiempo}) no puede ser mayor o igual "
                f"a la duración original ({self.duracion_original}) en la etapa {self.id}."
            )