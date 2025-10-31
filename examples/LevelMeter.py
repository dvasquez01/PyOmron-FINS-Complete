
#!/usr/bin/env python3
"""
LEVEL METER - PyOmron FINS
==========================

Script para escribir valores de nivel (float) en el PLC OMRON.
Ejemplo de escritura de valores reales en direcciones específicas.

Dirección: D1614 (Level Meter value)
"""

import sys
import time
import datetime
from pathlib import Path

# Agregar el directorio del paquete al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyomron_fins import FinsClient
from pyomron_fins.exceptions import FinsError, ReadError, WriteError

# Configuración del PLC
PLC_CONFIG = {
    'host': '192.168.140.10',
    'port': 9600,
    'protocol': 'udp',
    'timeout': 10.0,
    'ICF': 0x80,
    'DNA': 0x00,
    'DA1': 0x00,
    'DA2': 0x00,
    'SNA': 0x00,
    'SA1': 0x01,
    'SA2': 0x00
}
def write_level_value(address, value):
    """
    Escribir valor de nivel en el PLC
    
    Args:
        address: Dirección de memoria (ej: 'D1614')
        value: Valor real/float a escribir
    """
    print("="*50)
    print("LEVEL METER - Escritura de Valor")
    print("="*50)
    print(f"PLC: {PLC_CONFIG['host']}:{PLC_CONFIG['port']}")
    print(f"Dirección: {address}")
    print(f"Valor a escribir: {value}")
    print(f"Timestamp: {datetime.datetime.now()}")
    print("-"*50)

    try:
        with FinsClient(**PLC_CONFIG) as client:
            print(f"✅ Conectado al PLC")
            
            # Leer valor actual
            try:
                current_value = client.read_real(address)
                print(f"📖 Valor actual: {current_value:.3f}")
            except Exception as e:
                print(f"⚠️  No se pudo leer valor actual: {e}")
                current_value = None
            
            # Escribir nuevo valor real
            print(f"✍️  Escribiendo valor {value}...")
            client.write_real(address, value)
            
            # Verificar escritura leyendo de nuevo
            time.sleep(0.1)  # Pequeña pausa para asegurar escritura
            written_value = client.read_real(address)
            print(f"🔍 Valor verificado: {written_value:.3f}")
            
            # Validar precisión
            if abs(written_value - value) < 0.001:
                print("✅ Escritura exitosa - valores coinciden")
                if current_value is not None:
                    change = written_value - current_value
                    print(f"📊 Cambio: {change:+.3f} ({current_value:.3f} → {written_value:.3f})")
            else:
                print(f"⚠️  Advertencia: valor esperado {value:.3f}, obtenido {written_value:.3f}")
                print(f"   Diferencia: {abs(written_value - value):.6f}")
                
            print("-"*50)
            print("✅ Operación completada")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Verificaciones:")
        print("   - IP del PLC correcta")
        print("   - PLC encendido y en red")
        print("   - Dirección de memoria accesible")
        print("   - Permisos de escritura habilitados")

def interactive_mode():
    """Modo interactivo para escribir múltiples valores"""
    print("="*60)
    print("LEVEL METER - MODO INTERACTIVO")
    print("="*60)
    print("Escribe valores de nivel en tiempo real")
    print("Comandos disponibles:")
    print("  - Número: Escribir valor (ej: 150.5)")
    print("  - 'read': Leer valor actual")
    print("  - 'quit' o 'exit': Salir")
    print("-"*60)
    
    address = 'D1614'
    
    try:
        with FinsClient(**PLC_CONFIG) as client:
            print(f"✅ Conectado al PLC {PLC_CONFIG['host']}")
            
            while True:
                try:
                    user_input = input(f"\n[{address}] Comando: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Saliendo...")
                        break
                    elif user_input.lower() == 'read':
                        current_value = client.read_real(address)
                        print(f"📖 Valor actual: {current_value:.3f}")
                    else:
                        try:
                            new_value = float(user_input)
                            print(f"✍️  Escribiendo {new_value}...")
                            client.write_real(address, new_value)
                            
                            # Verificar
                            written_value = client.read_real(address)
                            print(f"✅ Escrito: {written_value:.3f}")
                            
                        except ValueError:
                            print("❌ Error: Ingresa un número válido o comando")
                            
                except KeyboardInterrupt:
                    print("\n👋 Interrupción del usuario")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1:
        # Modo comando: python LevelMeter.py <valor>
        try:
            value = float(sys.argv[1])
            address = 'D1614'
            write_level_value(address, value)
        except ValueError:
            print("❌ Error: El valor debe ser un número")
            print("Uso: python LevelMeter.py <valor>")
            print("Ejemplo: python LevelMeter.py 185.5")
    else:
        # Modo interactivo
        interactive_mode()

if __name__ == "__main__":
    main()