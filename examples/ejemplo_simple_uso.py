#!/usr/bin/env python3
"""
EJEMPLO DE USO SIMPLE - PyOmron FINS
====================================

Este es un ejemplo simple y directo de cómo usar la librería PyOmron FINS
para comunicarse con un PLC OMRON CJ1H-CPU66H-R.

Demuestra las operaciones más comunes que necesitarás en aplicaciones reales.
"""

import sys
import time
from pathlib import Path

# Agregar el directorio del paquete al path
sys.path.insert(0, str(Path(__file__).parent))

from pyomron_fins import FinsClient

def ejemplo_simple():
    """Ejemplo simple de uso de PyOmron FINS"""
    
    # Configuración del PLC (ajusta la IP según tu PLC)
    config = {
        'host': '192.168.140.10',  # IP del PLC
        'port': 9600,              # Puerto FINS estándar
        'protocol': 'udp',         # UDP es más rápido
        'timeout': 5.0,            # Timeout en segundos
        # Configuración FINS específica para OMRON CJ1H
        'ICF': 0x80, 'DNA': 0x00, 'DA1': 0x00, 'DA2': 0x00,
        'SNA': 0x00, 'SA1': 0x01, 'SA2': 0x00
    }
    
    print("EJEMPLO SIMPLE - PyOmron FINS")
    print("="*50)
    
    try:
        # Conectar al PLC
        with FinsClient(**config) as client:
            print(f"Conectado al PLC en {config['host']}")
            print()
            
            # 1. LEER VALORES ENTEROS
            print("Leyendo valores enteros:")
            try:
                # Puedes usar formato "D" o "DM" - ambos funcionan
                valor_d0 = client.read('D0')[0]        # Formato D
                valor_d100 = client.read('DM100')[0]   # Formato DM
                valor_d1700 = client.read('D1700')[0]
                
                print(f"   D0: {valor_d0}")
                print(f"   D100: {valor_d100}")  
                print(f"   D1700: {valor_d1700}")
            except Exception as e:
                print(f"   Error leyendo enteros: {e}")
            
            print()
            
            # 2. LEER VALORES REALES (FLOAT)
            print("Leyendo valores reales:")
            try:
                temperatura = client.read_real('D1702')  # Valor real en D1702
                print(f"   Temperatura (D1702): {temperatura:.3f}")
            except Exception as e:
                print(f"   Error leyendo real: {e}")
            
            print()
            
            # 3. ESCRIBIR UN VALOR ENTERO
            print("Escribiendo valor entero:")
            try:
                # Escribir un valor de prueba en D2000
                valor_prueba = 12345
                client.write('D2000', valor_prueba)
                print(f"   Escrito {valor_prueba} en D2000")
                
                # Verificar escritura
                valor_leido = client.read('D2000')[0]
                if valor_leido == valor_prueba:
                    print(f"   Verificado: D2000 = {valor_leido}")
                else:
                    print(f"   Diferente: esperado {valor_prueba}, leído {valor_leido}")
                
            except Exception as e:
                print(f"   Error escribiendo entero: {e}")
            
            print()
            
            # 4. ESCRIBIR UN VALOR REAL
            print("Escribiendo valor real:")
            try:
                # Escribir un valor real de prueba
                valor_real = 3.14159
                client.write_real('D1710', valor_real)
                print(f"   Escrito {valor_real:.5f} en D1710")
                
                # Verificar escritura
                valor_real_leido = client.read_real('D1710')
                if abs(valor_real_leido - valor_real) < 0.001:
                    print(f"   Verificado: D1710 = {valor_real_leido:.5f}")
                else:
                    print(f"   Diferente: esperado {valor_real:.5f}, leído {valor_real_leido:.5f}")
                    
            except Exception as e:
                print(f"   Error escribiendo real: {e}")
            
            print()
            
            # 5. INFORMACIÓN DEL PLC
            print("Información del PLC:")
            try:
                status = client.get_status()
                cpu_info = client.get_cpu_unit_data()
                
                if status:
                    modo = "RUN" if status.get('run_mode') else "STOP"
                    print(f"   Modo: {modo}")
                
                if cpu_info:
                    modelo = cpu_info.get('controller_model', 'N/A')
                    version = cpu_info.get('controller_version', 'N/A')
                    print(f"   Modelo: {modelo}")
                    print(f"   Versión: {version}")
                    
            except Exception as e:
                print(f"   Error obteniendo info: {e}")
            
            print()
            print("¡Ejemplo completado exitosamente!")
            
    except Exception as e:
        print(f"Error de conexión: {e}")
        print("Verifica:")
        print("   - IP del PLC correcta")
        print("   - PLC encendido y en red")
        print("   - Puerto 9600 abierto")
        print("   - Configuración FINS correcta")

def ejemplo_monitoreo_simple():
    """Ejemplo de monitoreo simple de algunas variables"""
    
    config = {
        'host': '192.168.140.10',
        'port': 9600, 'protocol': 'udp', 'timeout': 5.0,
        'ICF': 0x80, 'DNA': 0x00, 'DA1': 0x00, 'DA2': 0x00,
        'SNA': 0x00, 'SA1': 0x01, 'SA2': 0x00
    }
    
    print("\nMONITOREO SIMPLE")
    print("="*50)
    print("Monitoreando D0, D100, D1702 durante 15 segundos...")
    print("(Presiona Ctrl+C para detener)")
    
    try:
        with FinsClient(**config) as client:
            print("Conectado - Iniciando monitoreo")
            print("\nTiempo   | D0       | D100     | D1702    |")
            print("-" * 45)
            
            start_time = time.time()
            
            while time.time() - start_time < 15:
                try:
                    timestamp = time.strftime('%H:%M:%S')
                    
                    # Leer valores
                    d0 = client.read('D0')[0]
                    d100 = client.read('D100')[0] 
                    d1702 = client.read_real('D1702')
                    
                    print(f"{timestamp} | {d0:8} | {d100:8} | {d1702:8.3f} |")
                    
                except Exception as e:
                    print(f"{time.strftime('%H:%M:%S')} | ERROR: {e}")
                
                time.sleep(2)
                
    except KeyboardInterrupt:
        print("\nMonitoreo detenido")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    print("EJEMPLOS SIMPLES DE PYOMRON FINS")
    print("="*60)
    
    # Ejecutar ejemplo básico
    ejemplo_simple()
    
    # Preguntar si quiere monitoreo
    print("\n" + "="*60)
    respuesta = input("¿Ejecutar ejemplo de monitoreo? (s/n): ").strip().lower()
    
    if respuesta in ['s', 'si', 'y', 'yes']:
        ejemplo_monitoreo_simple()
    
    print("\nEjemplos terminados")
    print("Revisa el código para aprender cómo usar PyOmron FINS")