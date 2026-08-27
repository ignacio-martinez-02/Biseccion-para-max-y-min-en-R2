"""
Script de consola CLI para Búsqueda Visual de Extremos por Bisección
Análisis Matemático 1 - Tutorías
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from biseccion import parsear_funcion, generar_pasos_biseccion, dataframe_iteraciones, verificacion_interna_silenciosa


def main():
    print("=" * 65)
    print("        BÚSQUEDA DE EXTREMOS POR BISECCIÓN Y ANÁLISIS VISUAL    ")
    print("=" * 65)
    
    # 1. Ingreso inicial
    try:
        expr_str = input("Función f(x) [def: x^2 - 4*x + 3]: ").strip()
        if not expr_str:
            expr_str = "x^2 - 4*x + 3"
            
        a_str = input("Límite inferior 'a' [def: 0.0]: ").strip()
        a_val = float(a_str) if a_str else 0.0
        
        b_str = input("Límite superior 'b' [def: 4.0]: ").strip()
        b_val = float(b_str) if b_str else 4.0
        
        tipo_str = input("Extremo a buscar ('min' / 'max') [def: min]: ").strip().lower()
        if not tipo_str or tipo_str.startswith('min'):
            tipo = "Mínimo"
        else:
            tipo = "Máximo"
            
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada.")
        sys.exit(0)
        
    try:
        sym_expr, x_sym, f_num = parsear_funcion(expr_str)
        pasos = generar_pasos_biseccion(f_num, a_val, b_val, tipo=tipo.lower(), sym_expr=sym_expr, x_sym=x_sym)
    except Exception as e:
        print(f"Error al interpretar los datos: {e}")
        sys.exit(1)
        
    # 2. Función graficada en el intervalo
    print("\n" + "-" * 65)
    print(f"✓ Función graficada en el intervalo [{a_val:.2f}, {b_val:.2f}]")
    print(f"  Objetivo: Hallar {tipo.upper()}")
    print("-" * 65)
    input("Presioná [Enter] para comenzar las iteraciones paso a paso...")
    
    # 3. Iteraciones paso a paso con Enter
    for p in pasos:
        print(f"\n--- Iteración {p['iteracion']} de {len(pasos)} ---")
        print(f"• Intervalo actual : {p['intervalo_str']}")
        print(f"• Punto medio (m)   : {p['m']:.4f}  |  f(m) = {p['f_m']:.4f}")
        print(f"• Análisis visual   : {p['decision']}")
        input("Presioná [Enter] para la siguiente iteración...")
        
    # 4. Resultado final
    ultimo = pasos[-1]
    x_fin = (ultimo["nuevo_a"] + ultimo["nuevo_b"]) / 2.0
    y_fin = float(f_num(x_fin))
    
    # Comprobación interna silenciosa
    verificacion_interna_silenciosa(sym_expr, x_sym, a_val, b_val, x_fin, tipo=tipo.lower())
    
    print("\n" + "=" * 65)
    print(f"🎯 ¡{tipo.upper()} ALCANZADO!")
    print(f"   Coordenadas del punto: (x, y) = ({x_fin:.4f}, {y_fin:.4f})")
    print("=" * 65)
    
    print("\n📋 Registro completo de iteraciones:")
    df = dataframe_iteraciones(pasos)
    print(df.to_string(index=False))
    
    # Guardar gráfico final
    try:
        xs = np.linspace(a_val, b_val, 500)
        ys = f_num(xs)
        if np.isscalar(ys):
            ys = np.full_like(xs, ys)
            
        fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
        ax.plot(xs, ys, color='#2563eb', linewidth=2.2, label=f'$f(x)$')
        ax.axvspan(a_val, b_val, color='#3b82f6', alpha=0.1, label=f'Intervalo [{a_val:.2f}, {b_val:.2f}]')
        ax.plot(x_fin, y_fin, marker='*', markersize=14, color='#dc2626', label=f'{tipo}: ({x_fin:.3f}, {y_fin:.3f})')
        ax.set_title(f"Búsqueda de {tipo} por Bisección", fontsize=13)
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        plt.tight_layout()
        plt.savefig("grafico_biseccion.png")
        print("\n📊 Gráfico guardado como 'grafico_biseccion.png'")
    except Exception:
        pass


if __name__ == "__main__":
    main()
