# Proyecto Semestral ADAG — Grupo 3 (Ruta)
## Primera Entrega: Optimización de Cadena en Serie y Cobertura de Auditoría

**Integrantes:**
* Juan José Hernández Velásquez
* Victor Manuel Valencia Alvarez

---

### Descripción del Proyecto
Este repositorio contiene la solución algorítmica formal y ejecutable para la Primera Entrega del curso **Análisis y Diseño de Algoritmos (ADAG)**. El sistema aborda dos problemáticas de optimización desacopladas:
1. **Aceleración Óptima bajo Presupuesto:** Minimizar la duración total de un flujo en serie de $n$ etapas sujeto a un presupuesto financiero $B$ mediante **Programación Dinámica (Mochila 0/1)** en tiempo $\Theta(n \cdot B)$.
2. **Cobertura Mínima de Auditoría:** Mitigar el 100% de los riesgos normativos del sistema seleccionando el subconjunto óptimo de interacciones mediante **Algoritmos Voraces (Set Cover)**:
   * **Caso Estándar:** Minimiza la cantidad de auditorías (cardinalidad).
   * **Variante 1 Ponderada (Chvátal 1979):** Minimiza el costo monetario total con garantía armónica de aproximación $H_r \le \ln(r) + 1$.

---

### Requisitos y Ejecución Rápida
No requiere dependencias externas obligatorias para la ejecución base (utiliza la biblioteca estándar de Python 3.10+).

```powershell
# 1. Clonar o ubicarse en la raíz del repositorio
cd "C:\Users\lina\Desktop\2026-2\ADA\Proyecto-ADA"

# 2. Ejecutar el caso de prueba oficial de la profesora
python main.py --input data/casos/entrada_G3_mochila_20_nodos.json

# 3. Ejecutar con traza detallada paso a paso en consola
python main.py --input data/casos/entrada_G3_mochila_20_nodos.json --verbose
```

---

### Documentación Entregada
* 📄 **Informe Técnico Formal:** [`docs/Informe_Tecnico.pdf`](docs/Informe_Tecnico.pdf) (17 páginas con formalización matemática, demostraciones de NP-dureza por reducción, análisis de complejidad asintótica y resultados oficiales).
* 📘 **Manual Técnico:** [`docs/Manual_Tecnico.md`](docs/Manual_Tecnico.md) (arquitectura de software, esquemas JSON, instrucciones de CLI y limitaciones del sistema).
