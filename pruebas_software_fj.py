# -*- coding: utf-8 -*-
"""
Pruebas automáticas de Software FJ (Fase 4 - Programación 213023).

Verifican que las validaciones y las excepciones personalizadas funcionen
y que el sistema siga operando cuando ocurren errores.

Cómo ejecutarlas (en la misma carpeta que software_fj.py):
    python pruebas_software_fj.py
"""

import logging
import unittest

import software_fj as fj  # Módulo principal del proyecto

logging.disable(logging.CRITICAL)  # Evita llenar el archivo de logs durante las pruebas


class PruebasCliente(unittest.TestCase):
    """Validaciones de la clase Cliente."""

    def test_cliente_valido(self):
        cliente = fj.Cliente("ana perez", "Ana@Correo.com", "3101234567")
        self.assertEqual(cliente.nombre, "Ana Perez")        # Nombre normalizado
        self.assertEqual(cliente.correo, "ana@correo.com")   # Correo en minúsculas

    def test_correo_invalido(self):
        with self.assertRaises(fj.ClienteInvalidoError):
            fj.Cliente("Luis Gomez", "luis-correo.com", "3101234567")

    def test_telefono_invalido(self):
        with self.assertRaises(fj.ClienteInvalidoError):
            fj.Cliente("Luis Gomez", "luis@correo.com", "12345")

    def test_nombre_con_numeros(self):
        with self.assertRaises(fj.ClienteInvalidoError):
            fj.Cliente("Luis 123", "luis@correo.com", "3101234567")


class PruebasServicios(unittest.TestCase):
    """Servicios especializados, polimorfismo y cálculo de costos."""

    def setUp(self):
        self.sala = fj.ReservaSala("Sala", 50000, 10)
        self.equipo = fj.AlquilerEquipo("Portátil", 8000, "Computador")
        self.asesoria = fj.Asesoria("Redes", 90000, "Redes", nivel_experto=True)

    def test_servicio_abstracto_no_se_instancia(self):
        with self.assertRaises(TypeError):
            fj.Servicio("X", 1000)

    def test_costo_con_iva_por_defecto(self):
        self.assertEqual(self.sala.calcular_costo(2), 119000.0)

    def test_costo_sin_impuesto(self):
        self.assertEqual(self.sala.calcular_costo(2, impuesto=0), 100000.0)

    def test_costo_con_descuento(self):
        self.assertEqual(self.sala.calcular_costo(2, impuesto=0, descuento=0.10), 90000.0)

    def test_polimorfismo_costos_distintos(self):
        costos = {s.calcular_costo(2) for s in (self.sala, self.equipo, self.asesoria)}
        self.assertEqual(len(costos), 3)  # Cada servicio calcula con su propia regla

    def test_tarifa_negativa(self):
        with self.assertRaises(fj.ServicioInvalidoError):
            fj.ReservaSala("Sala", -100, 5)

    def test_horas_fuera_de_rango(self):
        with self.assertRaises(fj.ServicioInvalidoError):
            self.sala.calcular_costo(20)

    def test_descuento_inconsistente(self):
        with self.assertRaises(fj.CalculoInconsistenteError):
            self.sala.calcular_costo(2, descuento=1.5)


class PruebasReservas(unittest.TestCase):
    """Reserva: confirmación, cancelación y encadenamiento de excepciones."""

    def setUp(self):
        self.cliente = fj.Cliente("Carlos Ruiz", "carlos@correo.com", "3157654321")
        self.sala = fj.ReservaSala("Sala", 50000, 10)

    def test_reserva_se_procesa(self):
        reserva = fj.Reserva(self.cliente, self.sala, 3)
        costo = reserva.procesar(descuento=0.10)
        self.assertEqual(reserva.estado, "CONFIRMADA")
        self.assertEqual(costo, 160650.0)

    def test_duracion_invalida_encadena_excepcion(self):
        with self.assertRaises(fj.ReservaInvalidaError) as contexto:
            fj.Reserva(self.cliente, self.sala, 20)
        self.assertIsInstance(contexto.exception.__cause__, fj.ServicioInvalidoError)

    def test_servicio_no_disponible(self):
        self.sala.disponible = False
        reserva = fj.Reserva(self.cliente, self.sala, 2)
        with self.assertRaises(fj.ReservaInvalidaError) as contexto:
            reserva.procesar()
        self.assertIsInstance(contexto.exception.__cause__, fj.ServicioNoDisponibleError)

    def test_no_se_confirma_reserva_cancelada(self):
        reserva = fj.Reserva(self.cliente, self.sala, 2)
        reserva.cancelar()
        with self.assertRaises(fj.OperacionNoPermitidaError):
            reserva.confirmar()

    def test_no_se_cancela_dos_veces(self):
        reserva = fj.Reserva(self.cliente, self.sala, 2)
        reserva.cancelar()
        with self.assertRaises(fj.OperacionNoPermitidaError):
            reserva.cancelar()

    def test_reserva_con_cliente_invalido(self):
        with self.assertRaises(fj.ReservaInvalidaError):
            fj.Reserva(None, self.sala, 2)


class PruebasGestor(unittest.TestCase):
    """El gestor debe seguir funcionando aunque ocurran errores."""

    def test_gestor_continua_tras_errores(self):
        gestor = fj.GestorFJ()
        self.assertIsNone(gestor.registrar_cliente("Luis", "mal-correo", "123"))
        cliente = gestor.registrar_cliente("Ana Perez", "ana@correo.com", "3101234567")
        self.assertIsNotNone(cliente)
        self.assertEqual(len(gestor.clientes), 1)  # Solo el válido quedó registrado

    def test_procesar_reserva_inexistente_no_rompe(self):
        gestor = fj.GestorFJ()
        self.assertIsNone(gestor.procesar_reserva(None))

    def test_servicio_con_parametro_faltante(self):
        gestor = fj.GestorFJ()
        self.assertIsNone(gestor.registrar_servicio(fj.AlquilerEquipo, "Proyector", 12000))


if __name__ == "__main__":
    unittest.main(verbosity=2)
