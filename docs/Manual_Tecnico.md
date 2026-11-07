# Manual Técnico: Sistema de Optimización de Flujo y Auditoría
## Proyecto Semestral ADAG — Grupo 3 (Ruta) | Primera Entrega
**Integrantes:** Juan José Hernández Velásquez, Victor Manuel Valencia Alvarez  
**Repositorio:** `Proyecto-ADA`

---

## 1. Resumen Ejecutivo y Alcance

Este sistema implementa la solución completa, formal y reproducible para la Primera Entrega del proyecto semestral de **Análisis y Diseño de Algoritmos (ADAG)**. Su objetivo es modelar, resolver y auditar flujos de trabajo secuenciales en los que se debe:
1. **Maximizar la aceleración temporal** de una cadena de $n$ etapas dispuestas en serie bajo una restricción de presupuesto financiero $B$, empleando **Programación Dinámica (Mochila 0/1)** con tiempo de ejecución pseudo-polinomial exacto $\Theta(n \cdot B)$.
2. **Minimizar la cardinalidad** de las interacciones necesarias para auditar la totalidad de riesgos normativos del sistema mediante un **Algoritmo Voraz Estándar (Set Cover)** con cota armónica de aproximación $H_r \le \ln(r) + 1$.
3. **Minimizar el costo monetario global** de auditoría considerando costos heterogéneos y variaciones de auditoría (parcial vs. completa) mediante la **Variante 1 Ponderada por Costo (Chvátal 1979)**.
4. **Verificar el Presupuesto Conjunto** entre la inversión en aceleración y el costo de auditoría frente al techo financiero global ($B_{conjunto} \le 100$).

---

## 2. Arquitectura de Software y Principios de Diseño

La estructura del repositorio `Proyecto-ADA` refleja una separación limpia de responsabilidades (SoC), tipado estático estricto y cero acoplamiento entre la lógica algorítmica y los mecanismos de persistencia:

```
Proyecto-ADA/
├── main.py                        # Punto de entrada CLI: orquesta, mide y exporta
├── requirements.txt               # Dependencias de entorno
├── data/
│   ├── casos/                     # Casos de prueba en formato JSON (incluye entrada_G3_mochila_20_nodos.json)
│   └── resultados/                # JSONs exportados con métricas, tiempos y trazas detalladas
├── src/
│   ├── models/
│   │   ├── Etapa.py               # Dataclass de etapa (duración, costo aceleración, reducción)
│   │   ├── Interaccion.py         # Dataclass de interacción de auditoría (costo, riesgos)
│   │   ├── caso_prueba_entrada.py # Estructura agregada de entrada
│   │   ├── paso_decision_dp.py    # Modelo de trazabilidad para reconstrucción DP
│   │   ├── paso_traza_voraz.py    # Modelo de trazabilidad para Voraz estándar
│   │   ├── paso_traza_ponderada.py# Modelo de trazabilidad para Voraz con ratios Chvátal
│   │   ├── resultado_aceleracion.py
│   │   ├── resultado_auditoria.py
│   │   └── resultado_ejecucion_caso.py
│   ├── algorithms/
│   │   ├── aceleracion_dp.py      # Solución exacta DP Mochila 0/1 y Backtracking
│   │   ├── auditoria_voraz.py     # Heurística voraz cardinal estándar
│   │   └── auditoria_ponderada.py # Heurística voraz ponderada por costo (Variante 1)
│   └── utils/
│       ├── io_handler.py          # Serialización/deserialización dual de entradas y salidas JSON
│       └── timer.py               # Medición con time.perf_counter() de alta resolución
└── docs/
    ├── Informe_Tecnico.pdf        # Documento PDF compilado final (17 páginas)
    └── Manual_Tecnico.md          # Este manual técnico
```

### 2.1. Separación Estricta de Responsabilidades (SoC)
* **Capa de Entrada/Salida (`src/utils/io_handler.py`):** Encargada exclusiva de deserializar archivos JSON, validar formatos duales (soporta tanto el formato nativo simplificado como el esquema enriquecido oficial de la profesora con `variaciones_auditoria`), y serializar los resultados con indentación y tipado seguro.
* **Capa de Dominio (`src/models/`):** Modelos de datos desacoplados definidos con `@dataclass`, asegurando validación e invariantes en cada entidad.
* **Capa Algorítmica Pura (`src/algorithms/`):** Funciones sin efectos colaterales de terminal o disco (`pure functions`), que operan sobre listas o conjuntos y retornan objetos de resultado enriquecidos con su traza.
* **Capa de Orquestación (`main.py`):** CLI construida con `argparse` que administra parámetros de entrada, cronometra mediante context managers y genera resúmenes en consola.

