# 🔧 Solución de Problemas Comunes - PyOmron FINS

Esta guía te ayuda a resolver los problemas más comunes que enfrentan los usuarios nuevos.

---

## 📋 Lista Rápida de Verificación

Antes de ejecutar cualquier programa, verifica:

### ✅ Requisitos Básicos
- [ ] Python 3.7+ instalado: `python --version`
- [ ] Librería instalada: `pip list | grep pyomron`
- [ ] PLC encendido y accesible
- [ ] IP del PLC correcta

### ✅ Conexión de Red
- [ ] PLC en la misma red que tu computadora
- [ ] Firewall no bloquea puerto 9600
- [ ] PLC configurado para comunicaciones FINS

---

## 🚨 Errores Comunes y Soluciones

### ❌ `ModuleNotFoundError: No module named 'pyomron_fins'`

**Problema:** La librería no está instalada correctamente.

**Soluciones:**
```bash
# Opción 1: Reinstalar
pip uninstall pyomron_fins
pip install -e .

# Opción 2: Verificar instalación
python -c "import pyomron_fins; print('OK')"

# Opción 3: Instalar desde GitHub
pip install git+https://github.com/dvasquez01/PyOmron-FINS-Complete.git
```

---

### ❌ `ConnectionError: Failed to connect to 192.168.X.X:9600`

**Problema:** No se puede conectar al PLC.

**Soluciones:**

#### 1. Verificar IP del PLC
```bash
# Hacer ping al PLC
ping 192.168.1.100

# Si no responde, la IP es incorrecta
```

#### 2. Verificar puerto y protocolo
```python
# Probar con TCP en lugar de UDP
config = FinsClient.simple_config('192.168.1.100', protocol='tcp')

# O cambiar puerto
config = FinsClient.simple_config('192.168.1.100', port=9600)
```

#### 3. Verificar firewall
```bash
# Windows: Apagar firewall temporalmente
# Linux: Verificar ufw/iptables
# macOS: Verificar firewall
```

#### 4. Verificar configuración del PLC
- PLC debe estar en modo **RUN** (no PROGRAM)
- Comunicaciones FINS deben estar habilitadas
- Puerto Ethernet debe estar configurado

---

### ❌ `TimeoutError: Operation timed out`

**Problema:** La conexión se establece pero las operaciones tardan demasiado.

**Soluciones:**
```python
# Aumentar timeout
config = FinsClient.simple_config('192.168.1.100', timeout=10.0)

# O con configuración avanzada
config = FinsClient.create_config(
    host='192.168.1.100',
    timeout=15.0
)
```

---

### ❌ `FinsError: MRES=1, SRES=1` o similares

**Problema:** Error específico del protocolo FINS.

**Posibles causas:**

#### 1. PLC en modo PROGRAM
```python
# Verificar estado del PLC
with FinsClient(**config) as client:
    status = client.get_status()
    print(f"RUN mode: {status.get('run_mode')}")
    print(f"PROGRAM mode: {status.get('program_mode')}")
```
**Solución:** Cambia el PLC a modo RUN desde el panel o CX-Programmer.

#### 2. Dirección de memoria incorrecta
```python
# Verificar direcciones válidas
# DM (Data Memory): DM0, DM100, DM1000
# CIO (Channel I/O): CIO10, CIO100
# WR (Work Relay): WR100
# HR (Holding Relay): HR100
```

#### 3. Área de memoria protegida
- **CIO/WR/HR**: Solo lectura en muchos PLC industriales
- **DM**: Lectura/escritura permitida
- Necesitas permisos especiales para escritura en áreas protegidas

---

### ❌ `ReadError` o `WriteError`

**Problema:** Error al leer/escribir datos.

**Soluciones:**

#### 1. Verificar dirección de memoria
```python
# Direcciones válidas
client.read('DM100')    # ✅ Correcto
client.read('D100')     # ✅ También correcto
client.read('100')      # ❌ Incorrecto, falta prefijo
```

#### 2. Verificar tipo de datos
```python
# Enteros
valor = client.read('DM100')[0]        # ✅ Un valor
valores = client.read('DM100', count=5) # ✅ Múltiples valores

# Floats
# temp = client.read_real('DM1702')      # ✅ Float de 32 bits
```

