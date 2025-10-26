"""
Custom exceptions for PyOmron FINS library

This module defines all custom exceptions used throughout the FINS client library.
"""


class FinsError(Exception):
    """Base exception for all FINS-related errors"""
    pass


class ConnectionError(FinsError):
    """Raised when connection to PLC fails or is lost"""
    pass


class TimeoutError(FinsError):
    """Raised when operation times out"""
    pass


class ReadError(FinsError):
    """Raised when read operation fails"""
    pass


class WriteError(FinsError):
    """Raised when write operation fails"""
    pass


class InvalidAddressError(FinsError):
    """Raised when an invalid memory address is specified"""
    pass


class ProtocolError(FinsError):
    """Raised when FINS protocol error occurs"""
    pass


class AuthenticationError(FinsError):
    """Raised when authentication with PLC fails"""
    pass
