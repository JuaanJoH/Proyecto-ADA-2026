from typing import List, Set, Dict, Any, Union
from src.models.Interaccion import Interaccion
from src.models.resultado_auditoria import ResultadoAuditoria

def seleccionar_cobertura_voraz(
    universo_riesgos: Union[Set[str], List[str]],
    interacciones: List[Interaccion],
) -> ResultadoAuditoria:
    """
    Selecciona vorazmente el subconjunto de interacciones que minimiza
    la cardinalidad total para cubrir todos los riesgos de auditoría.

    En cada iteración, selecciona la interacción no elegida que cubra
    el mayor número de riesgos que aún no han sido cubiertos.

    Complejidad Temporal: O(n * r^2) en el peor caso, donde:
        - n: número de interacciones candidatas.
        - r: número de categorías de riesgo (|U|).
    """
    universo_set = set(str(r) for r in universo_riesgos)
    riesgos_pendientes = set(universo_set)
    riesgos_cubiertos_acumulados: Set[str] = set()

    interacciones_disponibles = list(interacciones)
    interacciones_seleccionadas: List[Interaccion] = []
    traza_pasos: List[Dict[str, Any]] = []

    iteracion = 1

    while riesgos_pendientes and interacciones_disponibles:
        mejor_interaccion = None
        max_nuevos_riesgos = -1
        mejores_riesgos_nuevos: Set[str] = set()

        evaluacion_candidatos: List[Dict[str, Any]] = []

        for candidata in interacciones_disponibles:
            nuevos = candidata.riesgos_cubiertos.intersection(riesgos_pendientes)
            cantidad_nuevos = len(nuevos)

            evaluacion_candidatos.append({
                "id": candidata.id,
                "nuevos_riesgos_posibles": sorted(list(nuevos)),
                "cantidad_nuevos": cantidad_nuevos,
            })

            # Criterio voraz: maximizar cantidad de nuevos riesgos cubiertos
            # Desempate determinista por ID
            if cantidad_nuevos > max_nuevos_riesgos:
                max_nuevos_riesgos = cantidad_nuevos
                mejor_interaccion = candidata
                mejores_riesgos_nuevos = nuevos
            elif cantidad_nuevos == max_nuevos_riesgos and mejor_interaccion is not None:
                if str(candidata.id) < str(mejor_interaccion.id):
                    mejor_interaccion = candidata
                    mejores_riesgos_nuevos = nuevos

        # Si ninguna interacción restante aporta nuevos riesgos, no se puede cubrir más
        if mejor_interaccion is None or max_nuevos_riesgos <= 0:
            break

        # Aplicar selección voraz
        interacciones_seleccionadas.append(mejor_interaccion)
        interacciones_disponibles.remove(mejor_interaccion)
        riesgos_pendientes.difference_update(mejores_riesgos_nuevos)
        riesgos_cubiertos_acumulados.update(mejores_riesgos_nuevos)

        traza_pasos.append({
            "iteracion": iteracion,
            "interaccion_elegida": mejor_interaccion.id,
            "descripcion": mejor_interaccion.descripcion,
            "riesgos_nuevos_cubiertos": sorted(list(mejores_riesgos_nuevos)),
            "total_riesgos_nuevos": len(mejores_riesgos_nuevos),
            "riesgos_restantes_por_cubrir": sorted(list(riesgos_pendientes)),
            "candidatos_evaluados": sorted(
                evaluacion_candidatos,
                key=lambda x: (-x["cantidad_nuevos"], str(x["id"]))
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
        metodo = "voraz_estandar",
        cardinalidad_cobertura = len(interacciones_seleccionadas),
        costo_total = costo_total,
        interacciones_seleccionadas = [it.id for it in interacciones_seleccionadas],
        detalle_interacciones = detalle_interacciones,
        universo_objetivo = sorted(list(universo_set)),
        riesgos_cubiertos_totales = sorted(list(riesgos_cubiertos_acumulados)),
        es_cobertura_completa = es_completa,
        riesgos_huerfanos_no_cubiertos = sorted(list(riesgos_pendientes)),
        traza_paso_a_paso = traza_pasos,
    )