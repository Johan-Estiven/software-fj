# -*- coding: utf-8 -*-
"""
Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
Curso: Programación (213023) - UNAD - Fase 4

Características:
- Programación orientada a objetos (abstracción, herencia, polimorfismo, encapsulación).
- Manejo avanzado de excepciones (personalizadas, try/except/else/finally, encadenamiento).
- Sin base de datos: todo se maneja con objetos y listas.
- Archivo de logs (software_fj.log) para eventos y errores.
- Simulación de 12 operaciones (válidas e inválidas) que no detienen el programa.
"""

import logging                      # Módulo estándar para escribir el archivo de logs
import re                           # Expresiones regulares para validar correo y teléfono
from abc import ABC, abstractmethod  # Herramientas para crear clases abstractas
from datetime import datetime       # Para marcar la fecha de creación de las reservas

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN DEL LOG
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="software_fj.log",      # Archivo donde se guardan eventos y errores
    level=logging.INFO,              # Nivel mínimo que se registra
    format="%(asctime)s | %(levelname)-8s | %(message)s",  # Formato de cada línea
    encoding="utf-8",                # Codificación para tildes y eñes
)
logger = logging.getLogger("SoftwareFJ")  # Logger propio del sistema


# ---------------------------------------------------------------------------
# 2. EXCEPCIONES PERSONALIZADAS
# ---------------------------------------------------------------------------
class SoftwareFJError(Exception):
    """Excepción base de todo el sistema; permite capturar cualquier error propio."""


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no son válidos."""


class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando los parámetros de un servicio no son válidos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio no disponible."""


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no se puede crear o procesar."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación no permitida por el estado actual."""


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce un resultado inconsistente."""


# ---------------------------------------------------------------------------
# 3. CLASE ABSTRACTA GENERAL
# ---------------------------------------------------------------------------
class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad general del sistema."""

    _contador = 0  # Contador de clase para generar identificadores únicos

    def __init__(self):
        Entidad._contador += 1                   # Incrementa el contador global
        self._id = Entidad._contador             # Identificador único (encapsulado)

    @property
    def id(self):
        """Devuelve el identificador de la entidad (solo lectura)."""
        return self._id

    @abstractmethod
    def describir(self):
        """Cada entidad debe describirse a sí misma (método abstracto)."""

    def __str__(self):
        return self.describir()                  # str() usa la descripción polimórfica


# ---------------------------------------------------------------------------
# 4. CLASE CLIENTE
# ---------------------------------------------------------------------------
class Cliente(Entidad):
    """Cliente de Software FJ con datos personales encapsulados y validados."""

    def __init__(self, nombre, correo, telefono):
        super().__init__()                       # Inicializa el id de la entidad
        # Se asignan mediante los setters para que las validaciones se apliquen
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    # --- nombre ---
    @property
    def nombre(self):
        return self.__nombre                     # Atributo privado (name mangling)

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe ser texto de al menos 3 caracteres.")
        if any(c.isdigit() for c in valor):
            raise ClienteInvalidoError("El nombre no puede contener números.")
        self.__nombre = valor.strip().title()    # Normaliza el formato

    # --- correo ---
    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"  # Patrón simple de correo
        if not isinstance(valor, str) or not re.match(patron, valor.strip()):
            raise ClienteInvalidoError(f"Correo inválido: {valor!r}")
        self.__correo = valor.strip().lower()

    # --- teléfono ---
    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not isinstance(valor, str) or not re.match(r"^3\d{9}$", valor.strip()):
            raise ClienteInvalidoError(
                f"Teléfono inválido: {valor!r} (debe tener 10 dígitos y empezar en 3)."
            )
        self.__telefono = valor.strip()

    def describir(self):
        """Descripción del cliente (implementa el método abstracto)."""
        return f"Cliente #{self.id}: {self.nombre} | {self.correo} | {self.telefono}"


# ---------------------------------------------------------------------------
# 5. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS
# ---------------------------------------------------------------------------
class Servicio(Entidad, ABC):
    """Clase abstracta base de todos los servicios que ofrece Software FJ."""

    IVA = 0.19  # Impuesto por defecto (19 %)

    def __init__(self, nombre, tarifa_hora, disponible=True):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El servicio requiere un nombre válido.")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ServicioInvalidoError(f"Tarifa por hora inválida: {tarifa_hora!r}")
        self._nombre = nombre.strip()            # Atributo protegido
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    @abstractmethod
    def validar_parametros(self, horas):
        """Valida los parámetros de uso del servicio (cada subclase define sus reglas)."""

    @abstractmethod
    def calcular_costo_base(self, horas):
        """Calcula el costo antes de impuestos y descuentos (polimórfico)."""

    # --- Sobrecarga simulada: un solo método con parámetros opcionales ---
    def calcular_costo(self, horas, impuesto=None, descuento=0.0):
        """
        Calcula el costo final. Variantes de uso (sobrecarga con parámetros opcionales):
            calcular_costo(2)                         -> costo base con IVA por defecto
            calcular_costo(2, impuesto=0.0)           -> costo sin impuesto
            calcular_costo(2, descuento=0.10)         -> costo con 10 % de descuento
            calcular_costo(2, impuesto=0.05, descuento=0.1)
        """
        self.validar_parametros(horas)
        impuesto = self.IVA if impuesto is None else impuesto
        if not 0 <= impuesto <= 1 or not 0 <= descuento < 1:
            raise CalculoInconsistenteError(
                f"Impuesto ({impuesto}) o descuento ({descuento}) fuera de rango."
            )
        base = self.calcular_costo_base(horas)
        total = base * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError("El costo calculado no es positivo.")
        return round(total, 2)

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio #{self.id}: {self._nombre} | ${self._tarifa_hora:,.0f}/h | {estado}"


