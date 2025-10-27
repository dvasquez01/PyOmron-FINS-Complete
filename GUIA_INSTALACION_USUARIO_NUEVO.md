# 🚀 Guía de Instalación Rápida - PyOmron FINS
## Para Usuarios Nuevos desde GitHub

Esta guía te ayudará a instalar y usar PyOmron FINS desde cero, asumiendo que solo tienes acceso al repositorio de GitHub.

---

## 📋 Requisitos Previos

### Sistema Operativo
- ✅ **Windows** (10/11)
- ✅ **Linux** (Ubuntu, CentOS, etc.)
- ✅ **macOS**

### Software Necesario
- **Python 3.7 o superior** (NO Python 2.x)
- **Git** (para clonar el repositorio)
- **Conexión a internet** (para instalación inicial)

---

## 🛠️ Paso 1: Instalar Python

### Verificar si ya tienes Python instalado:
```bash
python --version
# o
python3 --version
```

### Si NO tienes Python, instálalo:

#### Windows:
1. Ve a https://python.org/downloads/
2. Descarga Python 3.9+ (recomendado)
3. Durante instalación: ✅ **Marcar "Add Python to PATH"**
4. Verifica: `python --version`

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

#### macOS:
```bash
# Usando Homebrew (recomendado)
brew install python3

# O desde python.org
# Descarga e instala Python 3.9+
python3 --version
```

---

## 📥 Paso 2: Clonar el Repositorio

```bash
# Abre una terminal/cmd y ejecuta:
git clone https://github.com/dvasquez01/PyOmron-FINS-Complete.git

# Entra al directorio del proyecto:
cd PyOmron-FINS-Complete
```

---

## ⚙️ Paso 3: Instalar la Librería

### Opción A: Instalación Simple (Recomendado)
```bash
# Instalar en modo desarrollo (permite modificar el código)
pip install -e .
```

### Opción B: Instalación Normal
```bash
# Instalar como paquete normal
pip install .
```

### Verificar instalación:
```python
python -c "from pyomron_fins import FinsClient; print('✅ PyOmron FINS instalado correctamente!')"
```

---

## 🧪 Paso 4: Primer Uso - "Hola Mundo"

Crea un archivo llamado `primer_uso.py`:

```python
#!/usr/bin/env python3
"""
Mi primer programa con PyOmron FINS
"""

from pyomron_fins import FinsClient

# Configuración ultra-simple (¡una sola línea!)
config = FinsClient.simple_config('192.168.1.100')  # ← Cambia por la IP de tu PLC

try:
    with FinsClient(**config) as client:
        print("✅ Conectado al PLC!")
        
        # Leer un valor
        valor = client.read('D0')[0]
        print(f"Valor en D0: {valor}")
        
        # Leer temperatura (si tienes sensor)
        try:
            temp = client.read_real('D1702')
            print(f"Temperatura: {temp:.1f}°C")
        except:
            print("Nota: D1702 no disponible (normal)")

except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Verifica que:")
    print("   - La IP del PLC sea correcta")
    print("   - El PLC esté encendido")
    print("   - No haya firewall bloqueando el puerto 9600")
```

### Ejecutar el programa:
```bash
python primer_uso.py
```

---

## 🔧 Paso 5: Configuración de tu PLC

### Encontrar la IP de tu PLC OMRON:

#### Método 1: Desde el software CX-Programmer:
1. Abre CX-Programmer
2. Conecta al PLC
3. Ve a: `PLC` → `Edit` → `Preferences` → `Built-in Ethernet`
4. Busca la dirección IP

#### Método 2: Desde el panel del PLC:
- Presiona el botón `MODE/SET` en el PLC
- Navega hasta `Built-in Ethernet Settings`
- Anota la IP address

#### Método 3: Desde el software de configuración OMRON:
- Usa `CX-Integrator` o `Network Configurator`

### Configuración típica:
- **IP:** 192.168.250.1 (o similar en tu red)
- **Puerto:** 9600 (default)
- **Protocolo:** UDP (más rápido)

---

