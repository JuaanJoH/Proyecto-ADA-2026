from dataclasses import dataclass, asdict
from typing import List, Union, Dict, Any


@dataclass
class ResultadoAuditoria:
    metodo: str
    cardinalidad_cobertura: int
    costo_total: float
    interacciones_seleccionadas: List[Union[int, str]]
    detalle_interacciones: List[Dict[str, Any]]
    universo_objetivo: List[str]
    riesgos_cubiertos_totales: List[str]
    es_cobertura_completa: bool
    riesgos_huerfanos_no_cubiertos: List[str]
    traza_paso_a_paso: List[Dict[str, Any]]

    def a_diccionario(self) -> Dict[str, Any]:
        return asdict(self)
