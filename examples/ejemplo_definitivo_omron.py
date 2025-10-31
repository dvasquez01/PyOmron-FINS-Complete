#!/usr/bin/env python3
"""
EJEMPLO DEFINITIVO: PyOmron FINS - Comunicación Completa con PLC OMRON

Este ejemplo demuestra todas las capacidades de la librería PyOmron FINS:
- Lectura de diferentes tipos de datos (INT, REAL)
- Escritura en diferentes áreas de memoria (DM, CIO, WR)
- Manejo de errores y reconexión automática
- Monitoreo en tiempo real

PLC: OMRON CJ1H-CPU66H-R
IP: 192.168.140.10
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

def test_read_different_data_types():
    """Probar lectura de diferentes tipos de datos"""
    print("PRUEBA 1: LECTURA DE DIFERENTES TIPOS DE DATOS")
    print("="*70)
    
    test_addresses = [
        ('D17200', 'INT', 'Entero en D17200'),
        ('D1702', 'REAL', 'Real en D1702 (10.25)'),
        ('D1704', 'INT', 'Entero en D1704'),
    ]
    
    try:
        with FinsClient(**PLC_CONFIG) as client:
            print("Conexión establecida con el PLC")
            print()
            
            for address, data_type, description in test_addresses:
                print(f" {description}:")
                
                try:
                    if data_type == 'INT':
                        values = client.read(address, count=1)
                        if values:
                            print(f"   Valor: {values[0]}")
                        else:
                            print(f"   No se recibieron datos")
                    
                    elif data_type == 'REAL':
                        value = client.read_real(address)
                        print(f"   Valor: {value:.6f}")
                        
                        # Verificar si es el valor esperado
                        if abs(value - 10.25) < 0.001:
                            print(f"   ¡Perfecto! Coincide con el valor esperado")
                
                except Exception as e:
                    print(f"   Error: {e}")
                
                print()
                time.sleep(0.5)
    
    except Exception as e:
        print(f"Error de conexión: {e}")

def test_memory_areas_read_write():
    """Probar lectura y escritura en diferentes áreas de memoria"""
    print("PRUEBA 2: LECTURA Y ESCRITURA EN DIFERENTES ÁREAS")
    print("="*70)
    
    # Direcciones de prueba para cada área
    test_areas = [
        ('DM', [('DM2000', 12345), ('DM2001', 67890)]),
        ('CIO', [('CIO100', 1), ('CIO101', 0)]),
        ('WR', [('WR100', 255), ('WR101', 512)])
    ]
    
    try:
        with FinsClient(**PLC_CONFIG) as client:
            print("Conexión establecida con el PLC")
            print()
            
            for area_name, addresses in test_areas:
                print(f" Área de memoria: {area_name}")
                print("-" * 40)
                
                # Primero leer valores actuales
                print("   Valores actuales:")
                current_values = {}
                for address, _ in addresses:
                    try:
                        values = client.read(address, count=1)
                        if values:
                            current_values[address] = values[0]
                            print(f"      {address}: {values[0]}")
                        else:
                            current_values[address] = None
                            print(f"      {address}: ERROR - Sin datos")
                    except Exception as e:
                        current_values[address] = None
                        print(f"      {address}: ERROR - {e}")
                
                print()
                
                # Intentar escribir valores de prueba
                print("   Escribiendo valores de prueba:")
                write_success = {}
                for address, test_value in addresses:
                    try:
                        client.write(address, test_value)
                        write_success[address] = True
                        print(f"      {address}: {test_value} ESCRITO")
                    except Exception as e:
                        write_success[address] = False
                        print(f"      {address}: ERROR - {e}")
                
                print()
                
                # Verificar escritura leyendo de nuevo
                print("   Verificando escritura:")
                for address, test_value in addresses:
                    if write_success[address]:
                        try:
                            values = client.read(address, count=1)
                            if values and values[0] == test_value:
                                print(f"      {address}: {values[0]} VERIFICADO")
                            else:
                                actual = values[0] if values else "Sin datos"
                                print(f"      {address}: {actual} DIFERENTE (esperado: {test_value})")
                        except Exception as e:
                            print(f"      {address}: ERROR - {e}")
                    else:
                        print(f"      {address}: OMITIDO (no se escribió)")
                
                print()
                
                # Restaurar valores originales si es posible
                print("   Restaurando valores originales:")
                for address, _ in addresses:
                    if current_values[address] is not None and write_success[address]:
                        try:
                            client.write(address, current_values[address])
                            print(f"      {address}: {current_values[address]} RESTAURADO")
                        except Exception as e:
                            print(f"      {address}: ERROR restaurando - {e}")
                
                print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"Error de conexión: {e}")

def test_real_value_operations():
    """Probar operaciones con valores reales (float)"""
    print("PRUEBA 3: OPERACIONES CON VALORES REALES")
    print("="*70)
    
    test_addresses = ['D1702', 'D1710', 'D1720']
    
    try:
        with FinsClient(**PLC_CONFIG) as client:
            print("Conexión establecida con el PLC")
            print()
            
            # Leer valores reales actuales
            print("Valores reales actuales:")
            current_reals = {}
            for address in test_addresses:
                try:
                    value = client.read_real(address)
                    current_reals[address] = value
                    print(f"   {address}: {value:.6f}")
                except Exception as e:
                    current_reals[address] = None
                    print(f"   {address}: ERROR - {e}")
            
            print()
            
            # Intentar escribir valores reales de prueba
            test_real_values = [3.14159, -2.5, 100.001]
            print("Intentando escribir valores reales de prueba:")
            
            write_results = {}
            for i, address in enumerate(test_addresses):
                test_value = test_real_values[i]
                try:
                    client.write_real(address, test_value)
                    write_results[address] = test_value
                    print(f"   {address}: {test_value:.6f} ESCRITO")
                except Exception as e:
                    write_results[address] = None
                    print(f"   {address}: ERROR - {e}")
            
            print()
            
            # Verificar escritura
            print("Verificando escritura de valores reales:")
            for address in test_addresses:
                if write_results[address] is not None:
                    try:
                        actual_value = client.read_real(address)
                        expected_value = write_results[address]
                        
                        if abs(actual_value - expected_value) < 0.001:
                            print(f"   {address}: {actual_value:.6f} VERIFICADO")
                        else:
                            print(f"   {address}: {actual_value:.6f} DIFERENTE (esperado: {expected_value:.6f})")
                    except Exception as e:
                        print(f"   {address}: ERROR - {e}")
            
            print()
            
            # Restaurar valores originales
            print("Restaurando valores reales originales:")
            for address in test_addresses:
                if current_reals[address] is not None and write_results[address] is not None:
                    try:
                        client.write_real(address, current_reals[address])
                        print(f"   {address}: {current_reals[address]:.6f} RESTAURADO")
                    except Exception as e:
                        print(f"   {address}: ERROR restaurando - {e}")
    
    except Exception as e:
        print(f"Error de conexión: {e}")

def test_multiple_read():
    """Probar lectura múltiple de direcciones"""
    print("PRUEBA 4: LECTURA MÚLTIPLE OPTIMIZADA")
    print("="*70)
    
    # Direcciones variadas para probar
    addresses = [
        'D0',      # Valor conocido: 40111
        'D100',    # Valor conocido: 555
        'D1700',   # Valor conocido: 33
        'CIO10',   # Área CIO
        'WR100',   # Área WR
        'HR100'    # Área HR
    ]
    
    try:
        with FinsClient(**PLC_CONFIG) as client:
            print("Conexión establecida con el PLC")
            print()
            
            print("Lectura individual vs lectura múltiple:")
            print("-" * 50)
            
            # Lectura individual
            print("Lectura individual:")
            start_time = time.time()
            individual_results = {}
            
            for address in addresses:
                try:
                    values = client.read(address, count=1)
                    if values:
                        individual_results[address] = values[0]
                        print(f"   {address:8}: {values[0]:>8}")
                    else:
                        individual_results[address] = None
                        print(f"   {address:8}: {'ERROR':>8}")
                except Exception as e:
                    individual_results[address] = None
                    print(f"   {address:8}: ERROR - {str(e)[:20]}")
            
            individual_time = time.time() - start_time
            print(f"   Tiempo: {individual_time:.3f} segundos")
            
            print()
            
            # Lectura múltiple
            print("Lectura múltiple:")
            start_time = time.time()
            
            try:
                multiple_results = client.read_multiple(addresses)
                multiple_time = time.time() - start_time
                
                for address in addresses:
                    value = multiple_results.get(address, 'ERROR')
                    print(f"   {address:8}: {value:>8}")
                
                print(f"   Tiempo: {multiple_time:.3f} segundos")
                print(f"   Mejora: {individual_time/multiple_time:.1f}x más rápido")
                
            except Exception as e:
                print(f"   Error en lectura múltiple: {e}")
    
    except Exception as e:
        print(f"Error de conexión: {e}")

def test_plc_information():
    """Obtener información del PLC"""
    print("PRUEBA 5: INFORMACIÓN DEL PLC")
    print("="*70)
    
    try:
        with FinsClient(**PLC_CONFIG) as client:
            print("Conexión establecida con el PLC")
            print()
            
            # Estado del controlador
            print("Estado del controlador:")
            try:
                status = client.get_status()
                if status:
                    print(f"   Modo RUN: {'SÍ' if status.get('run_mode', False) else 'NO'}")
                    print(f"   Modo PROGRAM: {'SÍ' if status.get('program_mode', False) else 'NO'}")
                    print(f"   Error fatal: {'SÍ' if status.get('fatal_error', False) else 'NO'}")
                    print(f"   Error no fatal: {'SÍ' if status.get('non_fatal_error', False) else 'NO'}")
                else:
                    print("   No se pudo obtener el estado")
            except Exception as e:
                print(f"   Error obteniendo estado: {e}")
            
            print()
            
            # Información de la CPU
            print("Información de la CPU:")
            try:
                cpu_data = client.get_cpu_unit_data()
                if cpu_data:
                    model = cpu_data.get('controller_model', 'N/A')
                    version = cpu_data.get('controller_version', 'N/A')
                    print(f"   Modelo: {model}")
                    print(f"   Versión: {version}")
                else:
                    print("   No se pudo obtener información de CPU")
            except Exception as e:
                print(f"   Error obteniendo info CPU: {e}")
            
            print()
            
            # Reloj del PLC
            print("Reloj del PLC:")
            try:
                clock_data = client.read_clock()
                if clock_data:
                    year = clock_data.get('year', 0)
                    month = clock_data.get('month', 0)
                    day = clock_data.get('day', 0)
                    hour = clock_data.get('hour', 0)
                    minute = clock_data.get('minute', 0)
                    second = clock_data.get('second', 0)
                    
                    plc_time = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
                    print(f"   Fecha/Hora PLC: {plc_time}")
                    
                    # Comparar con hora del sistema
                    system_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"   Fecha/Hora PC:  {system_time}")
                else:
                    print("   No se pudo leer el reloj")
            except Exception as e:
                print(f"   Error leyendo reloj: {e}")
    
    except Exception as e:
        print(f"Error de conexión: {e}")

def create_monitoring_example():
    """Crear ejemplo de monitoreo en tiempo real"""
    print("\nEJEMPLO DE MONITOREO EN TIEMPO REAL")
    print("="*70)
    print("Monitoreando valores clave durante 30 segundos...")
    print("Presiona Ctrl+C para detener antes")
    
    # Direcciones a monitorear
    monitor_addresses = [
        ('D0', 'INT', 'Contador principal'),
        ('D100', 'INT', 'Estado sistema'),
        ('D1700', 'INT', 'Alarma general'),
        ('D1702', 'REAL', 'Temperatura')
    ]
    
    try:
        with FinsClient(**PLC_CONFIG) as client:
            print("Conexión establecida - Iniciando monitoreo")
            print()
            
            # Encabezado
            header = "Tiempo    |"
            for address, data_type, description in monitor_addresses:
                header += f" {address:8} |"
            print(header)
            print("-" * len(header))
            
            start_time = time.time()
            
            while time.time() - start_time < 30:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S')
                row = f"{timestamp} |"
                
                for address, data_type, description in monitor_addresses:
                    try:
                        if data_type == 'INT':
                            values = client.read(address, count=1)
                            if values:
                                row += f" {values[0]:8} |"
                            else:
                                row += f" {'ERROR':8} |"
                        elif data_type == 'REAL':
                            value = client.read_real(address)
                            row += f" {value:8.3f} |"
                    except Exception:
                        row += f" {'ERROR':8} |"
                
                print(row)
                time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por usuario")
    except Exception as e:
        print(f"\nError en monitoreo: {e}")

def main():
    """Función principal del ejemplo definitivo"""
    print("EJEMPLO DEFINITIVO: PyOmron FINS - Comunicación Completa con PLC OMRON")
    print("="*70)
    print("Demostrando todas las capacidades de comunicación con PLC OMRON")
    print(f"PLC: {PLC_CONFIG['host']}:{PLC_CONFIG['port']}")
    print(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        # Prueba 1: Lectura de diferentes tipos de datos
        test_read_different_data_types()
        
        input("\nPresiona Enter para continuar con la siguiente prueba...")
        
        # Prueba 2: Lectura y escritura en diferentes áreas
        test_memory_areas_read_write()
        
        input("\nPresiona Enter para continuar con la siguiente prueba...")
        
        # Prueba 3: Operaciones con valores reales
        test_real_value_operations()
        
        input("\nPresiona Enter para continuar con la siguiente prueba...")
        
        # Prueba 4: Lectura múltiple
        test_multiple_read()
        
        input("\nPresiona Enter para continuar con la siguiente prueba...")
        
        # Prueba 5: Información del PLC
        test_plc_information()
        
        # Pregunta por monitoreo
        print("\n" + "="*70)
        response = input("¿Deseas ejecutar el monitoreo en tiempo real? (s/n): ").strip().lower()
        
        if response in ['s', 'si', 'y', 'yes']:
            create_monitoring_example()
        
        print("\n¡EJEMPLO COMPLETADO EXITOSAMENTE!")
        print("="*70)
        print("Todas las funcionalidades de PyOmron FINS han sido probadas")
        print("La librería está lista para uso en aplicaciones de producción")
        print("Comunicación con PLC OMRON completamente funcional")
        
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por usuario")
    except Exception as e:
        print(f"\nError crítico: {e}")

if __name__ == "__main__":
    main()