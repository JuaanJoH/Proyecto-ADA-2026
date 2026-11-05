from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ResultadoEjecucionCaso:
    id_caso: str
    timestamp_utc: str
    tiempos_ejecucion_segundos: Dict[str, float]
    aceleracion_dp: Dict[str, Any]
    auditoria_voraz: Dict[str, Any]
    auditoria_ponderada: Dict[str, Any]

    def a_diccionario(self) -> Dict[str, Any]:
        return asdict(self)