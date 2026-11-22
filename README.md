# Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la Fase 4 del curso Programación (213023) de la UNAD.

## Descripción
Sistema orientado a objetos en Python, sin base de datos, que gestiona clientes, servicios y reservas para la empresa Software FJ. Aplica abstracción, herencia, polimorfismo, encapsulación y manejo avanzado de excepciones.

## Contenido
- `software_fj.py`: código completo del sistema, comentado.
- `software_fj.log`: se genera al ejecutar el programa y registra eventos y errores.

## Características
- Clase abstracta `Entidad` y clase `Cliente` con validaciones.
- Clase abstracta `Servicio` con tres servicios especializados: `ReservaSala`, `AlquilerEquipo` y `Asesoria`.
- Clase `Reserva` con confirmación, cancelación y procesamiento.
- Excepciones personalizadas, `try/except/else/finally` y encadenamiento de excepciones.
- Cálculo de costos con impuestos y descuentos opcionales.
- Simulación de 14 operaciones válidas e inválidas.

## Cómo ejecutarlo
```bash
python software_fj.py
```

## Autor
Johan-Estiven-Saavedra-Balanta
