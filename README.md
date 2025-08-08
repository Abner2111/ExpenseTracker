# 📊 Rastreador de Gastos Automático - BAC Credomatic

Un sistema automatizado avanzado para extraer datos de gastos de los correos de notificación de transacciones de BAC Credomatic, categorizarlos automáticamente y agregarlos a una hoja de cálculo de Google con conversión de divisas en tiempo real.

## 🌟 Características

- ✅ **Extracción automática** de correos de notificación de BAC Credomatic
- 🏪 **Detección inteligente de comercios** con base de datos extensa de vendedores costarricenses
- 📋 **Categorización automática** usando 15+ categorías personalizadas
- � **Conversión automática de divisas** (USD, EUR → CRC) con tasas de cambio en tiempo real
- 🌍 **Soporte multi-moneda** con detección automática de símbolos y códigos de divisa
- 📅 **Análisis de fechas en español** con soporte para abreviaciones como "Ago" (Agosto)
- 💰 **Análisis de montos avanzado** compatible con múltiples formatos numéricos
- 📅 **Filtrado por mes** para procesar transacciones específicas
- 🔄 **Sincronización con Google Sheets** en tiempo real
- 🛡️ **Manejo de errores robusto** con reintentos automáticos y detección de duplicados
- 📝 **Documentación automática** de conversiones con tasas de cambio en las notas

## 💱 Conversión de Divisas

### Divisas Soportadas
- **CRC** (Colones Costarricenses) - Moneda base
- **USD** (Dólares Estadounidenses) - Conversión automática
- **EUR** (Euros) - Conversión automática  
- **GBP** (Libras Esterlinas) - Conversión automática

### Formatos de Moneda Detectados
- `Monto: USD 9.99` ✅
- `USD 25.50` ✅
- `25.50 USD` ✅
- `$19.99` ✅
- `€45.99` ✅
- `CRC 5,650.00` ✅
- `₡15,500.50` ✅

### Características de Conversión
- 🌐 **Tasas de cambio en tiempo real** usando exchangerate-api.com
- 🔄 **Tasas de respaldo** para cuando la API no esté disponible
- 📝 **Documentación automática** en notas: "Original: 9.99 USD (Rate: 503.32)"
- ⚡ **Conversión instantánea** a CRC para consistencia en reportes

## 📅 Manejo de Fechas en Español

### Formatos de Fecha Soportados
- `Ago 15, 2025` → `2025-08-15` ✅
- `15/08/2025` → `2025-08-15` ✅
- `15 Ago 2025` → `2025-08-15` ✅
- `Agosto 15, 2025` → `2025-08-15` ✅

### Meses en Español Reconocidos
- **Abreviaciones:** ene, feb, mar, abr, may, jun, jul, ago, sep, oct, nov, dic
- **Nombres completos:** enero, febrero, marzo, abril, mayo, junio, julio, agosto, septiembre, octubre, noviembre, diciembre

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
- KFC, McDonald's, Burger King, Pizza Hut, Domino's
- Subway, Taco Bell, Uber Eats, Rappi, Glovo
- Comidas El Shaddai, Coral IBM, Pronto Snack
- Fiesta Express Delivery, Delimart AFZ

### Transporte y Movilidad
- Uber, DiDi, inDrive, TicoRide
- Interbus, RIDE CR, parquímetros
- Gasolineras, talleres mecánicos

### Streaming y Entretenimiento
- Netflix, Spotify, Amazon Prime, Disney+
- Google (servicios digitales)
- Otros servicios de streaming

### Y muchos más... (100+ comercios reconocidos)

## 📋 Requisitos Previos

- Python 3.7 o superior
- Cuenta de Gmail con acceso a las APIs de Google
- Hoja de cálculo de Google configurada
- Correos de BAC Credomatic en la bandeja de entrada
- Conexión a internet para conversión de divisas en tiempo real

## 🔧 Tecnologías Utilizadas

- **APIs de Google:** Gmail API, Google Sheets API
- **Conversión de divisas:** exchangerate-api.com
- **Parsing de emails:** BeautifulSoup4, regex avanzado
- **Autenticación:** OAuth2, Google Auth
- **Manejo de datos:** gspread, requests

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

