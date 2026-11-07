import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from src.models.caso_prueba_entrada import CasoPruebaEntrada
from src.models.resultado_ejecucion_caso import ResultadoEjecucionCaso
from src.algorithms.aceleracion_dp import calcular_aceleracion_optima_dp
from src.algorithms.auditoria_voraz import seleccionar_cobertura_voraz
from src.algorithms.auditoria_ponderada import seleccionar_cobertura_ponderada
from src.utils.io_handler import cargar_caso_prueba, guardar_resultado
from src.utils.timer import medir_tiempo

"""
uso:

python main.py --input data/casos/entrada_G3_mochila_20_nodos.json

para ver la traza:
python main.py --input data/casos/entrada_G3_mochila_20_nodos.json --verbose
"""

def procesar_caso(
    caso: CasoPruebaEntrada,
    directorio_salida: Path,
    verbose: bool = False,
) -> Path:
    print(f"\n{'='*75}")
    print(f" EJECUTANDO CASO: {caso.id_caso} - {caso.descripcion}")
    print(f"{'='*75}")
    print(f" • Etapas en serie: {len(caso.etapas)} | Presupuesto B: {caso.presupuesto_aceleracion}")
    print(f" • Universo de Riesgos: {len(caso.universo_riesgos)} | Interacciones candidatas: {len(caso.interacciones)}")
    # 1. PARTE 1: Aceleración Óptima bajo Presupuesto (DP Mochila 0/1)
    with medir_tiempo() as timer_dp:
        resultado_dp = calcular_aceleracion_optima_dp(
            etapas=caso.etapas,
            presupuesto=caso.presupuesto_aceleracion,
        )
    tiempo_dp = timer_dp["segundos"]
    # 2. PARTE 2: Cobertura Mínima de Auditoría (Voraz Estándar)
    with medir_tiempo() as timer_voraz:
        resultado_voraz = seleccionar_cobertura_voraz(
            universo_riesgos=caso.universo_riesgos,
            interacciones=caso.interacciones,
        )
    tiempo_voraz = timer_voraz["segundos"]
    # 3. VARIANTE 1: Cobertura de Auditoría Ponderada por Costo (Chvátal 1979)
    with medir_tiempo() as timer_ponderada:
        resultado_ponderada = seleccionar_cobertura_ponderada(
            universo_riesgos=caso.universo_riesgos,
            interacciones=caso.interacciones,
        )
    tiempo_ponderada = timer_ponderada["segundos"]
    tiempo_total = tiempo_dp + tiempo_voraz + tiempo_ponderada
    # Consolidar objeto de resultados
    tiempos = {
        "aceleracion_dp_segundos": round(tiempo_dp, 8),
        "auditoria_voraz_segundos": round(tiempo_voraz, 8),
        "auditoria_ponderada_segundos": round(tiempo_ponderada, 8),
        "total_ejecucion_segundos": round(tiempo_total, 8),
    }
    resultado_integral = ResultadoEjecucionCaso(
        id_caso=caso.id_caso,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        tiempos_ejecucion_segundos=tiempos,
        aceleracion_dp=resultado_dp.a_diccionario(),
        auditoria_voraz=resultado_voraz.a_diccionario(),
        auditoria_ponderada=resultado_ponderada.a_diccionario(),
    )
    # Exportar archivo JSON
    nombre_archivo_salida = f"{caso.id_caso}_resultado.json"
    ruta_salida = directorio_salida / nombre_archivo_salida
    guardar_resultado(resultado_integral, ruta_salida)
    # Imprimir resumen en consola
    print("\n [1] RESULTADOS ACELERACIÓN ÓPTIMA (DP MOCHILA 0/1):")
    print(f"     - Duración Original: {resultado_dp.duracion_original_total} unidades")
    print(f"     - Ahorro Óptimo Máximo: {resultado_dp.ahorro_optimo} unidades")
    print(f"     - Duración Final Reducida: {resultado_dp.duracion_final_total} unidades")
    print(f"     - Presupuesto Invertido: {resultado_dp.presupuesto_usado} / {resultado_dp.presupuesto_total}")
    ids_aceleradas = [e["id"] for e in resultado_dp.etapas_aceleradas]
    print(f"     - Etapas Aceleradas ({len(ids_aceleradas)}): {ids_aceleradas}")
    print(f"     - Tiempo de cómputo DP: {tiempo_dp*1000:.4f} ms")
    print("\n [2] RESULTADOS AUDITORÍA VORAZ ESTÁNDAR (SET COVER):")
    print(f"     - Interacciones Seleccionadas ({resultado_voraz.cardinalidad_cobertura}): {resultado_voraz.interacciones_seleccionadas}")
    print(f"     - Costo Total Resultante: {resultado_voraz.costo_total:.2f}")
    print(f"     - Cobertura Completa del Universo: {'SÍ' if resultado_voraz.es_cobertura_completa else 'NO'}")
    print(f"     - Tiempo de cómputo Voraz: {tiempo_voraz*1000:.4f} ms")
    print("\n [3] RESULTADOS AUDITORÍA VORAZ PONDERADA POR COSTO (VARIANTE 1):")
    print(f"     - Interacciones Seleccionadas ({resultado_ponderada.cardinalidad_cobertura}): {resultado_ponderada.interacciones_seleccionadas}")
    print(f"     - Costo Mínimo Logrado: {resultado_ponderada.costo_total:.2f}")
    print(f"     - Cobertura Completa del Universo: {'SÍ' if resultado_ponderada.es_cobertura_completa else 'NO'}")
    print(f"     - Tiempo de cómputo Ponderada: {tiempo_ponderada*1000:.4f} ms")
    if caso.presupuesto_conjunto is not None:
        costo_combinado_estandar = resultado_dp.presupuesto_usado + resultado_voraz.costo_total
        costo_combinado_ponderado = resultado_dp.presupuesto_usado + resultado_ponderada.costo_total
        print("\n [4] VERIFICACIÓN DE PRESUPUESTO CONJUNTO (ACELERACIÓN + AUDITORÍA):")
        print(f"     - Presupuesto Conjunto Disponible: {caso.presupuesto_conjunto}")
        print(f"     - Con Voraz Estándar: {resultado_dp.presupuesto_usado} + {resultado_voraz.costo_total:.2f} = {costo_combinado_estandar:.2f} "
              f"[{'CUMPLE' if costo_combinado_estandar <= caso.presupuesto_conjunto else 'EXCEDE'}]")
        print(f"     - Con Voraz Ponderada: {resultado_dp.presupuesto_usado} + {resultado_ponderada.costo_total:.2f} = {costo_combinado_ponderado:.2f} "
              f"[{'CUMPLE' if costo_combinado_ponderado <= caso.presupuesto_conjunto else 'EXCEDE'}]")
    if verbose:
        print("\n [TRAZA DETALLADA: ACELERACIÓN DP]")
        for paso in resultado_dp.traza_decisiones:
            estado = "ACELERADA" if paso["acelerada"] else "NORMAL"
            print(f"   Etapa {paso['etapa_id']} ({paso['nombre_etapa']}): [{estado}] - {paso['motivo_decision']}")
        print("\n [TRAZA DETALLADA: AUDITORÍA VORAZ ESTÁNDAR]")
        for paso in resultado_voraz.traza_paso_a_paso:
            print(f"   Paso {paso['iteracion']}: Elegida {paso['interaccion_elegida']} -> Cubre {paso['riesgos_nuevos_cubiertos']} | Quedan: {len(paso['riesgos_restantes_por_cubrir'])} riesgos")
        print("\n [TRAZA DETALLADA: AUDITORÍA VORAZ PONDERADA]")
        for paso in resultado_ponderada.traza_paso_a_paso:
            print(f"   Paso {paso['iteracion']}: Elegida {paso['interaccion_elegida']} (costo {paso['costo_interaccion']}, ratio {paso['ratio_costo_efectividad']}) -> Cubre {paso['riesgos_nuevos_cubiertos']}")
    print(f"\n [OK] Resultado guardado exitosamente en: {ruta_salida}")
    return ruta_salida