#### 3. Verificar límites
- **INT**: 0-65535 (16 bits)
- **REAL**: IEEE 754 float
- **Direcciones**: Dependen del modelo del PLC

---

## 🧪 Pruebas de Diagnóstico

### Test 1: Conexión Básica
```python
from pyomron_fins import FinsClient

config = FinsClient.simple_config('192.168.1.100')
try:
    with FinsClient(**config) as client:
        print("✅ Conexión básica: OK")
except Exception as e:
    print(f"❌ Conexión básica: {e}")
```

### Test 2: Estado del PLC
```python
with FinsClient(**config) as client:
    status = client.get_status()
    cpu_info = client.get_cpu_unit_data()

    print(f"RUN mode: {status.get('run_mode')}")
    print(f"CPU Model: {cpu_info.get('controller_model')}")
```

### Test 3: Lectura de Datos
```python
with FinsClient(**config) as client:
    # Probar diferentes áreas
    test_addresses = ['DM0', 'DM100', 'CIO0', 'WR0']

    for addr in test_addresses:
        try:
            value = client.read(addr)[0]
            print(f"{addr}: {value} ✅")
        except Exception as e:
            print(f"{addr}: Error ({e}) ❌")
```

---

## 🔍 Configuración del PLC OMRON

### Encontrar la IP del PLC:

#### Método A: CX-Programmer
1. Conecta al PLC
2. `PLC` → `Edit` → `Preferences` → `Built-in Ethernet`
3. Busca `IP Address`

#### Método B: Panel del PLC
1. Presiona `MODE/SET`
2. Navega a `Built-in Ethernet Settings`
3. Lee la IP

#### Método C: Software de red
- CX-Integrator
- Network Configurator

### Configuración típica:
- **IP:** 192.168.250.1 (o similar)
- **Subnet:** 255.255.255.0
- **Gateway:** 192.168.250.254
- **FINS Node:** 1 (para PC), 0 (para PLC)

---

## 🌐 Problemas de Red

### Firewall bloqueando conexiones
```bash
# Windows: Apagar firewall (temporal)
# Control Panel → System and Security → Windows Defender Firewall → Turn off

# Linux: Verificar reglas
sudo ufw status
sudo iptables -L

# macOS: System Preferences → Security & Privacy → Firewall
```

### PLC en VLAN diferente
- Verifica que PLC y PC estén en la misma VLAN
- O configura enrutamiento entre VLANs

### Conexión WiFi vs Ethernet
- Preferible usar cable Ethernet para comunicaciones industriales
- WiFi puede tener latencia/interferencias

---

## 📞 ¿Sigues teniendo problemas?

### Información útil para reportar bugs:
1. **Error exacto** que ves
2. **Modelo del PLC** (ej: CJ1H-CPU66H-R)
3. **Versión del software** del PLC
4. **Configuración de red** (IPs, máscaras)
5. **Sistema operativo** y versión de Python
6. **Comandos exactos** que ejecutas

### Comandos de diagnóstico:
```bash
# Verificar Python
python --version

# Verificar librería
python -c "import pyomron_fins; print('OK')"

# Verificar red
ping TU_IP_PLC

# Verificar puerto (Windows)
netstat -an | find "9600"

# Verificar puerto (Linux/Mac)
netstat -an | grep 9600
```

---

## 🎯 Resumen de Solución Rápida

```bash
# 1. Verificar instalación
python -c "from pyomron_fins import FinsClient; print('OK')"

# 2. Verificar conexión
ping TU_IP_PLC

# 3. Verificar PLC en RUN mode
# (desde panel del PLC o CX-Programmer)

# 4. Probar con timeout mayor
config = FinsClient.simple_config('TU_IP', timeout=10.0)

# 5. Probar direcciones simples
client.read('DM0')  # En lugar de CIO0 o WR0
```

¿Ninguna de estas soluciones funciona? Comparte el error exacto y tu configuración para ayudarte mejor.

---

**Recuerda: La mayoría de los problemas son de configuración de red o modo del PLC, no de la librería.**