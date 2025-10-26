# PyOmron FINS - Librería Python para Comunicación con PLC OMRON

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dvasquez01/PyOmron-FINS-Complete/graphs/commit-activity)

## 📋 Descripción

**PyOmron FINS** es una librería Python completa y profesional para comunicación con PLCs OMRON mediante el protocolo FINS Ethernet. Implementa soporte completo para lectura y escritura de valores enteros y reales, con manejo automático de conexiones y errores robustos.

### ✨ Características Principales

- 🔌 **Comunicación FINS**: UDP/TCP sobre puerto 9600
- 📊 **Tipos de Datos**: INT (16-bit) y REAL (32-bit IEEE 754)
- 🧠 **Formato OMRON**: Word Swapped Big Endian para valores reales
- 💾 **Áreas de Memoria**: DM, CIO, WR, HR, AR
- 🔄 **Gestión Automática**: Context manager para conexiones
- ⚡ **Optimización**: Lectura múltiple y operaciones eficientes
- 🛡️ **Manejo de Errores**: Sistema robusto de excepciones

## 🚀 Instalación

### Opción 1: Desde GitHub (Recomendado)
```bash
git clone https://github.com/dvasquez01/PyOmron-FINS-Complete.git
cd PyOmron-FINS-Complete
pip install .
```

### Opción 2: Instalación Directa
```bash
pip install git+https://github.com/dvasquez01/PyOmron-FINS-Complete.git
```

### Opción 3: Modo Desarrollo
```bash
git clone https://github.com/dvasquez01/PyOmron-FINS-Complete.git
cd PyOmron-FINS-Complete
pip install -e .
```

## 📖 Uso Rápido

```python
from pyomron_fins import FinsClient

# Configuración del PLC
config = {
    'host': '192.168.140.10',      # IP del PLC
    'port': 9600,                  # Puerto FINS estándar
    'protocol': 'udp',             # UDP es más rápido
    'timeout': 5.0,                # Timeout en segundos
    # Configuración FINS específica para OMRON CJ1H
    'ICF': 0x80, 'DNA': 0x00, 'DA1': 0x00, 'DA2': 0x00,
    'SNA': 0x00, 'SA1': 0x01, 'SA2': 0x00
}

# Uso con context manager (recomendado)
with FinsClient(**config) as client:
    # Leer valor entero
    valor = client.read('D0')[0]
    print(f"D0: {valor}")
    
    # Leer valor real (float)
    temperatura = client.read_real('D1702')
    print(f"Temperatura: {temperatura:.2f}")
    
    # Escribir valor entero
    client.write('D2000', 12345)
    
    # Escribir valor real
    client.write_real('D1710', 3.14159)
    
    # Información del PLC
    status = client.get_status()
    cpu_info = client.get_cpu_unit_data()
```

## 📚 API Completa

### Clase FinsClient

#### Constructor
```python
FinsClient(host, port=9600, protocol='udp', timeout=5.0,
           ICF=0x80, DNA=0x00, DA1=0x00, DA2=0x00,
           SNA=0x00, SA1=0x01, SA2=0x00)
```

#### Métodos de Lectura/Escritura

| Método | Descripción | Ejemplo |
|--------|-------------|---------|
| `read(address, count=1)` | Leer valores enteros | `client.read('D0', 5)` |
| `write(address, value)` | Escribir valor entero | `client.write('D100', 123)` |
| `read_real(address)` | Leer valor real | `client.read_real('D1702')` |
| `write_real(address, value)` | Escribir valor real | `client.write_real('D1710', 3.14)` |
| `read_multiple(addresses)` | Lectura múltiple optimizada | `client.read_multiple(['D0', 'D100'])` |

#### Métodos de Información del PLC

| Método | Descripción |
|--------|-------------|
| `get_status()` | Estado del controlador |
| `get_cpu_unit_data()` | Información de la CPU |
| `read_clock()` | Reloj del PLC |

### Sistema de Direccionamiento

#### Áreas de Memoria Soportadas