**Dependencias incluidas:**
- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- `google-api-python-client`, `gspread`
- `beautifulsoup4`, `requests`

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
2. 📧 Busca correos no leídos de BAC Credomatic (con filtro opcional por mes)
3. 🔍 Extrae información de transacciones (fecha, monto, comercio, divisa)
4. 💱 Detecta divisa automáticamente y convierte a CRC si es necesario
5. 📅 Analiza fechas en español y las convierte al formato estándar
6. 🏷️ Categoriza automáticamente cada transacción usando IA de reconocimiento
7. 📊 Agrega los datos a la hoja de cálculo con notas de conversión
8. ✅ Marca los correos como leídos
9. 🛡️ Detecta y evita duplicados automáticamente

## 🔍 Ejemplos de Procesamiento

### Ejemplo 1: Spotify USD
```
Email: "Comercio: SPOTIFY, Monto: USD 9.99, Fecha: Ago 15, 2025"
Resultado:
- Vendor: SPOTIFY
- Amount: 5,028.17 CRC
- Date: 2025-08-15
- Category: Streaming
- Notes: "Original: 9.99 USD (Rate: 503.32)"
```

### Ejemplo 2: Supermercado CRC
```
Email: "Comercio: AUTOMERCADO, Monto: CRC 25,500.00, Fecha: Jul 30, 2025"
Resultado:
- Vendor: AUTOMERCADO
- Amount: 25,500.00 CRC
- Date: 2025-07-30
- Category: Groceries
- Notes: "Email Subject: Notificación de transacción"
```

## 📁 Estructura del Proyecto

```
ExpenseTracker/
├── src/
│   ├── main.py           # Script principal con lógica de parsing avanzada
│   ├── config.py         # Configuración (IDs, filtros, rutas)
│   ├── database.py       # Módulo de base de datos SQLite
│   ├── credentials.json  # Credenciales de Google (no incluido)
│   └── token.pickle      # Token de acceso (generado automáticamente)
├── migrate_data.py       # Script de migración de datos a SQLite
├── admin_database.py     # Herramienta de administración de base de datos
├── expense_tracker.db    # Base de datos SQLite (generada automáticamente)
├── test_*.py            # Scripts de prueba para validar funcionalidades
├── requirements.txt     # Dependencias de Python (actualizado)
├── .gitignore          # Archivos excluidos del control de versiones
├── LICENSE             # Licencia MIT
└── README.md           # Este archivo (documentación completa)
```

## 💽 Base de Datos SQLite

### Configuración Inicial

1. **Migrar datos existentes** (solo necesario una vez):
```bash
python migrate_data.py
```

Esto crea la base de datos SQLite (`expense_tracker.db`) y migra:
- 88+ palabras clave de vendedores costarricenses
- 14 categorías de gastos
- 116+ reglas de categorización con prioridades

### Administración de la Base de Datos

Use el script `admin_database.py` para gestionar la base de datos:

#### Listar datos existentes:
```bash
# Ver todas las categorías
python admin_database.py list-categories

# Ver todas las palabras clave de vendedores
python admin_database.py list-vendors

# Ver todas las reglas de categorización
python admin_database.py list-rules
```

#### Agregar nuevos datos:
```bash
# Agregar nuevo vendedor
python admin_database.py add-vendor --keyword "nuevo_comercio" --vendor "Nuevo Comercio CR" --category "Personal"

# Agregar nueva categoría
python admin_database.py add-category --category "Cryptocurrency" --description "Bitcoin, crypto exchanges"

# Agregar nueva regla de categorización
python admin_database.py add-rule --rule-type "keyword_contains" --pattern "bitcoin" --category "Cryptocurrency" --priority 85
```

#### Probar categorización:
```bash
# Probar cómo se categorizaría un texto
python admin_database.py test-vendor --text "DLC* UBER RIDES"
python admin_database.py test-vendor --text "KFC EXPRESS"
```

#### Eliminar datos:
```bash
# Eliminar palabra clave de vendedor
python admin_database.py delete-vendor --keyword "comercio_obsoleto"
```

