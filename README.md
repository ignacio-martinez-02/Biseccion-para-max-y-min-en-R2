# TP3 - Búsqueda de Extremos por Bisección y Análisis Visual

Aplicación interactiva y minimalista para hallar extremos (máximo o mínimo) de una función en un intervalo mediante el **Método de Bisección** y el **análisis visual** paso a paso.

---

## ✨ Características y Flujo de Uso

1. **Pantalla Inicial**:
   - Ingreso exclusivo de la **Función $f(x)$** (con teclado matemático interactivo estilo GeoGebra en pantalla o teclado físico).
   - Definición del **Intervalo $[a, b]$** (Desde $a$, Hasta $b$).
   - Selección del objetivo: **Mínimo** o **Máximo**.

2. **Gráfica Inicial al presionar `[Enter]`**:
   - Al presionar `Enter` o el botón principal, la función se grafica automáticamente en el intervalo establecido.

3. **Iteraciones Paso a Paso con `[Enter]`**:
   - Con cada pulsación de la tecla `[Enter]`, el algoritmo avanza una iteración:
     - Resalta visualmente el intervalo actual y el punto medio $m$.
     - Muestra la decisión visual de qué subintervalo se conserva y cuál se descarta.
     - Continúa hasta converger en el extremo deseado $(x, y)$.

4. **Interfaz Minimalista y Limpia**:
   - No se muestran datos técnicos de error, tolerancias ni especificaciones internas.
   - Sin mención a derivadas en la interfaz (el método se fundamenta en la bisección y el análisis visual de la curva, mientras que la comprobación interna se realiza de forma silenciosa).

---

## 🚀 Cómo Ejecutar la Aplicación Web

```bash
source .venv/bin/activate
streamlit run app.py
```

### Ejecución en Consola (CLI)
```bash
source .venv/bin/activate
python3 main.py
```
