#!/usr/bin/env python3
"""
EJEMPLO DE CONFIGURACIÓN SIMPLIFICADA - PyOmron FINS

Este ejemplo demuestra cómo usar la nueva API simplificada que abstrae
los detalles técnicos de FINS, haciendo la librería más fácil de usar.
"""

import sys
import time
from pathlib import Path

# Agregar el directorio del paquete al path
sys.path.insert(0, str(Path(__file__).parent))

from pyomron_fins import FinsClient, FinsNode

def ejemplo_configuracion_simple():
    """Ejemplo de configuración ultra-simple"""
    print("EJEMPLO 1: CONFIGURACIÓN ULTRA-SIMPLE")
    print("=" * 50)
    
    # Configuración más simple posible
    config = FinsClient.simple_config('192.168.140.10')
    
    print("Configuración generada automáticamente:")
    print(f"  Host: {config['host']}")
    print(f"  PLC Nodo: {config['DA1']} (DNA={config['DNA']}, DA2={config['DA2']})")
    print(f"  PC Nodo: {config['SA1']} (SNA={config['SNA']}, SA2={config['SA2']})")
    print()
    
    try:
        with FinsClient(**config) as client:
            print("Conectado exitosamente al PLC")
            valor = client.read('D0')[0]
            print(f"D0: {valor}")
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_configuracion_avanzada():
    """Ejemplo de configuración avanzada con FinsNode"""
    print("\nEJEMPLO 2: CONFIGURACIÓN AVANZADA CON FinsNode")
    print("=" * 50)
    
    # Crear nodos de manera explícita
    plc = FinsNode.plc_node(node=0, network=0)  # PLC en red 0, nodo 0
    pc = FinsNode.pc_node(node=1, network=0)    # PC en red 0, nodo 1
    
    print("Nodos creados:")
    print(f"  PLC: {plc}")
    print(f"  PC:  {pc}")
    print()
    
    # Crear configuración usando nodos
    config = FinsClient.create_config(
        host='192.168.140.10',
        plc_node=plc,
        pc_node=pc,
        protocol='udp'
    )
    
    print("Configuración FINS generada:")
    print(f"  DNA/DA1/DA2: {config['DNA']}/{config['DA1']}/{config['DA2']} (Destino - PLC)")
    print(f"  SNA/SA1/SA2: {config['SNA']}/{config['SA1']}/{config['SA2']} (Origen - PC)")
    print()
    
    try:
        with FinsClient(**config) as client:
            print("Conectado exitosamente al PLC")
            
            # Leer varios valores
            valores = client.read('D0', count=5)
            print(f"D0-D4: {valores}")
            
            # Leer valor real
            temp = client.read_real('D1702')
            print(f"Temperatura (D1702): {temp:.2f}°C")
    
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_conexion_rapida():
    """Ejemplo de conexión rápida"""
    print("\nEJEMPLO 3: CONEXIÓN RÁPIDA")
    print("=" * 50)
    
    try:
        # Conexión instantánea
        client = FinsClient.quick_connect('192.168.140.10')
        
        print("Conexión rápida establecida")
        
        # Realizar operaciones
        status = client.get_status()
        print(f"Estado del PLC: {'RUN' if status.get('run_mode') else 'STOP'}")
        
        # Leer información del CPU
        cpu_info = client.get_cpu_unit_data()
        if cpu_info:
            print(f"Modelo CPU: {cpu_info.get('controller_model', 'N/A')}")
            print(f"Versión: {cpu_info.get('controller_version', 'N/A')}")
        
        client.disconnect()
        print("Conexión cerrada")
        
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_redes_multiples():
    """Ejemplo de configuración para redes múltiples"""
    print("\nEJEMPLO 4: CONFIGURACIÓN PARA REDES MÚLTIPLES")
    print("=" * 50)
    
    # Simular red industrial con múltiples PLCs
    plc_principal = FinsNode(network=1, node=10, unit=0)  # Red 1, PLC principal
    plc_backup = FinsNode(network=1, node=11, unit=0)     # Red 1, PLC backup
    pc_supervisor = FinsNode(network=1, node=100, unit=0) # PC supervisor
    
    print("Red industrial simulada:")
    print(f"  PLC Principal: {plc_principal}")
    print(f"  PLC Backup:    {plc_backup}")
    print(f"  PC Supervisor: {pc_supervisor}")
    print()
    
    # Configuración para comunicarse con PLC principal
    config = FinsClient.create_config(
        host='192.168.140.10',  # IP del PLC principal
        plc_node=plc_principal,
        pc_node=pc_supervisor
    )
    
    print("Configuración generada para PLC principal:")
    print(f"  Host: {config['host']}")
    print(f"  Destino (PLC): Red{config['DNA']}.Nodo{config['DA1']}.Unidad{config['DA2']}")
    print(f"  Origen (PC):   Red{config['SNA']}.Nodo{config['SA1']}.Unidad{config['SA2']}")
    print()
    
    # Nota: En una red real, cada PLC tendría su propia IP
    print("Nota: En implementación real, cada PLC tendría IP diferente")