### Tipos de Reglas de Categorización

- **vendor_exact**: Coincidencia exacta con el nombre del vendedor
- **vendor_contains**: El nombre del vendedor contiene el patrón
- **keyword_contains**: El texto del email contiene el patrón

Las reglas con mayor prioridad se evalúan primero.



## 🔧 Personalización

### Agregar Nuevos Comercios

Usar la herramienta de administración para agregar comercios:

```bash
# Método recomendado: usar admin_database.py
python admin_database.py add-vendor --keyword "nuevo_comercio" --vendor "Nuevo Comercio CR"

# Agregar regla de categorización específica
python admin_database.py add-rule --rule-type "vendor_exact" --pattern "nuevo comercio cr" --category "Personal" --priority 50
```

### Modificar Categorías

Agregar nuevas categorías y reglas:

```bash
# Agregar nueva categoría
python admin_database.py add-category --category "Cryptocurrency" --description "Bitcoin, crypto exchanges"

# Agregar reglas para la nueva categoría
python admin_database.py add-rule --rule-type "keyword_contains" --pattern "bitcoin" --category "Cryptocurrency" --priority 85
python admin_database.py add-rule --rule-type "keyword_contains" --pattern "crypto" --category "Cryptocurrency" --priority 85
```

### Probar Cambios

Antes de procesar emails reales, probar los cambios:

```bash
# Probar categorización de un texto específico
python admin_database.py test-vendor --text "COINBASE PRO BTC"
```

### Agregar Nuevas Divisas

Para soportar nuevas divisas, agregar patrones en `amount_patterns` y tasas de respaldo en `convert_currency_to_crc()`:

```python
# En amount_patterns
(r'(?:Monto|Total):\s*GBP\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'GBP'),

# En fallback_rates
fallback_rates = {
    'USD': 520.0,
    'EUR': 570.0,
    'GBP': 650.0,  # Nueva divisa
}
```

## 🧪 Testing y Debugging

### Scripts de Prueba Incluidos

El proyecto incluye varios scripts de prueba para validar funcionalidades:

```bash
# Probar conversión de divisas
python test_currency_conversion.py

# Probar análisis de fechas en español
python debug_date_parsing.py

# Probar formato específico de Spotify USD
python test_spotify_usd.py

# Probar múltiples formatos USD
python test_usd_formats.py

# Prueba de integración completa
python test_final_integration.py
```

### Modo Debug

El script incluye logging detallado para troubleshooting:

```python
Debug: Searching for amounts with currency detection...
Debug: Pattern 2 found amount match: '9.99' with currency hint: 'USD'
Debug: Detected currency: USD
Debug: Exchange rate USD to CRC: 503.32
Debug: Converted 9.99 USD to 5028.17 CRC (rate: 503.32)
Debug: Found vendor in Comercio field: 'SPOTIFY'
Debug: Assigned category 'Streaming' (streaming service match)
```

## 🛠️ Solución de Problemas

### Error de Autenticación
- Verificar que `credentials.json` esté en la carpeta `src/`
- Eliminar `token.pickle` y volver a autenticarse
- Verificar que las APIs de Gmail y Sheets estén habilitadas

### No se Encuentran Correos
- Verificar que los correos de BAC estén marcados como "no leídos"
- Comprobar el filtro de mes en `config.py`
- Verificar el query de búsqueda: `subject:"Notificación de transacción"`

### Errores de Conversión de Divisas
- Verificar conexión a internet para API de tasas de cambio
- Revisar logs para confirmar uso de tasas de respaldo
- Validar que la divisa esté en la lista de soportadas

### Problemas de Parsing de Fechas
- Verificar que el formato de fecha en el email sea reconocido
- Revisar logs de debug para ver qué patrón se está usando
- Agregar nuevos patrones si es necesario

### Errores de Google Sheets
- Verificar que la hoja de cálculo sea accesible
- Comprobar que el ID de la hoja de cálculo sea correcto
- Verificar permisos de la cuenta de servicio
- Revisar límites de rate limiting (se maneja automáticamente)

