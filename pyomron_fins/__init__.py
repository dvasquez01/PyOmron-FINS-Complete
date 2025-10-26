"""
PyOmron FINS - Python library for OMRON PLC communication using FINS protocol

This library provides a simple and efficient way to communicate with OMRON PLCs
using the FINS Ethernet protocol over UDP or TCP.

Example:
    from pyomron_fins import FinsClient
    
    config = {
        'host': '192.168.1.100',
        'port': 9600,
        'protocol': 'udp'
    }
    
    with FinsClient(**config) as client:
        value = client.read('D100')[0]
        print(f"D100: {value}")
"""

from .fins_client import FinsClient, FinsAddress
from .exceptions import (
    FinsError,
    ConnectionError,
    TimeoutError,
    ReadError,
    WriteError,
    InvalidAddressError
)

__version__ = '1.0.0'
__author__ = 'Development Team'
__email__ = 'dev@pyomron.com'
__description__ = 'Python library for OMRON PLC communication using FINS protocol'

__all__ = [
    'FinsClient',
    'FinsAddress',
    'FinsError',
    'ConnectionError',
    'TimeoutError',
    'ReadError',
    'WriteError',
    'InvalidAddressError'
]