### 2.2. Clean Code y Tipado Estático
* **Tipado Explícito:** Cobertura de anotaciones con `typing` (`List`, `Dict`, `Set`, `Union`, `Optional`, `Any`).
* **Cero Hardcoding:** Toda la ejecución depende de las especificaciones del archivo JSON provisto.
* **Nombres Autodocumentados:** Métodos expresivos como `construir_tabla_dp`, `reconstruir_solucion_optima`, `seleccionar_cobertura_voraz`, `seleccionar_cobertura_ponderada`.

---

## 3. Especificación Técnica de los Algoritmos

### 3.1. Aceleración Óptima de la Cadena (`aceleracion_dp.py`)
* **Problema Equivalente:** Mochila 0/1 entera clásica.
* **Entradas:** Lista de $n$ etapas $(t_i, c_i, d_i)$ y presupuesto entero $B \ge 0$.
* **Ecuación de Recurrencia (Bellman):**
  $$\text{DP}[i][b] = \begin{cases} 
  0 & \text{si } i=0 \lor b=0 \\
  \text{DP}[i-1][b] & \text{si } c_i > b \\
  \max\big(\text{DP}[i-1][b], \; \text{DP}[i-1][b - c_i] + d_i\big) & \text{si } c_i \le b
  \end{cases}$$
* **Fase 1 (Llenado):** Construye una matriz de dimensiones $(n+1) \times (B+1)$ evaluando todas las combinaciones posibles en $\Theta(n \cdot B)$ operaciones elementales.
* **Fase 2 (Backtracking):** Desciende desde $(n, B)$ hasta la fila $0$ determinando si cada etapa $i$ fue elegida ($x_i = 1$) o descartada ($x_i = 0$), documentando el motivo exacto de la decisión.
* **Complejidad:**
  * **Temporal:** $\Theta(n \cdot B)$ operaciones.
  * **Espacial:** $\Theta(n \cdot B)$ celdas enteras para permitir el backtracking determinista.

### 3.2. Cobertura Mínima de Auditoría - Voraz Estándar (`auditoria_voraz.py`)
* **Problema Equivalente:** Cobertura de Conjuntos (Set Cover cardinal).
* **Objetivo:** Minimizar la cantidad total de interacciones seleccionadas ($\min |Y|$) sujetas a $\bigcup_{S_j \in Y} S_j = U$.
* **Criterio de Selección:** En cada iteración $k$, elige la interacción $S^*$ que cubra el mayor número de riesgos que aún permanecen descubiertos:
  $$S^* = \arg\max_{S_j} |S_j \cap U_{restante}|$$
* **Desempate:** Mayor cantidad de riesgos nuevos; ante empate, menor ID lexicográfico.
* **Complejidad Temporal:** $\mathcal{O}(n \cdot r^2)$ en el peor caso ($r = |U|$).

### 3.3. Cobertura Ponderada por Costo - Variante 1 (`auditoria_ponderada.py`)
* **Problema Equivalente:** Weighted Set Cover (Chvátal 1979).
* **Objetivo:** Minimizar el costo económico total de la auditoría ($\min \sum_{j} w_j y_j$).
* **Criterio de Selección:** En cada iteración $k$, selecciona la interacción que minimice el ratio de costo por cada nuevo riesgo mitigado:
  $$S^* = \arg\min_{\substack{S_j \\ |S_j \cap U_{restante}| > 0}} \frac{w_j}{|S_j \cap U_{restante}|}$$
* **Garantía Teórica de Aproximación:** Cota armónica $H_r \cdot OPT$, donde $H_r = \sum_{k=1}^r \frac{1}{k} \le \ln(r) + 1$.
* **Complejidad Temporal:** $\mathcal{O}(n \cdot r^2)$.

---

## 4. Esquemas JSON de Entrada y Salida

### 4.1. Formato Oficial de la Profesora (`data/casos/*.json`)
El deserializador en `io_handler.py` interpreta automáticamente el formato extendido:
```json
{
  "parametros": {
    "numero_etapas": 20,
    "presupuesto_aceleracion_B": 72,
    "presupuesto_conjunto_aceleracion_y_auditoria": 100,
    "numero_categorias_riesgo": 12
  },
  "flujo": [
    { "origen": "E01", "destino": "E02" }
  ],
  "categorias_riesgo": [
    { "id": "R01", "categoria": "sesgo", "importancia": 4 }
  ],
  "etapas": [
    {
      "id": "E01",
      "duracion_normal": 18,
      "costo_aceleracion": 7,
      "reduccion_tiempo_si_acelera": 5,
      "variaciones_auditoria": [
        {
          "id": "parcial",
          "costo": 3,
          "riesgos_cubiertos": ["R01", "R02"]
        },
        {
          "id": "completa",
          "costo": 6,
          "riesgos_cubiertos": ["R01", "R02", "R03", "R10"]
        }
      ]
    }
  ]
}
```

