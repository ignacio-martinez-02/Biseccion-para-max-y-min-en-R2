"""
Aplicación Web Minimalista para Búsqueda Visual de Extremos por Bisección
Con Teclado GeoGebra, Escalado Gráfico Adaptativo y Persistencia Robusta de Estado
Análisis Matemático 1 - Tutorías
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import sympy as sp
import streamlit.components.v1 as components
from biseccion import parsear_funcion, generar_pasos_biseccion, dataframe_iteraciones, verificacion_interna_silenciosa

# Configuración de página
st.set_page_config(
    page_title="Búsqueda de Extremos por Bisección",
    page_icon="📈",
    layout="centered"
)

# Inyección de CSS Minimalista
st.markdown("""
<style>
    .main {
        background-color: #fafafa;
    }
    .stApp {
        max-width: 880px;
        margin: 0 auto;
    }
    .main-title {
        text-align: center;
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 6px;
        margin-bottom: 4px;
    }
    .subtitle {
        text-align: center;
        font-size: 1.02rem;
        color: #475569;
        margin-bottom: 20px;
    }
    .step-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        margin: 10px 0 16px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    .step-badge {
        display: inline-block;
        background: #eff6ff;
        color: #1d4ed8;
        font-weight: 700;
        font-size: 0.88rem;
        padding: 4px 12px;
        border-radius: 16px;
        margin-bottom: 8px;
    }
    .final-badge {
        background: #ecfdf5;
        color: #065f46;
        font-weight: 700;
        font-size: 1.15rem;
        padding: 12px 20px;
        border-radius: 10px;
        border: 1px solid #a7f3d0;
        text-align: center;
        margin-top: 12px;
    }
    .keyboard-box {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 8px 10px;
        margin-top: 4px;
        margin-bottom: 12px;
    }
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# JavaScript para capturar la tecla Enter y avanzar iteraciones
def escuchar_enter():
    components.html("""
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const nextBtn = doc.querySelector('button[kind="primary"]');
            if (nextBtn) {
                nextBtn.click();
            }
        }
    });
    </script>
    """, height=0, width=0)

# Callbacks para el teclado virtual
def insertar_token(token: str):
    if "input_texto_widget" not in st.session_state:
        st.session_state["input_texto_widget"] = ""
    st.session_state["input_texto_widget"] += token

def borrar_token():
    if "input_texto_widget" in st.session_state and st.session_state["input_texto_widget"]:
        cur = st.session_state["input_texto_widget"]
        for t in ["sqrt(", "sin(", "cos(", "tan(", "log(", "exp(", "abs(", "sen(", "ln("]:
            if cur.endswith(t):
                st.session_state["input_texto_widget"] = cur[:-len(t)]
                return
        st.session_state["input_texto_widget"] = cur[:-1]

def limpiar_input():
    st.session_state["input_texto_widget"] = ""

# Inicialización de Estados Persistentes (independientes de widgets)
if "estado_app" not in st.session_state:
    st.session_state["estado_app"] = "pantalla_inicial"
if "input_texto_widget" not in st.session_state:
    st.session_state["input_texto_widget"] = "50000*sqrt(x²+0.25)+30000(2-x)"
if "funcion_activa" not in st.session_state:
    st.session_state["funcion_activa"] = "50000*sqrt(x²+0.25)+30000(2-x)"
if "tipo_activo" not in st.session_state:
    st.session_state["tipo_activo"] = "Mínimo"
if "a_activo" not in st.session_state:
    st.session_state["a_activo"] = 0.0
if "b_activo" not in st.session_state:
    st.session_state["b_activo"] = 2.0
if "iter_actual" not in st.session_state:
    st.session_state["iter_actual"] = 0
if "pasos_activos" not in st.session_state:
    st.session_state["pasos_activos"] = []
if "ver_teclado" not in st.session_state:
    st.session_state["ver_teclado"] = True


