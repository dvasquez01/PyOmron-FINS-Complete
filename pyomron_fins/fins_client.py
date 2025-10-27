"""
FINS Client for OMRON PLCs

This module provides a Python interface to communicate with OMRON PLCs
using the FINS Ethernet protocol over UDP/TCP.
"""

import socket
import struct
import time
import threading
from typing import Union, List, Dict, Any, Optional, Tuple
from .exceptions import FinsError, ConnectionError, TimeoutError, ReadError, WriteError, InvalidAddressError


class FinsNode:
    """
    Representa un nodo FINS en la red (PLC o dispositivo)
    
    Simplifica la configuración de direcciones FINS abstrayendo los valores hexadecimales.
    """
    
    def __init__(self, network: int = 0, node: int = 0, unit: int = 0):
        """
        Inicializar un nodo FINS
        
        Args:
            network: Número de red (0-127, normalmente 0 para red local)
            node: Número de nodo (0-254, 0 para PLC, 1+ para otros dispositivos)
            unit: Número de unidad (0-15, normalmente 0 para CPU principal)
        """
        if not (0 <= network <= 127):
            raise ValueError("Network debe estar entre 0-127")
        if not (0 <= node <= 254):
            raise ValueError("Node debe estar entre 0-254")
        if not (0 <= unit <= 15):
            raise ValueError("Unit debe estar entre 0-15")
            
        self.network = network
        self.node = node
        self.unit = unit
    
    def to_fins_params(self) -> Dict[str, int]:
        """
        Convertir a parámetros FINS tradicionales
        
        Returns:
            Diccionario con parámetros SNA/SA1/SA2 o DNA/DA1/DA2 según el contexto
        """
        return {
            'network': self.network,
            'node': self.node,
            'unit': self.unit
        }
    
    @classmethod
    def plc_node(cls, node: int = 0, network: int = 0) -> 'FinsNode':
        """Crear un nodo para PLC (unidad 0)"""
        return cls(network=network, node=node, unit=0)
    
    @classmethod
    def pc_node(cls, node: int = 1, network: int = 0) -> 'FinsNode':
        """Crear un nodo para PC/computadora (unidad 0)"""
        return cls(network=network, node=node, unit=0)
    
    def __str__(self):
        return f"Red{self.network}.Nodo{self.node}.Unidad{self.unit}"


class FinsAddress:
    """Represents a FINS memory address"""
    
    # Memory area codes for FINS protocol
    MEMORY_AREAS = {
        'CIO': 0x30,  # CIO Area
        'WR': 0x31,   # Work Area  
        'HR': 0x32,   # Holding Area
        'AR': 0x33,   # Auxiliary Area
        'DM': 0x82,   # Data Memory Area (0x82 for words, 0x02 for bits)
        'D': 0x82,    # Data Memory Area (alias for DM)
        'EM': 0x20,   # Extended Memory Area
        'TIM': 0x09,  # Timer Area
        'CNT': 0x09,  # Counter Area
        'DR': 0x2C,   # Data Register Area
        'IR': 0x2D,   # Index Register Area
    }
    
    def __init__(self, area: str, address: int, bit: Optional[int] = None):
        """
        Initialize a FINS address
        
        Args:
            area: Memory area name (e.g., 'DM', 'CIO', 'WR')
            address: Word address
            bit: Bit number (0-15) for bit access, None for word access
        """
        if area not in self.MEMORY_AREAS:
            raise InvalidAddressError(f"Invalid memory area: {area}")
        
        self.area = area
        self.address = address
        self.bit = bit
        self.area_code = self.MEMORY_AREAS[area]
    
    @classmethod
    def from_string(cls, address_str: str) -> 'FinsAddress':
        """
        Parse address string into FinsAddress object
        
        Examples:
            DM1000 -> DM area, address 1000
            CIO100.05 -> CIO area, address 100, bit 5
            WR200 -> WR area, address 200
        """
        address_str = address_str.upper().strip()
        
        # Check for bit access (contains '.')
        if '.' in address_str:
            area_addr, bit_str = address_str.split('.')
            bit = int(bit_str)
            if bit < 0 or bit > 15:
                raise InvalidAddressError(f"Bit number must be 0-15, got {bit}")
        else:
            area_addr = address_str
            bit = None
        
        # Extract area and address
        area = ""
        addr_str = ""
        
        for i, char in enumerate(area_addr):
            if char.isdigit():
                area = area_addr[:i]
                addr_str = area_addr[i:]
                break
        
        if not area or not addr_str:
            raise InvalidAddressError(f"Invalid address format: {address_str}")
        
        address = int(addr_str)
        
        return cls(area, address, bit)
    
    def to_bytes(self) -> bytes:
        """Convert address to FINS protocol bytes"""
        # FINS address format: [area_code, address_high, address_low, bit]
        addr_high = (self.address >> 8) & 0xFF
        addr_low = self.address & 0xFF
        bit_byte = self.bit if self.bit is not None else 0x00
        
        return bytes([self.area_code, addr_high, addr_low, bit_byte])
    
    def __str__(self):
        if self.bit is not None:
            return f"{self.area}{self.address:04d}.{self.bit:02d}"
        else:
            return f"{self.area}{self.address:04d}"