### 4.2. Formato de Salida Exportado (`data/resultados/*_resultado.json`)
Cada ejecución genera un archivo de salida enriquecido con métricas y trazas cronológicas:
```json
{
  "id_caso": "entrada_G3_mochila_20_nodos",
  "timestamp_utc": "2026-11-05T20:30:12.123456+00:00",
  "tiempos_ejecucion_segundos": {
    "aceleracion_dp_segundos": 0.0002242,
    "auditoria_voraz_segundos": 0.0001741,
    "auditoria_ponderada_segundos": 0.0002854,
    "total_ejecucion_segundos": 0.0006837
  },
  "aceleracion_dp": {
    "ahorro_optimo": 55,
    "duracion_original_total": 501,
    "duracion_final_total": 446,
    "presupuesto_total": 72,
    "presupuesto_usado": 72,
    "presupuesto_remanente": 0,
    "etapas_aceleradas": [
      { "id": "E02", "costo": 12, "reduccion": 9 },
      { "id": "E03", "costo": 5, "reduccion": 4 },
      { "id": "E04", "costo": 16, "reduccion": 12 },
      { "id": "E06", "costo": 13, "reduccion": 10 },
      { "id": "E08", "costo": 17, "reduccion": 13 },
      { "id": "E12", "costo": 9, "reduccion": 7 }
    ],
    "vector_decision_binario": [0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    "traza_decisiones": [ ... ]
  },
  "auditoria_voraz": {
    "metodo": "voraz_estandar",
    "cardinalidad_cobertura": 4,
    "costo_total": 29.0,
    "interacciones_seleccionadas": ["E01_completa", "E16_completa", "E06_completa", "E03_completa"],
    "es_cobertura_completa": true,
    "traza_paso_a_paso": [ ... ]
  },
  "auditoria_ponderada": {
    "metodo": "voraz_ponderado",
    "cardinalidad_cobertura": 4,
    "costo_total": 26.0,
    "interacciones_seleccionadas": ["E01_completa", "E16_completa", "E06_completa", "E03_parcial"],
    "es_cobertura_completa": true,
    "traza_paso_a_paso": [ ... ]
  }
}
```

---

## 5. Instrucciones de Uso y Comandos CLI

Para ejecutar la solución, abre una terminal en la raíz de `Proyecto-ADA`:


### 5.1. Ejecutar Caso Oficial
```powershell
python main.py --input data/casos/entrada_G3_mochila_20_nodos.json
```

### 5.2. Ejecutar con Traza Detallada en Pantalla (`--verbose`)
Muestra el motivo exacto de decisión de cada etapa evaluada en DP y el cálculo de ratios paso a paso en Set Cover:
```powershell
python main.py --input data/casos/entrada_G3_mochila_20_nodos.json --verbose
```

### 5.3. Procesar un Directorio Completo por Lotes
```powershell
python main.py --input data/casos --output-dir data/resultados
```

### 5.4. Ver Ayuda de Argumentos
```powershell
python main.py --help
```

---

## 6. Resultados y Verificación del Caso Oficial

Al ejecutar el pipeline sobre `entrada_G3_mochila_20_nodos.json`, se obtienen los siguientes resultados certificados:

| Algoritmo | Métrica Principal | Costo Incurrido | Tiempo |
| :--- | :--- | :---: | :---: |
| **Aceleración DP** | Ahorro: **55 u** (Duración: 501 $\to$ 446) | **72 / 72** | ~0.22 ms |
| **Auditoría Estándar** | 4 interacciones (12/12 riesgos cubiertos) | **$29.00** | ~0.17 ms |
| **Auditoría Ponderada** | 4 interacciones (12/12 riesgos cubiertos) | **$26.00** (-$3) | ~0.29 ms |

### Impacto en el Presupuesto Conjunto ($B_{conjunto} \le 100$):
* **Con Auditoría Estándar:** $72 + 29 = \mathbf{101.00}$ $\implies$ **EXCEDE** (Infactible).
* **Con Auditoría Ponderada:** $72 + 26 = \mathbf{98.00}$ $\implies$ **CUMPLE** (Margen libre: 2.00).

---

## 7. Limitaciones del Sistema y Escalabilidad

1. **Naturaleza Pseudo-Polinomial de DP:** La tabla de memoria utiliza $(n+1) \times (B+1)$ celdas. Para valores de $B$ moderados (como $B=72$), toma fracciones de milisegundo. Si el presupuesto se expresara en centavos o magnitudes astronómicas ($B \ge 10^7$), la memoria física se saturaría; en tales casos se requerirían esquemas de aproximación FPTAS o discretización de escala.
2. **Heurística Voraz:** Aunque Set Cover es NP-difícil y el algoritmo voraz no siempre alcanza el óptimo mínimo global, la cota armónica $H_r \le \ln(r) + 1$ garantiza formalmente la mejor cota teóricamente posible en tiempo polinomial (Feige, 1998).
3. **Flujos en Serie:** El modelo actual optimiza cadenas secuenciales lineales donde todas las etapas forman parte del camino crítico. En flujos con ramificaciones paralelas o grafos DAG generales, se requerirá extender el modelo con ordenamiento topológico y cálculo de rutas críticas dinámicas.