def comparar_metodos():
    """Comparar métodos antiguos vs nuevos"""
    print("\nCOMPARACIÓN: MÉTODO ANTIGUO VS NUEVO")
    print("=" * 50)
    
    print("ANTES (difícil de recordar):")
    config_antiguo = {
        'host': '192.168.140.10',
        'port': 9600,
        'protocol': 'udp',
        'timeout': 5.0,
        'ICF': 0x80, 'DNA': 0x00, 'DA1': 0x00, 'DA2': 0x00,
        'SNA': 0x00, 'SA1': 0x01, 'SA2': 0x00
    }
    print("  Configuración manual con valores hexadecimales")
    print(f"  {len(str(config_antiguo))} caracteres de configuración")
    print()
    
    print("AHORA (fácil de usar):")
    config_nuevo = FinsClient.simple_config('192.168.140.10')
    print("  FinsClient.simple_config('192.168.140.10')")
    print("  ¡Una sola línea!")
    print()
    
    print("O usando nodos explícitos:")
    plc = FinsNode.plc_node(node=5, network=1)
    pc = FinsNode.pc_node(node=10, network=1)
    config_avanzado = FinsClient.create_config('192.168.140.10', plc_node=plc, pc_node=pc)
    print("  plc = FinsNode.plc_node(node=5, network=1)")
    print("  pc = FinsNode.pc_node(node=10, network=1)")
    print("  config = FinsClient.create_config('192.168.140.10', plc_node=plc, pc_node=pc)")
    print()
    
    print("Resultado generado automáticamente:")
    print(f"  PLC -> Red{config_nuevo['DNA']}.Nodo{config_nuevo['DA1']}.Unidad{config_nuevo['DA2']}")
    print(f"  PC  -> Red{config_nuevo['SNA']}.Nodo{config_nuevo['SA1']}.Unidad{config_nuevo['SA2']}")

if __name__ == "__main__":
    print("EJEMPLOS DE CONFIGURACIÓN SIMPLIFICADA - PyOmron FINS")
    print("=" * 60)
    
    # Ejecutar ejemplos
    ejemplo_configuracion_simple()
    ejemplo_configuracion_avanzada()
    ejemplo_conexion_rapida()
    ejemplo_redes_multiples()
    comparar_metodos()
    
    print("\n" + "=" * 60)
    print("RESUMEN DE LA NUEVA API SIMPLIFICADA:")
    print("• FinsClient.simple_config() - Para casos comunes")
    print("• FinsClient.create_config() - Para configuraciones avanzadas")
    print("• FinsClient.quick_connect() - Conexión instantánea")
    print("• FinsNode - Para representar dispositivos en la red")
    print("• Abstracción completa de valores hexadecimales FINS")
    print("• API intuitiva y fácil de recordar")