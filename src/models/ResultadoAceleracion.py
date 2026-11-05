from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass

class ResultadoAceleracion:
    ahorro_optimo: int
    duracion_original_total: int
    duracion_final_total: int
    presupuesto_total: int
    presupuesto_usado: int
    presupuesto_remanente: int
    etapas_aceleradas: List[Dict[str, Any]]
    etapas_no_aceleradas: List[Dict[str, Any]]
    vector_decision_binario: List[int]
    dimensiones_tabla_dp: Dict[str, int]
    traza_decisiones: List[Dict[str, Any]]

    def a_diccionario(self) -> Dict[str, Any]:
        return asdict(self)