# ==============================================================================
# PANTALLA 1: INGRESO DE DATOS
# ==============================================================================
if st.session_state["estado_app"] == "pantalla_inicial":
    st.markdown('<div class="main-title">📐 Búsqueda de Extremos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ingresá la función, el intervalo y el extremo a buscar para iniciar el análisis visual.</div>', unsafe_allow_html=True)
    
    # Campo de texto para la función
    st.text_input(
        "Función f(x):",
        key="input_texto_widget",
        help="Escribí la función usando el teclado físico o el teclado en pantalla."
    )
    
    # Teclado en pantalla
    st.session_state["ver_teclado"] = st.toggle("⌨️ Teclado en pantalla", value=st.session_state["ver_teclado"])
    if st.session_state["ver_teclado"]:
        st.markdown('<div class="keyboard-box">', unsafe_allow_html=True)
        tab_123, tab_fx = st.tabs(["123 (Números y Operaciones)", "f(x) (Funciones)"])
        with tab_123:
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("x", on_click=insertar_token, args=("x",), use_container_width=True)
            c2.button("x²", on_click=insertar_token, args=("²",), use_container_width=True)
            c3.button("xⁿ", on_click=insertar_token, args=("^",), use_container_width=True)
            c4.button("√", on_click=insertar_token, args=("sqrt(",), use_container_width=True)
            c5.button("π", on_click=insertar_token, args=("pi",), use_container_width=True)
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("7", on_click=insertar_token, args=("7",), use_container_width=True)
            c2.button("8", on_click=insertar_token, args=("8",), use_container_width=True)
            c3.button("9", on_click=insertar_token, args=("9",), use_container_width=True)
            c4.button("÷", on_click=insertar_token, args=("/",), use_container_width=True)
            c5.button("⌫", on_click=borrar_token, use_container_width=True)
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("4", on_click=insertar_token, args=("4",), use_container_width=True)
            c2.button("5", on_click=insertar_token, args=("5",), use_container_width=True)
            c3.button("6", on_click=insertar_token, args=("6",), use_container_width=True)
            c4.button("×", on_click=insertar_token, args=("*",), use_container_width=True)
            c5.button("C", on_click=limpiar_input, use_container_width=True)
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("1", on_click=insertar_token, args=("1",), use_container_width=True)
            c2.button("2", on_click=insertar_token, args=("2",), use_container_width=True)
            c3.button("3", on_click=insertar_token, args=("3",), use_container_width=True)
            c4.button("−", on_click=insertar_token, args=("-",), use_container_width=True)
            c5.button("(", on_click=insertar_token, args=("(",), use_container_width=True)
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("0", on_click=insertar_token, args=("0",), use_container_width=True)
            c2.button(".", on_click=insertar_token, args=(".",), use_container_width=True)
            c3.button("|x|", on_click=insertar_token, args=("abs(",), use_container_width=True)
            c4.button("+", on_click=insertar_token, args=("+",), use_container_width=True)
            c5.button(")", on_click=insertar_token, args=(")",), use_container_width=True)
            
        with tab_fx:
            f1, f2, f3 = st.columns(3)
            f1.button("sin( )", on_click=insertar_token, args=("sin(",), use_container_width=True)
            f2.button("cos( )", on_click=insertar_token, args=("cos(",), use_container_width=True)
            f3.button("tan( )", on_click=insertar_token, args=("tan(",), use_container_width=True)
            
            f1, f2, f3 = st.columns(3)
            f1.button("ln( )", on_click=insertar_token, args=("log(",), use_container_width=True)
            f2.button("eˣ", on_click=insertar_token, args=("exp(",), use_container_width=True)
            f3.button("1/x", on_click=insertar_token, args=("1/(",), use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Intervalo
    st.markdown("**Intervalo de análisis:**")
    col_a, col_b = st.columns(2)
    with col_a:
        a_in = st.number_input("Desde (a):", value=float(st.session_state["a_activo"]), step=0.5, format="%.4f")
    with col_b:
        b_in = st.number_input("Hasta (b):", value=float(st.session_state["b_activo"]), step=0.5, format="%.4f")
        
    # Extremo a buscar
    tipo_in = st.radio(
        "Extremo a hallar:",
        options=["Mínimo", "Máximo"],
        horizontal=True,
        index=0 if st.session_state["tipo_activo"] == "Mínimo" else 1
    )
    
    # Botón para graficar e iniciar
    if st.button("Graficar función (Enter)", type="primary", use_container_width=True):
        if a_in >= b_in:
            st.error("El extremo 'Desde (a)' debe ser menor que 'Hasta (b)'.")
        else:
            try:
                texto_func = st.session_state["input_texto_widget"].strip()
                sym_expr, x_sym, f_num = parsear_funcion(texto_func)
                pasos = generar_pasos_biseccion(f_num, a_in, b_in, tipo=tipo_in.lower())
                
                # Guardar en estados permanentes
                st.session_state["funcion_activa"] = texto_func
                st.session_state["a_activo"] = a_in
                st.session_state["b_activo"] = b_in
                st.session_state["tipo_activo"] = tipo_in
                st.session_state["pasos_activos"] = pasos
                st.session_state["iter_actual"] = 0
                st.session_state["estado_app"] = "graficada"
                st.rerun()
            except Exception as e:
                st.error(f"Error en la función: {e}")


# ==============================================================================
# PANTALLA 2: GRÁFICA E ITERACIONES PASO A PASO
# ==============================================================================
else:
    escuchar_enter()
    
    # Recuperación de los datos persistentes activos
    expr_str = st.session_state["funcion_activa"]
    a_init = float(st.session_state["a_activo"])
    b_init = float(st.session_state["b_activo"])
    tipo_ext = st.session_state["tipo_activo"]
    pasos = st.session_state["pasos_activos"]
    idx = st.session_state["iter_actual"]
    total_pasos = len(pasos)
    
    # Parsear función activa
    sym_expr, x_sym, f_num = parsear_funcion(expr_str)
    
    # Encabezado compacto
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"### Función: $f(x) = {sp.latex(sym_expr)}$")
        st.markdown(f"**Buscando:** {tipo_ext} en $[{a_init:.4f}, {b_init:.4f}]$")
    with col_t2:
        if st.button("🔄 Nueva función", use_container_width=True):
            st.session_state["estado_app"] = "pantalla_inicial"
            st.session_state["iter_actual"] = 0
            st.session_state["input_texto_widget"] = st.session_state["funcion_activa"]
            st.rerun()

    # Intervalo actual según la iteración
    if idx == 0:
        a_curr, b_curr = a_init, b_init
    else:
        paso_actual = pasos[idx - 1]
        a_curr, b_curr = paso_actual["a"], paso_actual["b"]

    # Selector de modo de vista para el gráfico
    modo_zoom = st.radio(
        "Visualización:",
        options=["🔍 Zoom al intervalo de la iteración", "🌐 Vista general completa [a, b]"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Determinación del rango de graficación en X
    if modo_zoom.startswith("🔍") and idx > 0:
        margen_x = max((b_curr - a_curr) * 0.20, 1e-4)
        x_min_plot = a_curr - margen_x
        x_max_plot = b_curr + margen_x
    else:
        margen_x = (b_init - a_init) * 0.05
        x_min_plot = a_init - margen_x
        x_max_plot = b_init + margen_x

    # Muestreo fino de puntos
    xs = np.linspace(x_min_plot, x_max_plot, 1000)
    try:
        ys = f_num(xs)
        if np.isscalar(ys):
            ys = np.full_like(xs, ys)
    except Exception:
        ys = np.array([f_num(x) for x in xs])
        
    # Auto-escalado vertical óptimo
    y_vis_min = float(np.nanmin(ys))
    y_vis_max = float(np.nanmax(ys))
    delta_y = y_vis_max - y_vis_min
    
    if delta_y <= 1e-9:
        y_pad = 1.0
    else:
        y_pad = delta_y * 0.10
        
    y_range = [y_vis_min - y_pad, y_vis_max + y_pad]

    fig = go.Figure()
    
    # 1. Curva principal
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode='lines',
        name='f(x)',
        line=dict(color='#2563eb', width=2.8)
    ))
    
    # 2. Zona sombreada del intervalo actual
    fig.add_vrect(
        x0=a_curr, x1=b_curr,
        fillcolor="rgba(59, 130, 246, 0.12)",
        layer="below",
        line_width=1.5,
        line_color="#3b82f6",
        annotation_text=f"[{a_curr:.4f}, {b_curr:.4f}]",
        annotation_position="top left"
    )
    
    # 3. Puntos de análisis de la iteración
    if idx > 0:
        paso_actual = pasos[idx - 1]
        m_val = paso_actual["m"]
        fm_val = paso_actual["f_m"]
        
        # Punto medio m
        fig.add_trace(go.Scatter(
            x=[m_val], y=[fm_val],
            mode='markers+text',
            name='Punto medio (m)',
            text=[f'm = {m_val:.4f}'],
            textposition="top center",
            marker=dict(color='#f59e0b', size=11, symbol='circle', line=dict(color='#ffffff', width=1.5))
        ))
        
        # Puntos de sondeo
        fig.add_trace(go.Scatter(
            x=[paso_actual["x1"], paso_actual["x2"]],
            y=[paso_actual["f_x1"], paso_actual["f_x2"]],
            mode='markers',
            name='Sondeo',
            marker=dict(color='#10b981', size=7, symbol='diamond')
        ))
        
    # 4. Si llegó al final, marcar el extremo definitivo
    if idx >= total_pasos:
        ultimo = pasos[-1]
        x_fin = (ultimo["nuevo_a"] + ultimo["nuevo_b"]) / 2.0
        y_fin = float(f_num(x_fin))
        
        verificacion_interna_silenciosa(sym_expr, x_sym, a_init, b_init, x_fin, tipo=tipo_ext.lower())
        
        fig.add_trace(go.Scatter(
            x=[x_fin], y=[y_fin],
            mode='markers+text',
            name=f'{tipo_ext} hallado',
            text=[f'{tipo_ext}: ({x_fin:.4f}, {y_fin:.2f})'],
            textposition="bottom center",
            marker=dict(color='#dc2626', size=15, symbol='star', line=dict(color='#ffffff', width=1.5))
        ))
        
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=40, r=30, t=30, b=35),
        xaxis=dict(
            title="x",
            range=[x_min_plot, x_max_plot],
            autorange=False,
            zeroline=False,
            gridcolor="#f1f5f9"
        ),
        yaxis=dict(
            title="f(x)",
            range=y_range,
            autorange=False,
            zeroline=False,
            gridcolor="#f1f5f9"
        ),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Información del estado del análisis
    if idx == 0:
        st.markdown("""
        <div class="step-card">
            <span class="step-badge">Paso inicial</span>
            <p style="margin: 0; color: #374151;">Función graficada en el intervalo inicial con auto-escalado adaptado. Presioná <b>Enter</b> o el botón a continuación para comenzar la bisección paso a paso.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Realizar primera iteración (Enter) ➔", type="primary", use_container_width=True):
            st.session_state["iter_actual"] = 1
            st.rerun()
            
    elif idx < total_pasos:
        paso_actual = pasos[idx - 1]
        st.markdown(f"""
        <div class="step-card">
            <span class="step-badge">Iteración {idx} de {total_pasos}</span>
            <div style="font-size: 1.05rem; font-weight: 600; color: #1f2937; margin-bottom: 4px;">
                Intervalo actual: [{paso_actual['a']:.4f}, {paso_actual['b']:.4f}]
            </div>
            <p style="margin: 0; color: #4b5563;">
                Punto medio: <b>m = {paso_actual['m']:.4f}</b> &nbsp;|&nbsp; <b>f(m) = {paso_actual['f_m']:.4f}</b><br>
                <b>Análisis visual:</b> {paso_actual['decision']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            if st.button(f"Siguiente iteración (Enter) ➔", type="primary", use_container_width=True):
                st.session_state["iter_actual"] += 1
                st.rerun()
        with col_btn2:
            if st.button("Ir al final", use_container_width=True):
                st.session_state["iter_actual"] = total_pasos
                st.rerun()
                
    else:
        # Finalizado
        ultimo = pasos[-1]
        x_fin = (ultimo["nuevo_a"] + ultimo["nuevo_b"]) / 2.0
        y_fin = float(f_num(x_fin))
        
        st.markdown(f"""
        <div class="final-badge">
            🎯 ¡{tipo_ext} alcanzado!<br>
            <span style="font-size: 1.25rem;">(x, y) = ({x_fin:.4f}, {y_fin:.4f})</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📋 Registro de todas las iteraciones realizadas:")
        df_pasos = dataframe_iteraciones(pasos)
        st.dataframe(
            df_pasos.style.format({
                "Punto Medio (m)": "{:.4f}",
                "Valor f(m)": "{:.4f}"
            }),
            use_container_width=True
        )
        
        if st.button("Realizar otro análisis", type="primary", use_container_width=True):
            st.session_state["estado_app"] = "pantalla_inicial"
            st.session_state["iter_actual"] = 0
            st.session_state["input_texto_widget"] = st.session_state["funcion_activa"]
            st.rerun()