## 📚 Paso 6: Ejemplos de Uso

### Ejemplo Básico:
```python
from pyomron_fins import FinsClient

# Configuración simple
config = FinsClient.simple_config('192.168.250.1')  # ← Tu IP del PLC

with FinsClient(**config) as client:
    # Leer datos
    valor = client.read('DM100')[0]        # Leer entero
    temp = client.read_real('DM1702')      # Leer float
    
    # Escribir datos
    client.write('DM200', 12345)           # Escribir entero
    client.write_real('DM1710', 23.5)     # Escribir float
```

### Ejemplo con Nodos Personalizados:
```python
from pyomron_fins import FinsClient, FinsNode

# Si tu PLC no está en nodo 0
plc = FinsNode.plc_node(node=5)  # PLC en nodo 5
pc = FinsNode.pc_node(node=10)   # PC en nodo 10

config = FinsClient.create_config(
    host='192.168.250.1',
    plc_node=plc,
    pc_node=pc
)

with FinsClient(**config) as client:
    data = client.read('DM100')
```

### Conexión Rápida:
```python
# Conexión instantánea
client = FinsClient.quick_connect('192.168.250.1')
data = client.read('DM100')
client.disconnect()
```

---

## 🔍 Paso 7: Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'pyomron_fins'"
```bash
# Reinstala la librería
pip uninstall pyomron_fins
pip install -e .
```

### Error: "ConnectionError: Failed to connect"
- ✅ Verifica que la IP del PLC sea correcta
- ✅ Verifica que el PLC esté encendido
- ✅ Verifica que no haya firewall bloqueando puerto 9600
- ✅ Prueba hacer ping al PLC: `ping 192.168.250.1`

### Error: "TimeoutError"
- ✅ Aumenta el timeout: `config = FinsClient.simple_config('192.168.250.1', timeout=10.0)`
- ✅ Verifica la conexión de red

### Error: "FinsError: MRES=1, SRES=1"
- ✅ Verifica que el PLC esté en modo RUN (no PROGRAM)
- ✅ Verifica que las direcciones de memoria sean correctas
- ✅ Algunos PLC tienen áreas protegidas (CIO/WR requieren permisos especiales)

### Verificar estado del PLC:
```python
with FinsClient(**config) as client:
    status = client.get_status()
    print(f"Modo RUN: {status.get('run_mode', False)}")
    print(f"Modo PROGRAM: {status.get('program_mode', False)}")
```

---

## 📖 Paso 8: Aprender Más

### Documentación completa:
- Lee el `README.md` en el repositorio
- Revisa los ejemplos en la carpeta `examples/`

### Ejemplos incluidos:
```bash
# Ejemplo básico
python examples/ejemplo_simple_uso.py

# Ejemplos avanzados
python examples/ejemplo_configuracion_simplificada.py

# Pruebas automatizadas
python examples/ejemplo_automatizado_omron.py
```

### Áreas de memoria comunes:
- `DM100` - Data Memory (lectura/escritura)
- `CIO10` - Channel I/O (solo lectura en muchos PLC)
- `WR100` - Work Relay (solo lectura en muchos PLC)
- `HR100` - Holding Relay

---

## 🎯 Resumen Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/dvasquez01/PyOmron-FINS-Complete.git
cd PyOmron-FINS-Complete

# 2. Instalar
pip install -e .

# 3. Usar
from pyomron_fins import FinsClient
config = FinsClient.simple_config('TU_IP_PLC')
with FinsClient(**config) as client:
    valor = client.read('DM100')[0]
    print(f"Valor: {valor}")
```

---

## ❓ ¿Necesitas Ayuda?

1. **Revisa los ejemplos** en la carpeta `examples/`
2. **Lee el README.md** para documentación completa
3. **Verifica tu configuración de PLC** (IP, modo RUN)
4. **Prueba con diferentes direcciones de memoria**

¿Sigues teniendo problemas? Comparte el error exacto que ves.

---

**¡Felicidades! Ya puedes controlar tu PLC OMRON con Python. 🚀**