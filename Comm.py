from pyomron_fins import FinsClient

# NUEVA FORMA: Configuración ultra-simple (¡una sola línea!)
config = FinsClient.simple_config('192.168.140.10')

# ANTES: Configuración manual con parámetros hexadecimales
# config = {
#     'host': '192.168.140.10',    # IP del PLC
#     'port': 9600,               # Puerto FINS
#     'protocol': 'udp',          # UDP más rápido
#     'ICF': 0x80, 'DNA': 0x00, 'DA1': 0x00, 'DA2': 0x00,
#     'SNA': 0x00, 'SA1': 0x01, 'SA2': 0x00
# }

with FinsClient(**config) as client:
    data = client.read('DM1700', count=10)
    print(f"DM1700-1709: {data}")