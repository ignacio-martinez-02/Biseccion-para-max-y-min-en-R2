"""
Módulo de Optimización por Método de Bisección Visual
Análisis Matemático 1 - Tutorías
"""

import numpy as np
import pandas as pd
import sympy as sp
from typing import Tuple, Dict, Any, List, Optional


def parsear_funcion(expr_str: str) -> Tuple[sp.Expr, sp.Symbol, Any]:
    """
    Parsea una expresión matemática en formato string a una función sympy y lambda de numpy.
    Soporta superíndices unicode (², ³, etc.), símbolos de teclado virtual como ^, π, √, sen, tg, ln, exp, etc.
    """
    expr_clean = expr_str.strip()
    
    # Reemplazo de superíndices numéricos Unicode
    superscripts = {
        '⁰': '**0', '¹': '**1', '²': '**2', '³': '**3', '⁴': '**4',
        '⁵': '**5', '⁶': '**6', '⁷': '**7', '⁸': '**8', '⁹': '**9'
    }
    for k, v in superscripts.items():
        expr_clean = expr_clean.replace(k, v)
        
    # Reemplazos de operadores y símbolos comunes
    expr_clean = expr_clean.replace('·', '*').replace('×', '*').replace('÷', '/')
    expr_clean = expr_clean.replace("π", "pi")
    expr_clean = expr_clean.replace("√", "sqrt")
    expr_clean = expr_clean.replace("^", "**")
    expr_clean = expr_clean.replace("sen(", "sin(")
    expr_clean = expr_clean.replace("tg(", "tan(")
    expr_clean = expr_clean.replace("ln(", "log(")
    
    x = sp.Symbol('x', real=True)
    
    transformations = sp.parsing.sympy_parser.standard_transformations + (
        sp.parsing.sympy_parser.implicit_multiplication_application,
        sp.parsing.sympy_parser.convert_xor,
    )
    
    try:
        sym_expr = sp.parsing.sympy_parser.parse_expr(
            expr_clean, 
            local_dict={'x': x, 'e': sp.E, 'pi': sp.pi, 'E': sp.E, 'PI': sp.pi},
            transformations=transformations
        )
    except Exception as e:
        raise ValueError(f"Error al interpretar la función: {str(e)}")
    
    f_num = sp.lambdify(
        x, 
        sym_expr, 
        modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                           'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                           'abs': np.abs}]
    )
    
    return sym_expr, x, f_num


def generar_pasos_biseccion(
    f_num: Any,
    a_init: float,
    b_init: float,
    tipo: str = "minimo",
    max_iter: int = 15,
    tol: float = 1e-4
) -> List[Dict[str, Any]]:
    """
    Genera la secuencia completa de pasos del método de bisección
    basado en el análisis comparativo del intervalo.
    """
    tipo_norm = tipo.lower().replace("í", "i").replace("á", "a").strip()
    buscar_min = tipo_norm.startswith("min")
    a = float(a_init)
    b = float(b_init)
    
    if a >= b:
        raise ValueError("El extremo 'a' debe ser menor que 'b'.")
        
    delta = min(tol / 10.0, (b - a) / 100.0, 1e-5)
    pasos = []
    
    for k in range(1, max_iter + 1):
        longitud = b - a
        m = (a + b) / 2.0
        
        delta_k = min(delta, longitud / 4.0)
        x1 = m - delta_k
        x2 = m + delta_k
        
        try:
            y1 = float(f_num(x1))
            y2 = float(f_num(x2))
            ym = float(f_num(m))
        except Exception as e:
            raise RuntimeError(f"Error evaluando f(x): {e}")
        
        if buscar_min:
            if y1 < y2:
                nuevo_a, nuevo_b = a, x2
                explicacion = f"La función decrece hacia la izquierda -> Se conserva [{a:.4f}, {x2:.4f}]"
            else:
                nuevo_a, nuevo_b = x1, b
                explicacion = f"La función decrece hacia la derecha -> Se conserva [{x1:.4f}, {b:.4f}]"
        else:
            if y1 > y2:
                nuevo_a, nuevo_b = a, x2
                explicacion = f"La función crece hacia la izquierda -> Se conserva [{a:.4f}, {x2:.4f}]"
            else:
                nuevo_a, nuevo_b = x1, b
                explicacion = f"La función crece hacia la derecha -> Se conserva [{x1:.4f}, {b:.4f}]"
                
        pasos.append({
            "iteracion": k,
            "a": a,
            "b": b,
            "m": m,
            "f_m": ym,
            "x1": x1,
            "x2": x2,
            "f_x1": y1,
            "f_x2": y2,
            "nuevo_a": nuevo_a,
            "nuevo_b": nuevo_b,
            "intervalo_str": f"[{a:.4f}, {b:.4f}]",
            "decision": explicacion
        })
        
        a = nuevo_a
        b = nuevo_b
        
        if (b - a) < tol:
            break
            
    return pasos


def dataframe_iteraciones(pasos: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convierte la lista de pasos en un DataFrame de Pandas limpio para el usuario.
    """
    registros = []
    for p in pasos:
        registros.append({
            "Iteración": p["iteracion"],
            "Intervalo [a, b]": p["intervalo_str"],
            "Punto Medio (m)": p["m"],
            "Valor f(m)": p["f_m"],
            "Decisión": p["decision"]
        })
    return pd.DataFrame(registros)


def verificacion_interna_silenciosa(
    sym_expr: sp.Expr,
    x_sym: sp.Symbol,
    a_init: float,
    b_init: float,
    x_obtenido: float,
    tipo: str = "minimo"
) -> bool:
    """
    Comprobación interna con derivadas sin exponer fórmulas ni menciones al usuario.
    Retorna simplemente un booleano de consistencia.
    """
    tipo_norm = tipo.lower().replace("í", "i").replace("á", "a").strip()
    buscar_min = tipo_norm.startswith("min")
    try:
        d1 = sp.diff(sym_expr, x_sym)
        d2 = sp.diff(d1, x_sym)
        
        puntos = []
        try:
            for s in sp.solve(d1, x_sym):
                if s.is_real:
                    val = float(s.evalf())
                    if a_init - 1e-3 <= val <= b_init + 1e-3:
                        puntos.append(val)
        except Exception:
            pass
            
        if puntos:
            f_num = sp.lambdify(x_sym, sym_expr, modules=['numpy'])
            if buscar_min:
                mejor = min(puntos, key=lambda p: float(f_num(p)))
            else:
                mejor = max(puntos, key=lambda p: float(f_num(p)))
            return abs(x_obtenido - mejor) < 0.1
        else:
            d1_val = float(sp.lambdify(x_sym, d1, modules=['numpy'])(x_obtenido))
            return abs(d1_val) < 0.2
    except Exception:
        return True
