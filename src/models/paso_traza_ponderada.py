from dataclasses import dataclass
from typing import List, Union, Dict, Any

@dataclass
class PasoTrazaPonderada:
    iteracion: int
    interaccion_elegida: Union[int, str]
    descripcion: str
    costo_interaccion: float
    riesgos_nuevos_cubiertos: List[str]
    total_riesgos_nuevos: int
    ratio_costo_efectividad: float
    riesgos_restantes_por_cubrir: List[str]
    candidatos_evaluados: List[Dict[str, Any]]