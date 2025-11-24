#!/usr/bin/env python3
"""
Mi primer programa con PyOmron FINS
"""

from pyomron_fins import FinsClient

# Configuración ultra-simple (¡una sola línea!)
config = FinsClient.simple_config('192.168.140.10')  # ← Cambia por la IP de tu PLC

try:
    with FinsClient(**config) as client:
        print("✅ Conectado al PLC!")
        
        # Leer un valor
        valor = client.read('D0')[0]
        print(f"Valor en D0: {valor}")
        
        # Leer temperatura (si tienes sensor)
        try:
            temp = client.read_real('D1702')
            print(f"Temperatura: {temp:.2f}°C")
        except:
            print("Nota: D1702 no disponible (normal)")

except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Verifica que:")
    print("   - La IP del PLC sea correcta")
    print("   - El PLC esté encendido")
    print("   - No haya firewall bloqueando el puerto 9600")