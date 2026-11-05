from dataclasses import dataclass
from typing import Set, Union

@dataclass
class Interaccion:
    id: Union[int, str]
    descripcion: str
    riesgos_cubiertos: Set[str]
    costo: float = 1.0

    def __post_init__(self) -> None:
        if isinstance(self.riesgos_cubiertos, (list, tuple)):
            self.riesgos_cubiertos = set(str(r) for r in self.riesgos_cubiertos)
        else:
            self.riesgos_cubiertos = set(str(r) for r in self.riesgos_cubiertos)

        if self.costo <= 0:
            raise ValueError(f"El costo de la interacción {self.id} debe ser estrictamente positivo (> 0).")
