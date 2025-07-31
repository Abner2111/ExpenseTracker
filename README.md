# 📊 Rastreador de Gastos Automático - BAC Credomatic

Un sistema automatizado para extraer datos de gastos de los correos de notificación de transacciones de BAC Credomatic, categorizarlos automáticamente y agregarlos a una hoja de cálculo de Google.

## 🌟 Características

- ✅ **Extracción automática** de correos de notificación de BAC Credomatic
- 🏪 **Detección inteligente de comercios** con base de datos de vendedores costarricenses
- 📋 **Categorización automática** usando 15 categorías personalizadas
- 💰 **Análisis de montos** compatible con formato de colones costarricenses (CRC)
- 📅 **Filtrado por mes** para procesar transacciones específicas
- 🔄 **Sincronización con Google Sheets** en tiempo real
- 🛡️ **Manejo de errores robusto** con reintentos automáticos

## 🎯 Categorías Soportadas

El sistema categoriza automáticamente las transacciones en:

- **Groceries** - Supermercados (Auto Mercado, Pali, PriceSmart, etc.)
- **Dining Out** - Restaurantes y entrega de comida (KFC, Uber Eats, etc.)
- **Transportation** - Transporte y parqueo (Uber, parquímetros)
- **Health/medical** - Salud y medicina (farmacias, clínicas)
- **Home** - Hogar y mejoras (ferreterías, Cemaco)
- **Personal** - Cuidado personal y café (salones, Café Britt)
- **Utilities** - Servicios públicos (ICE, Kolbi, AyA)
- **Car maintenance** - Mantenimiento de vehículos (gasolineras, talleres)
- **Pets** - Mascotas (veterinarias, tiendas de mascotas)
- **Travel** - Viajes (hoteles, tours)
- **Debt** - Deudas (bancos, servicios financieros)
- **Streaming** - Entretenimiento (Netflix, Spotify)
- **Education** - Educación (universidades, librerías)
- **Gifts** - Regalos (florerías, joyerías)
- **General** - Categoría por defecto

## 🏪 Comercios Reconocidos

### Supermercados y Tiendas
- Auto Mercado, Mas x Menos, Maxi Pali, Pali
- PriceSmart, Walmart, Pequeño Mundo
- Mega Super, Super Compro, Perimercados

### Comida Rápida y Restaurantes
- KFC, McDonald's, Burger King, Pizza Hut
- Subway, Uber Eats, Rappi, Glovo
- Comidas El Shaddai, Coral IBM, Pronto Snack

### Servicios y Utilidades
- ICE, Kolbi, Claro, Movistar
- AyA, CNFL, Jasec
- Bancos: BAC, BCR, Banco Nacional, Scotiabank

### Y muchos más...

## 📋 Requisitos Previos

- Python 3.7 o superior
- Cuenta de Gmail con acceso a las APIs de Google
- Hoja de cálculo de Google configurada
- Correos de BAC Credomatic en la bandeja de entrada

## � Plantilla de Hoja de Cálculo

Para facilitar la configuración, puedes usar esta plantilla pre-configurada:

