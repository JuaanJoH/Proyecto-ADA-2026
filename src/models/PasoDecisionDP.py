from dataclasses import dataclass
from typing import Union

@dataclass

class PasoDecisionDP:
    """Registra el análisis de decisión para una etapa durante la reconstrucción óptima."""
    etapa_id: Union[int, str]
    nombre_etapa: str
    costo: int
    reduccion: int
    acelerada: bool
    presupuesto_disponible: int
    presupuesto_restante: int
    motivo: str