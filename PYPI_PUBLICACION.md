# Publicación en PyPI - PyOmron FINS

Esta guía explica cómo publicar PyOmron FINS en PyPI para que se pueda instalar con `pip install pyomron-fins`.

---

## Requisitos Previos

### 1. Cuentas Necesarias
- **Cuenta en PyPI**: https://pypi.org/account/register/
- **Cuenta en TestPyPI** (opcional pero recomendado): https://test.pypi.org/account/register/

### 2. Herramientas de Desarrollo
```bash
# Instalar herramientas de empaquetado
pip install --upgrade build twine

# Verificar instalación
build --version
twine --version
```

---

## Paso 1: Preparar el Paquete

### Verificar Configuración
```bash
# Verificar que pyproject.toml existe y es válido
cat pyproject.toml

# Verificar que setup.py existe
cat setup.py

# Verificar estructura del paquete
find . -name "*.py" | head -10
```

### Construir el Paquete
```bash
# Limpiar builds anteriores
rm -rf dist/ build/ *.egg-info/

# Construir el paquete
python -m build

# Verificar que se crearon los archivos
ls -la dist/
```

---

## Paso 2: Probar en TestPyPI (Recomendado)

### Subir a TestPyPI
```bash
# Subir a TestPyPI para probar
twine upload --repository testpypi dist/*

# Verificar que se subió correctamente
# Visita: https://test.pypi.org/project/pyomron-fins/
```

### Probar Instalación desde TestPyPI
```bash
# Crear entorno virtual de prueba
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# o en Windows: test_env\Scripts\activate

# Instalar desde TestPyPI
pip install --index-url https://test.pypi.org/simple/ pyomron-fins

# Probar que funciona
python -c "from pyomron_fins import FinsClient; print('Instalación exitosa!')"

# Salir del entorno virtual
deactivate
rm -rf test_env
```

---

## Paso 3: Publicar en PyPI

### Subir a PyPI Oficial
```bash
# Subir a PyPI oficial
twine upload dist/*

# Verificar que se publicó
# Visita: https://pypi.org/project/pyomron-fins/
```

### Verificar Instalación
```bash
# Probar instalación desde PyPI oficial
pip install pyomron-fins

# Verificar que funciona
python -c "from pyomron_fins import FinsClient; print('Instalación desde PyPI exitosa!')"
```

---

## Configuración de Credenciales

### Archivo .pypirc (Opcional pero recomendado)
Crear archivo `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...
```

### Obtener Tokens de API
1. **PyPI**: https://pypi.org/manage/account/token/
2. **TestPyPI**: https://test.pypi.org/manage/account/token/

---

## Actualizar Versión

### Para nuevas versiones:
```bash
# Cambiar versión en pyproject.toml
# version = "1.0.1"

# Cambiar versión en setup.py (si existe)
# version="1.0.1",

# Reconstruir y subir
python -m build
twine upload dist/*
```

---

## Solución de Problemas

### Error: "Package already exists"
```bash
# Si el nombre ya existe, cambiar el nombre en pyproject.toml
name = "pyomron-fins-omron"  # o similar
```

### Error: "Invalid version"
```bash
# Usar versiones válidas: 1.0.0, 1.0.1, 2.0.0, etc.
# NO usar: 1.0, 1.0-dev, etc.
```

### Error: "No module named 'build'"
```bash
pip install --upgrade build twine
```

### Error de Autenticación
```bash
# Usar token de API en lugar de contraseña
# Username: __token__
# Password: pypi-AgEIcHlwaS5vcmcC...
```

---

## Verificación Final

### Checklist de Publicación:
- [ ] `pyproject.toml` configurado correctamente
- [ ] Nombre del paquete único en PyPI
- [ ] Versión correcta
- [ ] Descripción y metadata completas
- [ ] Probado en TestPyPI
- [ ] Subido a PyPI oficial
- [ ] Instalación verificada
- [ ] Documentación actualizada

### Comandos de Verificación:
```bash
# Verificar instalación
pip install pyomron-fins
python -c "import pyomron_fins; print('OK')"

# Verificar versión
python -c "import pyomron_fins; print(pyomron_fins.__version__)"
```

---

## Documentación Actualizada

Después de publicar, actualizar la documentación:

```markdown
## Instalación

### Opción 1: Desde PyPI (Recomendado)
```bash
pip install pyomron-fins
```

### Opción 2: Desde GitHub
```bash
git clone https://github.com/dvasquez01/PyOmron-FINS-Complete.git
cd PyOmron-FINS-Complete
pip install -e .
```
```

---

## ¡Listo para Distribución!

Una vez publicado en PyPI, cualquier usuario podrá instalar PyOmron FINS con:

```bash
pip install pyomron-fins
```

¡La librería ahora es accesible globalmente!