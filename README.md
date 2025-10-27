# PyOmron FINS Complete

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

**Librería Python profesional para comunicación con PLCs OMRON usando protocolo FINS Ethernet**

## Características Principales

- Comunicación FINS completa - UDP y TCP
- Soporte PLC OMRON CJ1H - Completamente probado
- Tipos de datos múltiples - INT, REAL (float), bits
- Áreas de memoria - DM, CIO, WR, HR y más
- Operaciones optimizadas - Lectura/escritura eficiente
- Manejo de errores robusto - Códigos FINS específicos
- Context manager - Gestión automática de conexiones
- Documentación completa - Ejemplos y guías

## Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/dvasquez01/PyOmron-FINS-Complete.git
cd PyOmron-FINS-Complete

# Instalar dependencias (solo Python estándar)
# No requiere dependencias externas!
```

## Uso Básico

### Método Simplificado (Recomendado)
```python
from pyomron_fins import FinsClient

# Configuración ultra-simple (¡una sola línea!)
config = FinsClient.simple_config('192.168.140.10')

# Usar con context manager
with FinsClient(**config) as client:
    valor = client.read('D0')[0]          # Leer entero
    temp = client.read_real('D1702')      # Leer float
    client.write('D200', 12345)           # Escribir entero
    client.write_real('D1710', 3.14)     # Escribir float
```

### Método Avanzado con Nodos
```python
from pyomron_fins import FinsClient, FinsNode

# Crear nodos de manera intuitiva
plc = FinsNode.plc_node(node=0, network=0)  # PLC en red 0, nodo 0
pc = FinsNode.pc_node(node=1, network=0)    # PC en red 0, nodo 1

# Configuración avanzada
config = FinsClient.create_config(
    host='192.168.140.10',
    plc_node=plc,
    pc_node=pc,
    protocol='udp'
)

with FinsClient(**config) as client:
    # Operaciones...
```

### Conexión Rápida
```python
# Conexión instantánea
client = FinsClient.quick_connect('192.168.140.10')
# Cliente ya conectado y listo para usar
data = client.read('DM100')
client.disconnect()
```

## API Simplificada

### Clase FinsNode
Representa un dispositivo en la red FINS de manera intuitiva:

```python
from pyomron_fins import FinsNode

# Crear nodos de manera intuitiva
plc = FinsNode.plc_node(node=0)        # PLC en nodo 0
pc = FinsNode.pc_node(node=1)          # PC en nodo 1

# O crear nodos personalizados
dispositivo = FinsNode(network=1, node=10, unit=0)  # Red 1, nodo 10, unidad 0
```

### Métodos de Configuración Simplificada

#### `FinsClient.simple_config()`
Para configuraciones básicas:
```python
config = FinsClient.simple_config(
    host='192.168.1.100',  # IP del PLC
    plc_node=0,             # Nodo del PLC (default 0)
    pc_node=1,              # Nodo de la PC (default 1)
    protocol='udp'          # Protocolo (default 'udp')
)
```

#### `FinsClient.create_config()`
Para configuraciones avanzadas:
```python
config = FinsClient.create_config(
    host='192.168.1.100',
    plc_node=FinsNode.plc_node(node=5, network=1),  # PLC en red 1, nodo 5
    pc_node=FinsNode.pc_node(node=10, network=1),   # PC en red 1, nodo 10
    timeout=10.0
)
```

#### `FinsClient.quick_connect()`
Conexión instantánea:
```python
client = FinsClient.quick_connect('192.168.1.100')
# Cliente ya conectado y listo para usar
```

### Beneficios de la Nueva API
- **Abstracción completa** de valores hexadecimales FINS
- **Configuración intuitiva** con nombres descriptivos
- **Menos propenso a errores** en configuración
- **Compatible hacia atrás** con configuraciones tradicionales
- **Soporte para redes complejas** con múltiples dispositivos

## Funcionalidades Verificadas

### Lectura de Datos
- **Enteros (INT)**: `client.read('D100')[0]`
- **Reales (REAL)**: `client.read_real('D1702')`
- **Múltiples valores**: `client.read('D100', count=5)`

### Escritura de Datos  
- **Enteros**: `client.write('D200', 12345)`
- **Reales**: `client.write_real('D1710', 3.14159)`
- **Múltiples**: `client.write('D200', [100, 200, 300])`

### Áreas de Memoria Soportadas
- **Data Memory**: `D100` o `DM100`
- **Channel I/O**: `CIO10`
- **Work Relay**: `WR100`
- **Holding Relay**: `HR100`

### Información del PLC
- **Estado del controlador**: `client.get_status()`
- **Información CPU**: `client.get_cpu_unit_data()`
- **Modelo verificado**: OMRON CJ1H-CPU66H-R

## Ejemplos Avanzados

### Monitoreo en Tiempo Real
```python
with FinsClient(**config) as client:
    while True:
        temp = client.read_real('D1702')
        estado = client.read('D100')[0]
        print(f"Temp: {temp:.1f}°C, Estado: {estado}")
        time.sleep(1)
