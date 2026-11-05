from typing import List, Set, Dict, Any, Union, Optional
from src.models.interaccion import Interaccion
from src.models.resultado_auditoria import ResultadoAuditoria

def seleccionar_cobertura_ponderada(
    universo_riesgos: Union[Set[str], List[str]],
    interacciones: List[Interaccion],
) -> ResultadoAuditoria:
    """
    Selecciona vorazmente el subconjunto de interacciones que minimiza
    el costo monetario total para cubrir todos los riesgos de auditoría.

    Criterio voraz (Chvátal 1979):
        En cada paso, selecciona la interacción j que minimiza el ratio:
        ratio = costo_j / |S_j ∩ U_restante|
        para todos los candidatos con |S_j ∩ U_restante| > 0.

    Complejidad Temporal: O(n * r^2) en el peor caso.
    """
    universo_set = set(str(r) for r in universo_riesgos)
    riesgos_pendientes = set(universo_set)
    riesgos_cubiertos_acumulados: Set[str] = set()

    interacciones_disponibles = list(interacciones)
    interacciones_seleccionadas: List[Interaccion] = []
    traza_pasos: List[Dict[str, Any]] = []

    iteracion = 1

    while riesgos_pendientes and interacciones_disponibles:
        mejor_interaccion: Optional[Interaccion] = None
        mejor_ratio: float = float("inf")
        mejor_cantidad_nuevos: int = 0
        mejores_riesgos_nuevos: Set[str] = set()

        evaluacion_candidatos: List[Dict[str, Any]] = []

        for candidata in interacciones_disponibles:
            nuevos = candidata.riesgos_cubiertos.intersection(riesgos_pendientes)
            cantidad_nuevos = len(nuevos)

            if cantidad_nuevos > 0:
                ratio = candidata.costo / cantidad_nuevos
            else:
                ratio = float("inf")

            evaluacion_candidatos.append({
                "id": candidata.id,
                "costo": candidata.costo,
                "nuevos_riesgos_posibles": sorted(list(nuevos)),
                "cantidad_nuevos": cantidad_nuevos,
                "ratio_costo_efectividad": round(ratio, 4) if ratio != float("inf") else None,
            })

            # Criterio: minimizar ratio; desempate por mayor cantidad de nuevos, luego ID
            if cantidad_nuevos > 0:
                if ratio < mejor_ratio:
                    mejor_ratio = ratio
                    mejor_cantidad_nuevos = cantidad_nuevos
                    mejor_interaccion = candidata
                    mejores_riesgos_nuevos = nuevos
                elif abs(ratio - mejor_ratio) < 1e-9:
                    if cantidad_nuevos > mejor_cantidad_nuevos:
                        mejor_ratio = ratio
                        mejor_cantidad_nuevos = cantidad_nuevos
                        mejor_interaccion = candidata
                        mejores_riesgos_nuevos = nuevos
                    elif cantidad_nuevos == mejor_cantidad_nuevos and mejor_interaccion is not None:
                        if str(candidata.id) < str(mejor_interaccion.id):
                            mejor_ratio = ratio
                            mejor_cantidad_nuevos = cantidad_nuevos
                            mejor_interaccion = candidata
                            mejores_riesgos_nuevos = nuevos

        # Si no hay interacción que aporte nuevos riesgos, finalizar
        if mejor_interaccion is None or mejor_cantidad_nuevos <= 0:
            break

        interacciones_seleccionadas.append(mejor_interaccion)
        interacciones_disponibles.remove(mejor_interaccion)
        riesgos_pendientes.difference_update(mejores_riesgos_nuevos)
        riesgos_cubiertos_acumulados.update(mejores_riesgos_nuevos)

        traza_pasos.append({
            "iteracion": iteracion,
            "interaccion_elegida": mejor_interaccion.id,
            "descripcion": mejor_interaccion.descripcion,
            "costo_interaccion": mejor_interaccion.costo,
            "riesgos_nuevos_cubiertos": sorted(list(mejores_riesgos_nuevos)),
            "total_riesgos_nuevos": len(mejores_riesgos_nuevos),
            "ratio_costo_efectividad": round(mejor_ratio, 6),
            "riesgos_restantes_por_cubrir": sorted(list(riesgos_pendientes)),
            "candidatos_evaluados": sorted(
                evaluacion_candidatos,
                key=lambda x: (
                    x["ratio_costo_efectividad"] if x["ratio_costo_efectividad"] is not None else float("inf"),
                    -x["cantidad_nuevos"],
                    str(x["id"])
                )
            ),
        })

        iteracion += 1

    es_completa = len(riesgos_pendientes) == 0
    costo_total = sum(it.costo for it in interacciones_seleccionadas)

    detalle_interacciones = [
        {
            "id": it.id,
            "descripcion": it.descripcion,
            "riesgos_cubiertos": sorted(list(it.riesgos_cubiertos)),
            "costo": it.costo,
        }
        for it in interacciones_seleccionadas
    ]

    return ResultadoAuditoria(
        metodo = "voraz_ponderado",
        cardinalidad_cobertura = len(interacciones_seleccionadas),
        costo_total = round(costo_total, 4),
        interacciones_seleccionadas = [it.id for it in interacciones_seleccionadas],
        detalle_interacciones = detalle_interacciones,
        universo_objetivo = sorted(list(universo_set)),
        riesgos_cubiertos_totales = sorted(list(riesgos_cubiertos_acumulados)),
        es_cobertura_completa = es_completa,
        riesgos_huerfanos_no_cubiertos = sorted(list(riesgos_pendientes)),
        traza_paso_a_paso = traza_pasos,
    )