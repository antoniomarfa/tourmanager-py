# Validación de Upload de Archivos en Company Routes

## Resumen de Cambios

Se implementó la validación de archivos en el endpoint `/company/update` para garantizar que los archivos subidos cumplan con los requisitos de tipo y tamaño.

## Archivos Modificados

### 1. `templates/company/edit.html`
- ✅ Agregado `enctype="multipart/form-data"` al formulario (línea 36)
- Esto es **esencial** para que el navegador envíe los archivos correctamente

### 2. `routes/company_routes.py`
Se agregaron validaciones completas para los 3 archivos:

#### **Contrato Gira de Estudio (`contratoge`)**
- ✅ Valida que la extensión sea `.docx`
- ✅ Valida que el tamaño no exceda 2MB
- ✅ Cambia el nombre a: `Contratoge_{code_company}.docx`
- ✅ Guarda en: `uploads/company/contrato/{company_id}/`

#### **Contrato Viajes Grupales (`contratovg`)**
- ✅ Valida que la extensión sea `.docx`
- ✅ Valida que el tamaño no exceda 2MB
- ✅ Cambia el nombre a: `Contratovg_{code_company}.docx`
- ✅ Guarda en: `uploads/company/contrato/{company_id}/`

#### **Logo (`archive_image`)**
- ✅ Valida que la extensión sea `.png`
- ✅ Valida que el tamaño no exceda 2MB
- ✅ Cambia el nombre a: `login_logo_{code_company}.png`
- ✅ Guarda en: `uploads/company/logo/`

## Validaciones Implementadas

### 1. **Validación de Extensión**
```python
ext = os.path.splitext(archivo.filename)[1].lower()
if ext != ".docx":  # o ".png" para el logo
    Helper.flash_message(request, "error", "Tipo de archivo no permitido")
    return RedirectResponse(...)
```

### 2. **Validación de Tamaño**
```python
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
contents = await archivo.read()
if len(contents) > MAX_FILE_SIZE:
    Helper.flash_message(request, "error", "Archivo excede 2MB")
    return RedirectResponse(...)
```

### 3. **Cambio de Nombre (sin cambiar extensión)**
```python
nuevo_nombre = f"Contratoge_{request.session.get('code_company')}{ext}"
```
- Mantiene la extensión original
- Usa el código de la compañía para identificación única

## Mensajes de Error

Si hay algún problema, el usuario verá mensajes claros:
- "El archivo de Contrato GE debe ser .docx"
- "El archivo de Contrato VG debe ser .docx"
- "El logo debe ser un archivo .png"
- "El archivo excede el tamaño máximo de 2MB"

## Estructura de Carpetas

```
uploads/
└── company/
    ├── contrato/
    │   └── {company_id}/
    │       ├── Contratoge_{code_company}.docx
    │       └── Contratovg_{code_company}.docx
    └── logo/
        └── login_logo_{code_company}.png
```

## Notas Importantes

1. **Los archivos son opcionales**: Si el usuario no selecciona un archivo, no se valida nada
2. **Validación solo por extensión**: Actualmente valida solo la extensión del archivo. Para mayor seguridad, se podría agregar validación de "magic numbers" usando la librería `python-magic`
3. **Sobrescritura**: Si se sube un archivo con el mismo nombre, se sobrescribe el anterior
4. **Tamaño máximo**: 2MB para todos los archivos

## Pruebas Recomendadas

1. ✅ Subir archivo DOCX válido < 2MB
2. ✅ Subir archivo PNG válido < 2MB
3. ❌ Intentar subir archivo con extensión incorrecta (.pdf, .jpg, etc.)
4. ❌ Intentar subir archivo > 2MB
5. ✅ Enviar formulario sin seleccionar archivos (debe funcionar)