| Área | Código | Descripción | Ejemplos |
|------|--------|-------------|----------|
| **DM** | `0x82` | Data Memory | `D0`, `DM100`, `D1700` |
| **CIO** | `0x30` | CIO Area | `CIO100`, `CIO0.00` |
| **WR** | `0x31` | Work Area | `WR100`, `W100` |
| **HR** | `0x32` | Holding Area | `HR100`, `H100` |
| **AR** | `0x33` | Auxiliary Area | `AR100`, `A100` |

#### Formatos de Dirección
- **D/DM**: `D0`, `DM100`, `D1700`
- **CIO**: `CIO100`, `CIO0.00` (bit específico)
- **WR**: `WR100`, `W100`
- **HR**: `HR100`, `H100`
- **AR**: `AR100`, `A100`

## ⚠️ Manejo de Errores

```python
from pyomron_fins import FinsClient
from pyomron_fins.exceptions import FinsError, ReadError, WriteError, ConnectionError

try:
    with FinsClient(**config) as client:
        valor = client.read('D0')[0]
except ConnectionError as e:
    print(f"Error de conexión: {e}")
except ReadError as e:
    print(f"Error de lectura: {e}")
except WriteError as e:
    print(f"Error de escritura: {e}")
except FinsError as e:
    print(f"Error FINS general: {e}")
```

### Tipos de Excepciones

- **`ConnectionError`**: Problemas de conexión con el PLC
- **`ReadError`**: Errores al leer datos
- **`WriteError`**: Errores al escribir datos
- **`FinsError`**: Errores generales del protocolo FINS

## 📋 Ejemplos Incluidos

### 1. Ejemplo Simple (`ejemplo_simple_uso.py`)
Uso básico paso a paso con todas las operaciones fundamentales.

### 2. Ejemplo Automatizado (`ejemplo_automatizado_omron.py`)
Ejecuta todas las pruebas automáticamente sin intervención del usuario.

### 3. Ejemplo Definitivo (`ejemplo_definitivo_omron.py`)
Demostración completa e interactiva de todas las capacidades.

```bash
# Ejecutar ejemplos
python examples/ejemplo_simple_uso.py
python examples/ejemplo_automatizado_omron.py
python examples/ejemplo_definitivo_omron.py
```

## 🔧 Configuración del PLC

### PLC Soportado
- **Modelo**: OMRON CJ1H-CPU66H-R
- **Versión Firmware**: 04.60+
- **Modo**: RUN (operativo)

### Configuración de Red
- **IP PLC**: Configurar según tu red local
- **Puerto**: 9600 (FINS estándar)
- **Protocolo**: UDP (recomendado) o TCP

### Configuración FINS en CX-Programmer
```
Network Settings:
- IP Address: [IP_DE_TU_PLC]
- Subnet Mask: 255.255.255.0
- Default Gateway: [GATEWAY_DE_TU_RED]

FINS Settings:
- FINS Network Address: 0
- FINS Node Address: 0
- FINS Unit Address: 0
```

## 🧪 Valores de Prueba Verificados

### Valores Enteros (INT)
| Dirección | Valor | Descripción |
|-----------|-------|-------------|
| `D0` | 40111 | Contador principal |
| `D100` | 555 | Estado del sistema |
| `D1700` | 33 | Alarma general |

### Valores Reales (REAL)
| Dirección | Valor | Descripción |
|-----------|-------|-------------|
| `D1702` | 10.25 | Temperatura |

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/dvasquez01/PyOmron-FINS-Complete/issues)
- **Documentación**: Ver carpeta `docs/`
- **Ejemplos**: Ver carpeta `examples/`

## 🏆 Estado del Proyecto

**⚠️ IMPORTANTE**: El uso en ambientes industriales queda bajo responsabilidad del usuario. Solo usar en ambientes de pruebas.

---

**⭐ Si te gusta este proyecto, no olvides darle una estrella en GitHub!**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Contacto

- **Autor**: PyOmron FINS Team
- **Proyecto**: [PyOmron FINS](https://github.com/dvasquez01/PyOmron-FINS-Complete)
- **Email**: [Información de contacto próximamente]

---

**PyOmron FINS** - Comunicación industrial simplificada con PLC OMRON ⚡