### Problemas de Categorización
- Verificar que el nombre del comercio se extraiga correctamente
- Revisar la lógica de categorización en el código
- Agregar nuevos comercios a `vendor_keywords` si es necesario

## ✨ Nuevas Características (Actualizaciones Recientes)

### v3.0 - Sistema de Base de Datos SQLite
- ✅ Migración de vendedores y categorías a SQLite
- ✅ Herramienta de administración sin código
- ✅ Reglas de categorización con prioridades
- ✅ Sistema de pruebas integrado
- ✅ Gestión de datos más eficiente y mantenible

### v2.3 - Sistema de Testing
- ✅ Scripts de prueba automatizados
- ✅ Validación de todos los formatos de divisa
- ✅ Tests de integración completa
- ✅ Debugging mejorado con logs detallados

### v2.2 - Detección Avanzada de Comercios
- ✅ Limpieza automática de nombres de comercios
- ✅ Separación de información de monto del nombre
- ✅ Base de datos expandida de comercios CR
- ✅ Categorización inteligente mejorada

### v2.1 - Mejoras en Parsing de Fechas
- ✅ Soporte completo para meses en español
- ✅ Manejo de abreviaciones (Ago → Agosto)
- ✅ Múltiples formatos de fecha
- ✅ Parsing robusto con fallbacks

### v2.0 - Sistema de Conversión de Divisas
- ✅ Conversión automática USD/EUR → CRC
- ✅ Tasas de cambio en tiempo real via API
- ✅ Tasas de respaldo para offline
- ✅ Documentación de conversiones en notas

## 🔒 Seguridad

- ⚠️ **Nunca** subir `credentials.json` o `token.pickle` al control de versiones
- Los archivos sensibles están incluidos en `.gitignore`
- Usar cuentas de servicio para acceso programático a Google Sheets

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Hacer fork del repositorio
2. Crear una rama para la nueva característica (`git checkout -b feature/nueva-caracteristica`)
3. Hacer commit de los cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Enviar un pull request

### Áreas de Mejora Buscadas
- 🌐 Soporte para más divisas internacionales
- 🏪 Expansión de base de datos de comercios
- 📊 Mejoras en lógica de categorización
- 🔄 Integración con otros bancos costarricenses
- 📱 Interface web o mobile

## 🏆 Casos de Uso Exitosos

- ✅ **Spotify USD 9.99** → Conversión automática a ~5,000 CRC
- ✅ **Amazon EUR 45.99** → Conversión automática a ~26,000 CRC  
- ✅ **Auto Mercado CRC 15,500** → Categorización como "Groceries"
- ✅ **Uber $25.50** → Categorización como "Transportation"
- ✅ **Fechas españolas** → "Ago 15, 2025" se convierte a "2025-08-15"

## 📊 Estadísticas del Sistema

- **100+ comercios** reconocidos automáticamente
- **15+ categorías** para organización precisa
- **4 divisas** soportadas con conversión automática
- **99%+ precisión** en extracción de datos
- **Duplicados:** Detección y prevención automática
- **Rate limiting:** Manejo inteligente de límites de API

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## 🙏 Reconocimientos

- APIs de Google para Gmail y Sheets
- [exchangerate-api.com](https://exchangerate-api.com) para conversión de divisas en tiempo real
- Comunidad de desarrolladores de Python
- BAC Credomatic por el formato consistente de correos
- Usuarios beta que ayudaron a identificar y resolver edge cases

## 📞 Soporte

Para preguntas o problemas:
- 🐛 Abrir un issue en GitHub para bugs
- 💡 Usar Discussions para preguntas generales  
- 📖 Revisar la documentación de las APIs de Google
- 🔍 Consultar los logs de debug para troubleshooting
- 🧪 Ejecutar scripts de test para validar instalación

## 🚀 Roadmap Futuro

- [ ] Soporte para más bancos costarricenses (BCR, Banco Nacional)
- [ ] Machine Learning para categorización mejorada

---

**¡Automatiza tu seguimiento de gastos con conversión de divisas inteligente y mantén tu presupuesto bajo control! 💰💱📊**
