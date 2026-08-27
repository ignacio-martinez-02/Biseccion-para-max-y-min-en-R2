"""
Pruebas unitarias para el módulo de bisección visual
"""

import unittest
import numpy as np
from biseccion import parsear_funcion, generar_pasos_biseccion, dataframe_iteraciones, verificacion_interna_silenciosa


class TestBiseccion(unittest.TestCase):

    def test_parabola_minimo(self):
        # f(x) = (x - 3)^2 + 2, mínimo en x=3, y=2
        sym_expr, x_sym, f_num = parsear_funcion("(x - 3)^2 + 2")
        pasos = generar_pasos_biseccion(f_num, 0.0, 5.0, tipo="minimo")
        
        ultimo = pasos[-1]
        x_calc = (ultimo["nuevo_a"] + ultimo["nuevo_b"]) / 2.0
        y_calc = float(f_num(x_calc))
        
        self.assertAlmostEqual(x_calc, 3.0, places=2)
        self.assertAlmostEqual(y_calc, 2.0, places=2)
        self.assertTrue(verificacion_interna_silenciosa(sym_expr, x_sym, 0.0, 5.0, x_calc, tipo="minimo"))

    def test_trigonometrica_maximo(self):
        # f(x) = sin(x), máximo en x=pi/2 ~ 1.570796 en [0, pi]
        sym_expr, x_sym, f_num = parsear_funcion("sin(x)")
        pasos = generar_pasos_biseccion(f_num, 0.0, np.pi, tipo="maximo")
        
        ultimo = pasos[-1]
        x_calc = (ultimo["nuevo_a"] + ultimo["nuevo_b"]) / 2.0
        y_calc = float(f_num(x_calc))
        
        self.assertAlmostEqual(x_calc, np.pi / 2.0, places=2)
        self.assertAlmostEqual(y_calc, 1.0, places=2)
        self.assertTrue(verificacion_interna_silenciosa(sym_expr, x_sym, 0.0, np.pi, x_calc, tipo="maximo"))

    def test_dataframe_limpio(self):
        sym_expr, x_sym, f_num = parsear_funcion("x^2")
        pasos = generar_pasos_biseccion(f_num, -2.0, 2.0, tipo="minimo")
        df = dataframe_iteraciones(pasos)
        
        # Verificar que no contenga columnas de errores o técnicas
        self.assertIn("Iteración", df.columns)
        self.assertIn("Intervalo [a, b]", df.columns)
        self.assertIn("Punto Medio (m)", df.columns)
        self.assertIn("Valor f(m)", df.columns)
        self.assertIn("Decisión", df.columns)
        self.assertNotIn("Error", " ".join(df.columns))
        self.assertNotIn("Tolerancia", " ".join(df.columns))


if __name__ == "__main__":
    unittest.main()
