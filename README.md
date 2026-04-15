# PRODUCIBLE-PFV
Sistema automatizado en Python para el cálculo de energía producible y generación de reportes horarios en parques fotovoltaicos, basado en el estándar IEEE 830-1998

# Producible de Energía - Parque Fotovoltaico

Sistema desarrollado para la materia de **Administración del Proceso de Software I** en la **Universidad Autónoma de Chihuahua**.

## Objetivo del Proyecto
Desarrollar una herramienta funcional que automatice el procesamiento de datos operativos y meteorológicos provenientes de sistemas SCADA, generando reportes energéticos precisos en formato Excel

## Tecnologías Utilizadas
**Lenguaje:** Python 3.x.
**Librerías:** Pandas (Procesamiento de datos) y OpenPyXL (Gestión de Excel).
**Estándar de Documentación:** IEEE 830-1998 para la Especificación de Requisitos de Software (SRS).

## Estructura del Repositorio
* `main.py`: Punto de entrada del sistema.
* `validador.py`: Módulo de limpieza y verificación de integridad de datos.
* `procesador.py`: Lógica de cálculo de energía y agregación horaria.
* `exportador.py`: Generación del archivo Excel con formato profesional.
* `/data`: Carpeta para archivos de entrada (CSV/Excel) y resultados.

## Funcionamiento Técnico
El sistema aplica la siguiente lógica para determinar la energía minuto a minuto:
$$Energía_{min}(kWh) = \left( \frac{Potencia \ Activa \ (MW) \times 1000}{60} \right) \times \left( \frac{Disponibilidad}{100} \right)$$.

## Autor
* **Ricardo Alejandro Deanda Polo** - Matrícula: 382931.
* **Asesor:** Ing. José Antonio Lomelí García.