class ReservaSala(Servicio):
    """Servicio de reserva de salas (con capacidad máxima de personas)."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")
        self._capacidad = capacidad

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 8:
            raise ServicioInvalidoError("Las salas se reservan entre 1 y 8 horas.")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas          # Tarifa lineal por hora

    def describir(self):
        return super().describir() + f" | Sala para {self._capacidad} personas"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos (con depósito fijo de garantía)."""

    DEPOSITO = 20000  # Depósito fijo por alquiler

    def __init__(self, nombre, tarifa_hora, tipo_equipo, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ServicioInvalidoError("El tipo de equipo es obligatorio.")
        self._tipo_equipo = tipo_equipo.strip()

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 72:
            raise ServicioInvalidoError("Los equipos se alquilan entre 1 y 72 horas.")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas + self.DEPOSITO  # Suma el depósito

    def describir(self):
        return super().describir() + f" | Equipo: {self._tipo_equipo}"


class Asesoria(Servicio):
    """Servicio de asesoría especializada (recargo por nivel de experto)."""

    def __init__(self, nombre, tarifa_hora, especialidad, nivel_experto=False, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("La especialidad es obligatoria.")
        self._especialidad = especialidad.strip()
        self._nivel_experto = bool(nivel_experto)

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 0.5 <= horas <= 6:
            raise ServicioInvalidoError("Las asesorías duran entre 0.5 y 6 horas.")

    def calcular_costo_base(self, horas):
        recargo = 1.30 if self._nivel_experto else 1.0  # 30 % más si es experto
        return self._tarifa_hora * horas * recargo

    def describir(self):
        nivel = "Experto" if self._nivel_experto else "Estándar"
        return super().describir() + f" | Asesoría en {self._especialidad} ({nivel})"


# ---------------------------------------------------------------------------
# 6. CLASE RESERVA
# ---------------------------------------------------------------------------
class Reserva(Entidad):
    """Integra cliente, servicio, duración y estado de una reserva."""

    ESTADOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")

    def __init__(self, cliente, servicio, horas):
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")
        try:
            servicio.validar_parametros(horas)   # Reutiliza la validación polimórfica
        except ServicioInvalidoError as error:
            # Encadenamiento de excepciones: se conserva la causa original con "from"
            raise ReservaInvalidaError(f"Duración inválida para la reserva: {horas!r}") from error
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = "PENDIENTE"
        self._fecha = datetime.now()

    @property
    def estado(self):
        return self._estado

    def confirmar(self):
        """Confirma la reserva si el servicio está disponible y el estado lo permite."""
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self._estado}."
            )
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"'{self._servicio.nombre}' no está disponible.")
        self._estado = "CONFIRMADA"
        logger.info("Reserva #%s confirmada.", self.id)

    def cancelar(self):
        """Cancela la reserva si no estaba ya cancelada."""
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada.")
        self._estado = "CANCELADA"
        logger.info("Reserva #%s cancelada.", self.id)

    def procesar(self, descuento=0.0):
        """
        Procesa la reserva: confirma y calcula el costo.
        Usa try/except/else/finally para demostrar el manejo completo de excepciones.
        """
        try:
            self.confirmar()                                         # Puede fallar
            costo = self._servicio.calcular_costo(self._horas, descuento=descuento)
        except SoftwareFJError as error:
            logger.error("Fallo al procesar reserva #%s: %s", self.id, error)
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}") from error
        else:
            # Solo se ejecuta si NO hubo excepción
            logger.info("Reserva #%s procesada. Costo: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            # Siempre se ejecuta, haya o no error
            logger.info("Fin del procesamiento de la reserva #%s (estado: %s).", self.id, self._estado)

    def describir(self):
        return (f"Reserva #{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} "
                f"| {self._horas} h | {self._estado}")


# ---------------------------------------------------------------------------
# 7. GESTOR DEL SISTEMA (listas internas, sin base de datos)
# ---------------------------------------------------------------------------
class GestorFJ:
    """Administra las listas de clientes, servicios y reservas."""

    def __init__(self):
        self.clientes = []    # Lista interna de clientes
        self.servicios = []   # Lista interna de servicios
        self.reservas = []    # Lista interna de reservas

    def registrar_cliente(self, nombre, correo, telefono):
        try:
            cliente = Cliente(nombre, correo, telefono)
        except ClienteInvalidoError as error:
            logger.error("Registro de cliente fallido: %s", error)
            print(f"   [ERROR] {error}")
            return None
        else:
            self.clientes.append(cliente)
            logger.info("Cliente registrado: %s", cliente)
            print(f"   [OK] {cliente}")
            return cliente

    def registrar_servicio(self, clase, *args, **kwargs):
        try:
            servicio = clase(*args, **kwargs)
        except (ServicioInvalidoError, TypeError) as error:
            # TypeError cubre parámetros faltantes al construir el servicio
            logger.error("Creación de servicio fallida (%s): %s", clase.__name__, error)
            print(f"   [ERROR] {error}")
            return None
        else:
            self.servicios.append(servicio)
            logger.info("Servicio creado: %s", servicio)
            print(f"   [OK] {servicio}")
            return servicio

    def crear_reserva(self, cliente, servicio, horas):
        try:
            reserva = Reserva(cliente, servicio, horas)
        except ReservaInvalidaError as error:
            causa = f" (causa: {error.__cause__})" if error.__cause__ else ""
            logger.error("Creación de reserva fallida: %s%s", error, causa)
            print(f"   [ERROR] {error}{causa}")
            return None
        else:
            self.reservas.append(reserva)
            logger.info("Reserva creada: %s", reserva)
            print(f"   [OK] {reserva}")
            return reserva

    def procesar_reserva(self, reserva, descuento=0.0):
        try:
            costo = reserva.procesar(descuento)
        except ReservaInvalidaError as error:
            print(f"   [ERROR] {error} (causa: {error.__cause__})")
            return None
        else:
            print(f"   [OK] Reserva #{reserva.id} confirmada. Total a pagar: ${costo:,.2f}")
            return costo


# ---------------------------------------------------------------------------
# 8. SIMULACIÓN DE 12 OPERACIONES
# ---------------------------------------------------------------------------
def simular():
    """Ejecuta 12 operaciones (válidas e inválidas); el programa nunca se detiene."""
    logger.info("===== INICIO DE LA SIMULACIÓN =====")
    g = GestorFJ()

    print("\n1) Registro válido de cliente")
    ana = g.registrar_cliente("Ana María Pérez", "ana.perez@correo.com", "3101234567")

    print("\n2) Registro inválido: correo mal formado")
    g.registrar_cliente("Luis Gómez", "luis-correo.com", "3109876543")

    print("\n3) Registro inválido: teléfono incorrecto")
    g.registrar_cliente("Carlos Ruiz", "carlos@correo.com", "12345")

    print("\n4) Registro válido de segundo cliente")
    carlos = g.registrar_cliente("Carlos Ruiz", "carlos@correo.com", "3157654321")

    print("\n5) Creación válida de servicio: sala")
    sala = g.registrar_servicio(ReservaSala, "Sala Ejecutiva", 50000, 10)

    print("\n6) Creación válida de servicios: equipo y asesoría")
    equipo = g.registrar_servicio(AlquilerEquipo, "Portátil Pro", 8000, "Computador")
    asesoria = g.registrar_servicio(Asesoria, "Asesoría en Redes", 90000, "Redes", True)

    print("\n7) Creación inválida: tarifa negativa")
    g.registrar_servicio(ReservaSala, "Sala Fantasma", -100, 5)

    print("\n8) Creación inválida: parámetro faltante")
    g.registrar_servicio(AlquilerEquipo, "Proyector", 12000)

    print("\n9) Reserva exitosa (sala, 3 horas) con 10% de descuento")
    r1 = g.crear_reserva(ana, sala, 3)
    g.procesar_reserva(r1, descuento=0.10)

    print("\n10) Reserva fallida: duración fuera de rango (20 h en una sala)")
    g.crear_reserva(carlos, sala, 20)

    print("\n11) Reserva fallida: servicio no disponible")
    asesoria.disponible = False
    r2 = g.crear_reserva(carlos, asesoria, 2)
    g.procesar_reserva(r2)

    print("\n12) Operación no permitida: confirmar una reserva ya cancelada")
    asesoria.disponible = True
    r3 = g.crear_reserva(carlos, equipo, 5)
    r3.cancelar()
    g.procesar_reserva(r3)

    print("\n--- Demostración de polimorfismo y sobrecarga de costos ---")
    for s in g.servicios:
        horas = 2
        print(f"{s.nombre}: base+IVA=${s.calcular_costo(horas):,.2f} | "
              f"sin IVA=${s.calcular_costo(horas, impuesto=0):,.2f} | "
              f"con 15% desc.=${s.calcular_costo(horas, descuento=0.15):,.2f}")

    logger.info("===== FIN DE LA SIMULACIÓN =====")
    print("\nSimulación terminada. Revise el archivo 'software_fj.log'.")


if __name__ == "__main__":
    simular()
