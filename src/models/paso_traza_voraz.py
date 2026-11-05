from dataclasses import dataclass
from typing import List, Union, Dict, Any

@dataclass
class PasoTrazaVoraz:
    iteracion: int
    interaccion_elegida: Union[int, str]
    descripcion: str
    riesgos_nuevos_cubiertos: List[str]
    total_riesgos_nuevos: int
    riesgos_restantes_por_cubrir: List[str]
    candidatos_evaluados: List[Dict[str, Any]]