🔗 **[Plantilla de Google Sheets](https://docs.google.com/spreadsheets/d/13P4kQm1xVlvnLSrm4Pv-mfW6t3KZyMYmIachqVDQtYU/edit?usp=sharing)**

La plantilla incluye:
- ✅ Columnas configuradas correctamente (B: Date, C: Amount, D: Description, E: Category)
- ✅ Formato de presupuesto mensual
- ✅ Secciones separadas para Gastos e Ingresos
- ✅ Listo para usar con el sistema automático

**Instrucciones:**
1. Hacer clic en "Archivo" → "Hacer una copia"
2. Renombrar la copia con tu mes/año (ej: "Agosto 2025 - Presupuesto")
3. Copiar el ID de la URL de tu copia
4. Usar ese ID en la configuración del proyecto

## �🚀 Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Abner2111/ExpenseTracker.git
cd ExpenseTracker
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar credenciales de Google:**
   - Ir a [Google Cloud Console](https://console.cloud.google.com/)
   - Crear un nuevo proyecto o seleccionar uno existente
   - Habilitar Gmail API y Google Sheets API
   - Descargar `credentials.json` y colocarlo en la carpeta `src/`

4. **Configurar la hoja de cálculo:**
   - **Usar plantilla:** Hacer una copia de [esta plantilla de Google Sheets](https://docs.google.com/spreadsheets/d/13P4kQm1xVlvnLSrm4Pv-mfW6t3KZyMYmIachqVDQtYU/edit?usp=sharing)
   - **O crear manualmente:** Crear una hoja de Google Sheets nueva
   - Asegurarse de que tenga las columnas: Date, Amount, Description, Category en las columnas B, C, D, E
   - Copiar el ID de la hoja de cálculo de la URL

## ⚙️ Configuración

Editar el archivo `src/config.py`:

```python
# ID de la hoja de cálculo de Google (obtenido de la URL)
SPREADSHEET_ID = "tu_id_de_hoja_aqui"

# Nombre de la hoja donde se agregarán los gastos
SPREADSHEET_NAME = "Transactions"

# Filtro por mes (opcional)
FILTER_BY_MONTH = "2025/08"  # Para agosto 2025, o None para todos los meses
```

### Opciones de Filtrado por Mes

- `"2025/08"` - Procesar solo transacciones de agosto 2025
- `"2025/07"` - Procesar solo transacciones de julio 2025
- `None` - Procesar todos los correos no leídos

## 🏃‍♂️ Uso

Ejecutar el script principal:

```bash
cd src
python main.py
```

El sistema:
1. 🔐 Se autentica con las APIs de Google
2. 📧 Busca correos no leídos de BAC Credomatic
3. 🔍 Extrae información de transacciones (fecha, monto, comercio)
4. 🏷️ Categoriza automáticamente cada transacción
5. 📊 Agrega los datos a la hoja de cálculo
6. ✅ Marca los correos como leídos

## 📁 Estructura del Proyecto

```
ExpenseTracker/
├── src/
│   ├── main.py           # Script principal
│   ├── config.py         # Configuración
│   ├── credentials.json  # Credenciales de Google (no incluido)
│   └── token.pickle      # Token de acceso (generado automáticamente)
├── requirements.txt      # Dependencias de Python
├── .gitignore           # Archivos excluidos del control de versiones
└── README.md            # Este archivo
```

## 🔧 Personalización

### Agregar Nuevos Comercios

Para agregar reconocimiento de nuevos comercios, editar la sección `vendor_keywords` en `main.py`:

```python
vendor_keywords = {
    'nuevo_comercio': 'Nuevo Comercio CR',
    # ... otros comercios
}
```

### Modificar Categorías

Para cambiar la lógica de categorización, editar la sección de inferencia de categorías en `main.py`.

## 🛠️ Solución de Problemas

### Error de Autenticación
- Verificar que `credentials.json` esté en la carpeta `src/`
- Eliminar `token.pickle` y volver a autenticarse

### No se Encuentran Correos
- Verificar que los correos de BAC estén marcados como "no leídos"
- Comprobar el filtro de mes en `config.py`

### Errores de Google Sheets
- Verificar que la hoja de cálculo sea accesible
- Comprobar que el ID de la hoja de cálculo sea correcto
- Verificar permisos de la cuenta de servicio

## 🔒 Seguridad

- ⚠️ **Nunca** subir `credentials.json` o `token.pickle` al control de versiones
- Los archivos sensibles están incluidos en `.gitignore`
- Usar cuentas de servicio para acceso programático a Google Sheets

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Hacer fork del repositorio
2. Crear una rama para la nueva característica
3. Hacer commit de los cambios
4. Enviar un pull request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## 🙏 Reconocimientos

- APIs de Google para Gmail y Sheets
- Comunidad de desarrolladores de Python
- BAC Credomatic por el formato consistente de correos

## 📞 Soporte

Para preguntas o problemas:
- Abrir un issue en GitHub
- Revisar la documentación de las APIs de Google
- Consultar los logs de debug para troubleshooting

---

**¡Automatiza tu seguimiento de gastos y mantén tu presupuesto bajo control! 💰📊**
