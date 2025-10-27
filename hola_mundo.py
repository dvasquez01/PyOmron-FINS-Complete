#!/usr/bin/env python3
"""
HOLA MUNDO - PyOmron FINS
=========================

Este es el ejemplo más simple posible para empezar con PyOmron FINS.
Solo cambia la IP de tu PLC y ejecuta este archivo.

¿No sabes la IP de tu PLC? Lee la GUIA_INSTALACION_USUARIO_NUEVO.md
"""

from pyomron_fins import FinsClient

def main():
    # 🏭 CAMBIA ESTA IP POR LA DE TU PLC
    IP_DE_TU_PLC = '192.168.1.100'  # ← ¡MODIFICA AQUÍ!

    print("🤖 Conectando a PLC OMRON...")
    print(f"📍 IP del PLC: {IP_DE_TU_PLC}")
    print("-" * 40)

    try:
        # ✨ LA MAGIA: Una sola línea de configuración
        config = FinsClient.simple_config(IP_DE_TU_PLC)

        with FinsClient(**config) as client:
            print("✅ ¡Conectado exitosamente!")
            print()

            # 📖 Leer algunos valores de ejemplo
            print("📊 Leyendo datos del PLC:")

            # Leer D0 (Data Memory)
            try:
                valor_d0 = client.read('D0')[0]
                print(f"   D0: {valor_d0}")
            except Exception as e:
                print(f"   D0: No disponible ({e})")

            # Leer DM100 (Data Memory)
            try:
                valor_dm100 = client.read('DM100')[0]
                print(f"   DM100: {valor_dm100}")
            except Exception as e:
                print(f"   DM100: No disponible ({e})")

            # Leer temperatura (si tienes sensor)
            try:
                temp = client.read_real('DM1702')
                print(f"   Temperatura: {temp:.1f}°C")
            except Exception as e:
                print(f"   Temperatura: No disponible (normal)")

            print()
            print("🎉 ¡Tu primer programa con PLC OMRON funcionó!")

            # 📝 Información adicional del PLC
            try:
                status = client.get_status()
                cpu_info = client.get_cpu_unit_data()

                print()
                print("ℹ️  Información del PLC:")
                print(f"   Modo RUN: {status.get('run_mode', 'Desconocido')}")
                print(f"   CPU: {cpu_info.get('controller_model', 'Desconocido')}")
            except:
                pass

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Posibles soluciones:")
        print("   1. Verifica que la IP del PLC sea correcta")
        print("   2. Asegúrate de que el PLC esté encendido")
        print("   3. Verifica que no haya firewall bloqueando el puerto 9600")
        print("   4. Prueba hacer ping al PLC desde la terminal")
        print()
        print("📖 Lee GUIA_INSTALACION_USUARIO_NUEVO.md para más ayuda")

if __name__ == "__main__":
    main()