def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(
        description="Proyecto Semestral ADAG - Grupo 3 (Ruta): Primera Entrega."
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Ruta al archivo JSON de entrada o a un directorio con casos de prueba.",
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="data/resultados",
        help="Directorio donde se exportarán los archivos de resultados JSON (default: data/resultados).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Imprime las trazas de decisiones paso a paso en consola.",
    )
    args = parser.parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    archivos_json: List[Path] = []
    if input_path.is_file():
        archivos_json.append(input_path)
    elif input_path.is_dir():
        archivos_json = sorted(list(input_path.glob("*.json")))
        if not archivos_json:
            print(f"Error: No se encontraron archivos .json en el directorio: {input_path}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: La ruta especificada no existe: {input_path}", file=sys.stderr)
        sys.exit(1)
    print(f"Se encontraron {len(archivos_json)} caso(s) para procesar.")
    for archivo in archivos_json:
        try:
            caso = cargar_caso_prueba(archivo)
            procesar_caso(caso, output_dir, verbose=args.verbose)
        except Exception as e:
            print(f"Error procesando {archivo.name}: {e}", file=sys.stderr)
            sys.exit(1)
    print(f"\n{'='*75}")
    print(" EJECUCIÓN FINALIZADA SATISFACTORIAMENTE PARA TODOS LOS CASOS.")
    print(f"{'='*75}")
if __name__ == "__main__":
    main()