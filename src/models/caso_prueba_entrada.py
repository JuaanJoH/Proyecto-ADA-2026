from dataclasses import dataclass
from typing import List, Optional
from src.models.etapa import Etapa
from src.models.interaccion import Interaccion

@dataclass
class CasoPruebaEntrada:
    id_caso: str
    descripcion: str
    presupuesto_aceleracion: int
    etapas: List[Etapa]
    universo_riesgos: List[str]
    interacciones: List[Interaccion]
    presupuesto_conjunto: Optional[int] = None
