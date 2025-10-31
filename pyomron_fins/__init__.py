#!/usr/bin/env python3
"""
PyOmron FINS - Librería Python para Comunicación con PLC OMRON

Esta librería implementa el protocolo FINS Ethernet para comunicación
con PLCs OMRON de la serie CJ1H, incluyendo soporte completo para:

- Lectura y escritura de valores enteros (INT)
- Lectura y escritura de valores reales (REAL/float)
- Comunicación UDP/TCP sobre puerto 9600
- Manejo automático de conexiones y errores
- Soporte para múltiples áreas de memoria (DM, CIO, WR, HR)

Versión: 1.0.0
Autor: Desarrollado para aplicaciones industriales
"""

from .fins_client import FinsClient, FinsNode, FinsAddress
from .exceptions import FinsError, ReadError, WriteError, ConnectionError

__version__ = "1.0.0"
__author__ = "PyOmron FINS Team"
__description__ = "Librería Python para comunicación FINS con PLC OMRON"

__all__ = [
    'FinsClient',
    'FinsNode',
    'FinsAddress',
    'FinsError',
    'ReadError',
    'WriteError',
    'ConnectionError',
    '__version__',
    '__author__',
    '__description__'
]