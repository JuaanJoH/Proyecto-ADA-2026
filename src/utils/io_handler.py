"""
Módulo de manejo de entrada/salida (I/O) en formato JSON.
Asegura la separación estricta entre la lectura/escritura de datos
y la lógica algorítmica pura del dominio.
"""

import json
from pathlib import Path
from typing import Union, Dict, Any, List

from src.models.Etapa import Etapa
from src.models.Interaccion import Interaccion
from src.models.caso_prueba_entrada import CasoPruebaEntrada
from src.models.resultado_ejecucion_caso import ResultadoEjecucionCaso


class SerializadorJSONPersonalizado(json.JSONEncoder):
    """Codificador JSON personalizado para manejar conjuntos y dataclasses."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return sorted(list(obj))
        if hasattr(obj, "a_diccionario"):
            return obj.a_diccionario()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


def cargar_caso_prueba(ruta_archivo: Union[str, Path]) -> CasoPruebaEntrada:
    path = Path(ruta_archivo)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de caso de prueba: {ruta_archivo}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            datos = json.load(f)
        except json.JSONDecodeError as err:
            raise ValueError(f"Error de formato JSON en {ruta_archivo}: {err}") from err

    es_formato_profesora = "parametros" in datos or "categorias_riesgo" in datos

    if es_formato_profesora:
        id_caso = str(datos.get("id_caso", path.stem))
        params = datos.get("parametros", {})
        descripcion = str(datos.get("descripcion", f"Instancia oficial profesora: {id_caso}"))
        presupuesto = int(params.get("presupuesto_aceleracion_B", datos.get("presupuesto_aceleracion", 0)))
        presupuesto_conjunto = params.get("presupuesto_conjunto_aceleracion_y_auditoria")
        if presupuesto_conjunto is not None:
            presupuesto_conjunto = int(presupuesto_conjunto)

        if "etapas" not in datos:
            raise ValueError("El archivo carece de la lista de 'etapas'.")

        lista_etapas: List[Etapa] = []
        for idx, e in enumerate(datos["etapas"]):
            etapa_id = e.get("id", idx + 1)
            duracion = int(e.get("duracion_normal", e.get("duracion_original", 0)))
            costo = int(e["costo_aceleracion"])
            reduccion = int(e.get("reduccion_tiempo_si_acelera", e.get("reduccion_tiempo", 0)))
            nombre = str(e.get("nombre", f"Etapa_{etapa_id}"))
            lista_etapas.append(Etapa(
                id=etapa_id,
                nombre=nombre,
                duracion_original=duracion,
                costo_aceleracion=costo,
                reduccion_tiempo=reduccion,
            ))

        if "categorias_riesgo" in datos:
            universo_riesgos = [
                str(r["id"]) if isinstance(r, dict) else str(r)
                for r in datos["categorias_riesgo"]
            ]
        elif "universo_riesgos" in datos:
            universo_riesgos = [str(r) for r in datos["universo_riesgos"]]
        else:
            raise ValueError("No se encontró 'categorias_riesgo' ni 'universo_riesgos'.")

        lista_interacciones: List[Interaccion] = []
        if "interacciones" in datos:
            for idx, it in enumerate(datos["interacciones"]):
                lista_interacciones.append(Interaccion(
                    id=it.get("id", f"INT-{idx + 1:02d}"),
                    descripcion=str(it.get("descripcion", f"Interacción {idx + 1}")),
                    riesgos_cubiertos=set(str(r) for r in it["riesgos_cubiertos"]),
                    costo=float(it.get("costo", 1.0)),
                ))
        else:
            for e in datos["etapas"]:
                etapa_id = str(e["id"])
                variaciones = e.get("variaciones_auditoria", [])
                if variaciones:
                    for v in variaciones:
                        var_id = v.get("id", "completa")
                        costo_v = float(v.get("costo", 1.0))
                        riesgos_v = set(str(r) for r in v.get("riesgos_cubiertos", []))
                        lista_interacciones.append(Interaccion(
                            id=f"{etapa_id}_{var_id}",
                            descripcion=f"Auditoría {var_id} en etapa {etapa_id}",
                            riesgos_cubiertos=riesgos_v,
                            costo=costo_v,
                        ))
                elif "riesgos_cubiertos_auditoria_completa" in e:
                    lista_interacciones.append(Interaccion(
                        id=f"{etapa_id}_completa",
                        descripcion=f"Auditoría completa en etapa {etapa_id}",
                        riesgos_cubiertos=set(str(r) for r in e["riesgos_cubiertos_auditoria_completa"]),
                        costo=float(e.get("costo_auditoria", 1.0)),
                    ))

        return CasoPruebaEntrada(
            id_caso=id_caso,
            descripcion=descripcion,
            presupuesto_aceleracion=presupuesto,
            etapas=lista_etapas,
            universo_riesgos=universo_riesgos,
            interacciones=lista_interacciones,
            presupuesto_conjunto=presupuesto_conjunto,
        )

    # Formato estándar
    campos_requeridos = [
        "id_caso",
        "presupuesto_aceleracion",
        "etapas",
        "universo_riesgos",
        "interacciones",
    ]
    for campo in campos_requeridos:
        if campo not in datos:
            raise ValueError(f"El archivo JSON carece del campo obligatorio: '{campo}'")

    id_caso = str(datos["id_caso"])
    descripcion = str(datos.get("descripcion", f"Caso de prueba {id_caso}"))
    presupuesto = int(datos["presupuesto_aceleracion"])
    if presupuesto < 0:
        raise ValueError(f"El presupuesto de aceleración no puede ser negativo: {presupuesto}")

    lista_etapas_std: List[Etapa] = []
    for idx, e in enumerate(datos["etapas"]):
        etapa = Etapa(
            id=e.get("id", idx + 1),
            nombre=str(e.get("nombre", f"Etapa_{idx + 1}")),
            duracion_original=int(e["duracion_original"]),
            costo_aceleracion=int(e["costo_aceleracion"]),
            reduccion_tiempo=int(e["reduccion_tiempo"]),
        )
        lista_etapas_std.append(etapa)

    universo_riesgos_std = [str(r) for r in datos["universo_riesgos"]]
    lista_interacciones_std: List[Interaccion] = []
    for idx, it in enumerate(datos["interacciones"]):
        interaccion = Interaccion(
            id=it.get("id", f"INT-{idx + 1:02d}"),
            descripcion=str(it.get("descripcion", f"Interacción {idx + 1}")),
            riesgos_cubiertos=set(str(r) for r in it["riesgos_cubiertos"]),
            costo=float(it.get("costo", 1.0)),
        )
        lista_interacciones_std.append(interaccion)

    return CasoPruebaEntrada(
        id_caso=id_caso,
        descripcion=descripcion,
        presupuesto_aceleracion=presupuesto,
        etapas=lista_etapas_std,
        universo_riesgos=universo_riesgos_std,
        interacciones=lista_interacciones_std,
    )


def guardar_resultado(
    resultado: Union[ResultadoEjecucionCaso, Dict[str, Any]],
    ruta_destino: Union[str, Path],
) -> Path:
    path = Path(ruta_destino)
    path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(resultado, ResultadoEjecucionCaso):
        datos = resultado.a_diccionario()
    else:
        datos = resultado

    with open(path, "w", encoding="utf-8") as f:
        json.dump(datos, f, cls=SerializadorJSONPersonalizado, indent=2, ensure_ascii=False)

    return path