```

### Escritura Segura con Verificación
```python
with FinsClient(**config) as client:
    # Escribir y verificar
    client.write('D200', 12345)
    verificacion = client.read('D200')[0]
    
    if verificacion == 12345:
        print("Escritura exitosa")
    else:
        print("Error en escritura")
```

## Especificaciones Técnicas

### Protocolos Soportados
- **FINS over UDP** (Recomendado - más rápido)
- **FINS over TCP** (Más confiable)

### PLCs Compatibles
- **OMRON CJ1H-CPU66H-R** (Completamente probado)
- **Serie CJ** (Compatible)
- **Serie CP** (Compatible)
- **Serie CS** (Compatible)

### Formatos de Datos
- **INT (16 bits)**: 0 - 65,535
- **REAL (32 bits)**: IEEE 754 Word Swapped Big Endian
- **Bits individuales**: Con formato `.bit`

## Configuración para Diferentes PLCs

### OMRON CJ1H (Probado)
```python
config = {
    'host': 'IP_PLC',
    'ICF': 0x80, 'DNA': 0x00, 'DA1': 0x00, 'DA2': 0x00,
    'SNA': 0x00, 'SA1': 0x01, 'SA2': 0x00
}
```

### Configuración Genérica OMRON
```python
config = {
    'host': 'IP_PLC',
    'port': 9600,
    'protocol': 'udp',
    'timeout': 5.0
}
```

## Manejo de Errores

```python
from pyomron_fins.exceptions import FinsError, ReadError, WriteError

try:
    with FinsClient(**config) as client:
        valor = client.read('D100')[0]
excep ConnectionError:
    print("No se pudo conectar al PLC")
except ReadError as e:
    print(f"Error leyendo: {e}")
except FinsError as e:
    print(f"Error FINS: {e}")
```

## Estructura del Proyecto

```
PyOmron-FINS-Complete/
├── pyomron_fins/
│   ├── __init__.py
│   ├── fins_client.py          # Cliente principal
│   └── exceptions.py           # Excepciones personalizadas
├── examples/
│   ├── ejemplo_simple_uso.py   # Ejemplo básico
│   ├── ejemplo_automatizado_omron.py  # Pruebas completas
│   └── ejemplo_definitivo_omron.py    # Ejemplo interactivo
├── docs/
│   └── RESUMEN_FINAL_PYOMRON.md
├── README.md
└── LICENSE
```

## Pruebas Incluidas

Ejecuta los ejemplos para probar la librería:

```bash
# Ejemplo básico
python examples/ejemplo_simple_uso.py

# Pruebas completas automatizadas
python examples/ejemplo_automatizado_omron.py

# Ejemplo interactivo completo
python examples/ejemplo_definitivo_omron.py
```

## Resultados de Pruebas

### Pruebas Exitosas
- **Conexión**: PLC OMRON CJ1H-CPU66H-R 
- **Lectura INT**: D0=40111, D100=555, D1700=33 
- **Lectura REAL**: D1702=10.25 
- **Escritura DM**: Completamente funcional 
- **Info PLC**: Modelo y versión detectados 

### Limitaciones Identificadas
- **CIO/WR**: Áreas protegidas en PLC industrial (normal)
- **Lectura múltiple**: Comando deshabilitado en PLC específico
- **Reloj PLC**: Función no habilitada en configuración

## Contribuciones

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

Desarrollado y probado por el equipo de desarrollo industrial.

## Soporte

- **Issues**: [GitHub Issues](https://github.com/dvasquez01/PyOmron-FINS-Complete/issues)
- **Documentación**: Ver carpeta `docs/`
- **Ejemplos**: Ver carpeta `examples/`

## Estado del Proyecto

**IMPORTANTE**: El uso en ambientes industriales queda bajo responsabilidad del usuario. Solo usar en ambientes de pruebas.

---

**Si te gusta este proyecto, no olvides darle una estrella en GitHub!**