class FinsClient:
    """
    FINS Protocol Client for OMRON PLCs
    
    Supports both UDP and TCP connections with automatic connection management,
    read/write operations, and PLC control functions.
    """
    
    # FINS Command codes
    FINS_COMMANDS = {
        'MEMORY_AREA_READ': 0x0101,
        'MEMORY_AREA_WRITE': 0x0102,
        'MEMORY_AREA_FILL': 0x0103,
        'MULTIPLE_MEMORY_AREA_READ': 0x0104,
        'MEMORY_AREA_TRANSFER': 0x0105,
        'CONTROLLER_DATA_READ': 0x0501,
        'CONTROLLER_STATUS_READ': 0x0601,
        'RUN': 0x0401,
        'STOP': 0x0402,
        'CLOCK_READ': 0x0720,
        'CLOCK_WRITE': 0x0721,
    }
    
    def __init__(self, 
                 host: str,
                 port: int = 9600,
                 protocol: str = 'udp',
                 timeout: float = 5.0,
                 auto_connect: bool = True,
                 **options):
        """
        Initialize FINS client
        
        Args:
            host: PLC IP address
            port: FINS port (default 9600)
            protocol: 'udp' or 'tcp'
            timeout: Socket timeout in seconds
            auto_connect: Automatically connect on first operation
            **options: Additional FINS options (ICF, DNA, DA1, DA2, SNA, SA1, SA2)
        """
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.timeout = timeout
        self.auto_connect = auto_connect
        
        # FINS header options
        self.icf = options.get('ICF', 0x80)
        self.dna = options.get('DNA', 0x00)
        self.da1 = options.get('DA1', 0x00)  # Destination node
        self.da2 = options.get('DA2', 0x00)
        self.sna = options.get('SNA', 0x00)
        self.sa1 = options.get('SA1', 0x00)  # Source node
        self.sa2 = options.get('SA2', 0x00)
        
        self._socket = None
        self._connected = False
        self._sid = 0x00  # Service ID counter
        self._lock = threading.Lock()
    
    @property
    def connected(self) -> bool:
        """Check if connected to PLC"""
        return self._connected and self._socket is not None
    
    def connect(self) -> None:
        """Establish connection to PLC"""
        try:
            if self.protocol == 'udp':
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._socket.settimeout(self.timeout)
                # UDP doesn't require explicit connection, just store endpoint
                self._connected = True
            elif self.protocol == 'tcp':
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(self.timeout)
                self._socket.connect((self.host, self.port))
                self._connected = True
            else:
                raise ConnectionError(f"Unsupported protocol: {self.protocol}")
                
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}: {e}")
    
    def disconnect(self) -> None:
        """Close connection to PLC"""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            finally:
                self._socket = None
                self._connected = False
    
    def _ensure_connected(self):
        """Ensure connection is established"""
        if not self.connected and self.auto_connect:
            self.connect()
        elif not self.connected:
            raise ConnectionError("Not connected to PLC")
    
    def _build_fins_header(self, command: int, data_length: int) -> bytes:
        """Build FINS protocol header"""
        self._sid = (self._sid + 1) % 256  # Increment service ID
        
        header = struct.pack('>BBBBBBBBBB',
            self.icf,           # Information Control Field
            0x00,               # Reserved
            0x02,               # Gateway Count
            self.dna,           # Destination Network Address
            self.da1,           # Destination Node Address
            self.da2,           # Destination Unit Address  
            self.sna,           # Source Network Address
            self.sa1,           # Source Node Address
            self.sa2,           # Source Unit Address
            self._sid           # Service ID
        )
        
        # Add command code separately as 2 bytes
        header += struct.pack('>H', command)
        
        return header
    
    def _send_command(self, command: int, data: bytes = b'') -> bytes:
        """Send FINS command and receive response"""
        with self._lock:
            self._ensure_connected()
            
            # Build complete message
            header = self._build_fins_header(command, len(data))
            message = header + data
            
            try:
                if self.protocol == 'udp':
                    self._socket.sendto(message, (self.host, self.port))
                    response, _ = self._socket.recvfrom(1024)
                else:  # TCP
                    self._socket.send(message)
                    response = self._socket.recv(1024)
                
                # Check response header
                if len(response) < 12:
                    raise FinsError("Invalid response length")
                
                # Extract command code and error code from response
                response_cmd = struct.unpack('>H', response[10:12])[0]
                if len(response) >= 14:
                    mres = response[12]  # Main Response Code
                    sres = response[13]  # Sub Response Code
                    
                    if mres != 0x00 or sres != 0x00:
                        raise FinsError(f"FINS error: MRES={mres:02X}, SRES={sres:02X}")
                
                return response[14:]  # Return data portion
                
            except socket.timeout:
                raise TimeoutError("Operation timed out")
            except socket.error as e:
                raise FinsError(f"Communication error: {e}")
    
    def read(self, address: Union[str, FinsAddress], count: int = 1) -> List[int]:
        """
        Read data from PLC memory
        
        Args:
            address: Memory address (string or FinsAddress object)
            count: Number of words to read
            
        Returns:
            List of word values
        """
        if isinstance(address, str):
            fins_addr = FinsAddress.from_string(address)
        else:
            fins_addr = address
        
        # Build read command data
        addr_bytes = fins_addr.to_bytes()
        count_bytes = struct.pack('>H', count)
        data = addr_bytes + count_bytes
        
        try:
            response = self._send_command(self.FINS_COMMANDS['MEMORY_AREA_READ'], data)
            
            # Parse response data
            values = []
            for i in range(0, len(response), 2):
                if i + 1 < len(response):
                    value = struct.unpack('>H', response[i:i+2])[0]
                    values.append(value)
            
            return values
            
        except Exception as e:
            raise ReadError(f"Failed to read from {fins_addr}: {e}")
    
    def write(self, address: Union[str, FinsAddress], values: Union[int, List[int]]) -> None:
        """
        Write data to PLC memory
        
        Args:
            address: Memory address (string or FinsAddress object)  
            values: Single value or list of values to write
        """
        if isinstance(address, str):
            fins_addr = FinsAddress.from_string(address)
        else:
            fins_addr = address
        
        if isinstance(values, int):
            values = [values]
        
        # Build write command data
        addr_bytes = fins_addr.to_bytes()
        count_bytes = struct.pack('>H', len(values))
        
        # Pack values as 16-bit words
        data_bytes = b''
        for value in values:
            data_bytes += struct.pack('>H', value & 0xFFFF)
        
        data = addr_bytes + count_bytes + data_bytes
        
        try:
            self._send_command(self.FINS_COMMANDS['MEMORY_AREA_WRITE'], data)
        except Exception as e:
            raise WriteError(f"Failed to write to {fins_addr}: {e}")
    
    def read_multiple(self, addresses: List[Union[str, FinsAddress]]) -> Dict[str, int]:
        """
        Read multiple disparate addresses in one command
        
        Args:
            addresses: List of addresses to read
            
        Returns:
            Dictionary mapping address strings to values
        """
        if len(addresses) > 32:  # FINS limitation
            raise FinsError("Maximum 32 addresses per read_multiple operation")
        
        # Build multiple read command data
        data = struct.pack('B', len(addresses))  # Number of addresses
        
        fins_addresses = []
        for addr in addresses:
            if isinstance(addr, str):
                fins_addr = FinsAddress.from_string(addr)
            else:
                fins_addr = addr
            
            fins_addresses.append(fins_addr)
            data += fins_addr.to_bytes()
        
        try:
            response = self._send_command(self.FINS_COMMANDS['MULTIPLE_MEMORY_AREA_READ'], data)
            
            # Parse response
            result = {}
            offset = 0
            
            for i, fins_addr in enumerate(fins_addresses):
                if offset + 1 < len(response):
                    value = struct.unpack('>H', response[offset:offset+2])[0]
                    result[str(fins_addr)] = value
                    offset += 2
            
            return result
            
        except Exception as e:
            raise ReadError(f"Failed to read multiple addresses: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get controller status"""
        try:
            response = self._send_command(self.FINS_COMMANDS['CONTROLLER_STATUS_READ'])
            
            if len(response) >= 1:
                status_byte = response[0]
                return {
                    'run_mode': (status_byte & 0x01) == 0x01,
                    'program_mode': (status_byte & 0x02) == 0x02,
                    'fatal_error': (status_byte & 0x40) == 0x40,
                    'non_fatal_error': (status_byte & 0x80) == 0x80,
                }
            else:
                return {}
                
        except Exception as e:
            raise FinsError(f"Failed to get controller status: {e}")
    
    def get_cpu_unit_data(self) -> Dict[str, Any]:
        """Get CPU unit information"""
        try:
            response = self._send_command(self.FINS_COMMANDS['CONTROLLER_DATA_READ'])
            
            if len(response) >= 40:
                # Parse CPU unit data (simplified)
                result = {
                    'controller_model': response[0:20].decode('ascii', errors='ignore').strip(),
                    'controller_version': response[20:40].decode('ascii', errors='ignore').strip(),
                }
                return result
            else:
                return {}
                
        except Exception as e:
            raise FinsError(f"Failed to get CPU unit data: {e}")
    
    def read_real(self, address: Union[str, FinsAddress]) -> float:
        """
        Read REAL (float) value from PLC memory
        
        Args:
            address: Memory address (string or FinsAddress object)
            
        Returns:
            Float value (32-bit IEEE 754 in OMRON Word Swapped Big Endian format)
        """
        if isinstance(address, str):
            fins_addr = FinsAddress.from_string(address)
        else:
            fins_addr = address
        
        # Read 2 consecutive words for the float (32 bits)
        addr_bytes = fins_addr.to_bytes()
        count_bytes = struct.pack('>H', 2)  # 2 words
        data = addr_bytes + count_bytes
        
        try:
            response = self._send_command(self.FINS_COMMANDS['MEMORY_AREA_READ'], data)
            
            if len(response) >= 4:
                # OMRON format: Word Swapped Big Endian
                float_bytes = response[:4]
                swapped_bytes = float_bytes[2:4] + float_bytes[0:2]
                float_value = struct.unpack('>f', swapped_bytes)[0]
                return float_value
            else:
                raise ReadError(f"Insufficient data for REAL value from {fins_addr}")
                
        except Exception as e:
            raise ReadError(f"Failed to read REAL from {fins_addr}: {e}")
    
    def write_real(self, address: Union[str, FinsAddress], value: float) -> None:
        """
        Write REAL (float) value to PLC memory
        
        Args:
            address: Memory address (string or FinsAddress object)
            value: Float value to write
        """
        if isinstance(address, str):
            fins_addr = FinsAddress.from_string(address)
        else:
            fins_addr = address
        
        # Convert float to OMRON Word Swapped Big Endian format
        float_bytes = struct.pack('>f', value)
        swapped_bytes = float_bytes[2:4] + float_bytes[0:2]
        
        # Build write command data
        addr_bytes = fins_addr.to_bytes()
        count_bytes = struct.pack('>H', 2)  # 2 words
        data = addr_bytes + count_bytes + swapped_bytes
        
        try:
            self._send_command(self.FINS_COMMANDS['MEMORY_AREA_WRITE'], data)
        except Exception as e:
            raise WriteError(f"Failed to write REAL to {fins_addr}: {e}")
    
    def read_clock(self) -> Dict[str, int]:
        """Read PLC clock"""
        try:
            response = self._send_command(self.FINS_COMMANDS['CLOCK_READ'])
            
            if len(response) >= 7:
                year = response[0] + 2000 if response[0] < 50 else response[0] + 1900
                month = response[1]
                day = response[2]
                hour = response[3]
                minute = response[4]
                second = response[5]
                day_of_week = response[6]
                
                return {
                    'year': year,
                    'month': month,
                    'day': day,
                    'hour': hour,
                    'minute': minute,
                    'second': second,
                    'day_of_week': day_of_week
                }
            else:
                return {}
                
        except Exception as e:
            raise FinsError(f"Failed to read clock: {e}")
    
    @classmethod
    def create_config(cls,
                     host: str,
                     port: int = 9600,
                     protocol: str = 'udp',
                     timeout: float = 5.0,
                     plc_node: Union[FinsNode, int] = None,
                     pc_node: Union[FinsNode, int] = None,
                     icf: int = 0x80) -> Dict[str, Any]:
        """
        Crear configuración FINS de manera intuitiva
        
        Args:
            host: Dirección IP del PLC
            port: Puerto FINS (default 9600)
            protocol: Protocolo ('udp' o 'tcp')
            timeout: Timeout en segundos
            plc_node: Nodo del PLC (FinsNode o int para nodo simple)
            pc_node: Nodo de la PC (FinsNode o int para nodo simple)
            icf: Information Control Field (default 0x80)
            
        Returns:
            Diccionario de configuración listo para FinsClient
            
        Examples:
            # Configuración simple
            config = FinsClient.create_config(
                host='192.168.1.100',
                plc_node=0,  # PLC en nodo 0
                pc_node=1    # PC en nodo 1
            )
            
            # Configuración avanzada con FinsNode
            plc = FinsNode.plc_node(node=5, network=1)
            pc = FinsNode.pc_node(node=10, network=1)
            config = FinsClient.create_config(
                host='192.168.1.100',
                plc_node=plc,
                pc_node=pc
            )
        """
        # Procesar nodos
        if plc_node is None:
            plc_node = FinsNode.plc_node(0)  # PLC por defecto en nodo 0
        elif isinstance(plc_node, int):
            plc_node = FinsNode.plc_node(plc_node)
            
        if pc_node is None:
            pc_node = FinsNode.pc_node(1)  # PC por defecto en nodo 1
        elif isinstance(pc_node, int):
            pc_node = FinsNode.pc_node(pc_node)
        
        # Validar que estén en la misma red
        if plc_node.network != pc_node.network:
            print(f"Advertencia: PLC y PC están en redes diferentes ({plc_node.network} vs {pc_node.network})")
        
        config = {
            'host': host,
            'port': port,
            'protocol': protocol,
            'timeout': timeout,
            'ICF': icf,
            # PLC como destino
            'DNA': plc_node.network,  # Destination Network Address
            'DA1': plc_node.node,    # Destination Node Address
            'DA2': plc_node.unit,    # Destination Unit Address
            # PC como origen
            'SNA': pc_node.network,  # Source Network Address
            'SA1': pc_node.node,    # Source Node Address
            'SA2': pc_node.unit,    # Source Unit Address
        }
        
        return config
    
    @classmethod
    def simple_config(cls,
                     host: str,
                     plc_node: int = 0,
                     pc_node: int = 1,
                     protocol: str = 'udp',
                     port: int = 9600) -> Dict[str, Any]:
        """
        Configuración FINS ultra-simple para casos comunes
        
        Args:
            host: IP del PLC
            plc_node: Número de nodo del PLC (default 0)
            pc_node: Número de nodo de la PC (default 1)
            protocol: Protocolo ('udp' o 'tcp', default 'udp')
            port: Puerto (default 9600)
            
        Returns:
            Configuración lista para usar
            
        Example:
            config = FinsClient.simple_config('192.168.1.100')
            with FinsClient(**config) as client:
                data = client.read('DM100')
        """
        return cls.create_config(
            host=host,
            port=port,
            protocol=protocol,
            plc_node=plc_node,
            pc_node=pc_node
        )
    
    @classmethod
    def quick_connect(cls,
                     host: str,
                     plc_node: int = 0,
                     pc_node: int = 1,
                     protocol: str = 'udp') -> 'FinsClient':
        """
        Conexión rápida con configuración automática
        
        Args:
            host: IP del PLC
            plc_node: Nodo del PLC (default 0)
            pc_node: Nodo de la PC (default 1)
            protocol: Protocolo ('udp' o 'tcp')
            
        Returns:
            Instancia de FinsClient conectada
            
        Example:
            client = FinsClient.quick_connect('192.168.1.100')
            data = client.read('DM100')
            client.disconnect()
        """
        config = cls.simple_config(host, plc_node, pc_node, protocol)
        client = cls(**config)
        client.connect()
        return client
    
    def __enter__(self):
        """Context manager entry"""
        if not self.connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def __del__(self):
        """Destructor"""
        self.disconnect()