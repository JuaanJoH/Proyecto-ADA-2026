from typing import List, Dict, Any, Tuple
from src.models.Etapa import Etapa
from src.models.resultado_aceleracion import ResultadoAceleracion

def construir_tabla_dp(etapas: List[Etapa], presupuesto: int) -> List[List[int]]:
    """
    Construye la matriz DP para el problema de la Mochila 0/1.

    DP[i][b] almacena la reducción máxima de tiempo alcanzable considerando
    un subconjunto de las primeras i etapas con un presupuesto de a lo sumo b.

    Recurrencia:
        DP[i][b] = DP[i-1][b]                                    si c_i > b
        DP[i][b] = max(DP[i-1][b], DP[i-1][b - c_i] + d_i)       si c_i <= b

    Complejidad Temporal: O(n * B)
    Complejidad Espacial: O(n * B)
    """
    n = len(etapas)
    tabla = [[0] * (presupuesto + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        etapa_actual = etapas[i - 1]
        costo = etapa_actual.costo_aceleracion
        reduccion = etapa_actual.reduccion_tiempo

        for b in range(presupuesto + 1):
            if costo > b:
                tabla[i][b] = tabla[i - 1][b]
            else:
                opcion_sin_acelerar = tabla[i - 1][b]
                opcion_acelerando = tabla[i - 1][b - costo] + reduccion
                if opcion_acelerando > opcion_sin_acelerar:
                    tabla[i][b] = opcion_acelerando
                else:
                    tabla[i][b] = opcion_sin_acelerar

    return tabla

def reconstruir_solucion_optima(
    etapas: List[Etapa],
    presupuesto: int,
    tabla_dp: List[List[int]],
) -> Tuple[List[int], List[Dict[str, Any]], int]:

    # Reconstruye el vector binario de decisiones X y la traza de decisiones
    # retrocediendo a través de la matriz de programación dinámica desde (n, B).
    n = len(etapas)
    vector_decision = [0] * n
    presupuesto_actual = presupuesto
    presupuesto_usado = 0
    pasos_reconstruccion: List[Dict[str, Any]] = []

    # Retroceso desde la última etapa hasta la primera
    for i in range(n, 0, -1):
        etapa = etapas[i - 1]
        costo = etapa.costo_aceleracion
        reduccion = etapa.reduccion_tiempo

        # Verificar si la etapa i fue incluida en la solución óptima
        fue_acelerada = False
        motivo = ""

        if costo <= presupuesto_actual:
            valor_si_acelerada = tabla_dp[i - 1][presupuesto_actual - costo] + reduccion
            valor_sin_acelerar = tabla_dp[i - 1][presupuesto_actual]

            if tabla_dp[i][presupuesto_actual] == valor_si_acelerada and valor_si_acelerada > valor_sin_acelerar:
                fue_acelerada = True
                motivo = (
                    f"Acelerar aporta una reducción total de {valor_si_acelerada} frente a "
                    f"{valor_sin_acelerar} sin acelerar."
                )
            else:
                motivo = (
                    f"No acelerar es preferible u óptimo igual: valor sin acelerar ({valor_sin_acelerar}) "
                    f">= valor acelerando ({valor_si_acelerada})."
                )
        else:
            motivo = (
                f"Presupuesto insuficiente ({presupuesto_actual} disponible < {costo} costo requerido)."
            )

        presupuesto_previo = presupuesto_actual
        if fue_acelerada:
            vector_decision[i - 1] = 1
            presupuesto_actual -= costo
            presupuesto_usado += costo

        pasos_reconstruccion.append({
            "etapa_id": etapa.id,
            "nombre_etapa": etapa.nombre,
            "duracion_original": etapa.duracion_original,
            "costo": costo,
            "reduccion": reduccion,
            "acelerada": fue_acelerada,
            "presupuesto_disponible_previo": presupuesto_previo,
            "presupuesto_restante": presupuesto_actual,
            "motivo_decision": motivo,
        })

    # Invertir para presentar la traza en orden secuencial de la cadena (etapa 1 a n)
    traza_decisiones = list(reversed(pasos_reconstruccion))
    return vector_decision, traza_decisiones, presupuesto_usado

def calcular_aceleracion_optima_dp(
    etapas: List[Etapa],
    presupuesto: int,
) -> ResultadoAceleracion:
    
    # Calcula la asignación óptima de presupuesto para acelerar etapas de una cadena en serie.
    if not etapas:
        return ResultadoAceleracion(
            ahorro_optimo=0,
            duracion_original_total=0,
            duracion_final_total=0,
            presupuesto_total=presupuesto,
            presupuesto_usado=0,
            presupuesto_remanente=presupuesto,
            etapas_aceleradas=[],
            etapas_no_aceleradas=[],
            vector_decision_binario=[],
            dimensiones_tabla_dp={"filas": 1, "columnas": presupuesto + 1},
            traza_decisiones=[],
        )

    # 1. Construir la tabla DP
    tabla_dp = construir_tabla_dp(etapas, presupuesto)
    ahorro_optimo = tabla_dp[len(etapas)][presupuesto]

    # 2. Reconstruir la solución óptima y trazas
    vector_decision, traza_decisiones, presupuesto_usado = reconstruir_solucion_optima(
        etapas=etapas,
        presupuesto=presupuesto,
        tabla_dp=tabla_dp,
    )

    # 3. Calcular métricas agregadas
    duracion_original_total = sum(e.duracion_original for e in etapas)
    duracion_final_total = duracion_original_total - ahorro_optimo

    etapas_aceleradas: List[Dict[str, Any]] = []
    etapas_no_aceleradas: List[Dict[str, Any]] = []

    for idx, etapa in enumerate(etapas):
        info_etapa = {
            "id": etapa.id,
            "nombre": etapa.nombre,
            "duracion_original": etapa.duracion_original,
            "costo": etapa.costo_aceleracion,
            "reduccion": etapa.reduccion_tiempo,
            "duracion_final": etapa.duracion_original - (etapa.reduccion_tiempo if vector_decision[idx] else 0),
        }
        if vector_decision[idx] == 1:
            etapas_aceleradas.append(info_etapa)
        else:
            etapas_no_aceleradas.append(info_etapa)

    return ResultadoAceleracion(
        ahorro_optimo = ahorro_optimo,
        duracion_original_total = duracion_original_total,
        duracion_final_total = duracion_final_total,
        presupuesto_total = presupuesto,
        presupuesto_usado = presupuesto_usado,
        presupuesto_remanente = presupuesto - presupuesto_usado,
        etapas_aceleradas = etapas_aceleradas,
        etapas_no_aceleradas = etapas_no_aceleradas,
        vector_decision_binario = vector_decision,
        dimensiones_tabla_dp = {
            "filas": len(etapas) + 1,
            "columnas": presupuesto + 1,
        },
        traza_decisiones = traza_decisiones,
    )