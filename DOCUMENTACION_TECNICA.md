# Documentación Técnica - Sistema de Restaurante

## Arquitectura del Sistema

### Stack Tecnológico
- **Backend**: Flask 2.3.3 con Python 3.11
- **Base de Datos**: SQLite con SQLAlchemy ORM
- **Tiempo Real**: Flask-SocketIO para WebSockets
- **Frontend**: HTML5, CSS3, JavaScript (ES6), Bootstrap 5.1.3
- **Autenticación**: Flask-Login
- **Contenedores**: Docker y Docker Compose
- **Reportes**: ReportLab para generación de PDFs

### Estructura del Proyecto

```
/proyecto-restaurante/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Factory pattern y configuración
│   ├── models.py                # Modelos de base de datos
│   ├── routes/                  # Blueprints organizados por rol
│   │   ├── auth_routes.py       # Autenticación
│   │   ├── admin_routes.py      # Funciones de administrador
│   │   ├── waiter_routes.py     # Funciones de mesero
│   │   └── cook_routes.py       # Funciones de cocinero
│   ├── sockets/                 # Eventos WebSocket
│   ├── services/                # Lógica de negocio
│   ├── static/                  # Archivos estáticos
│   └── templates/               # Plantillas HTML
├── instance/                    # Base de datos SQLite
├── Dockerfile                   # Imagen Docker
├── docker-compose.yml           # Orquestación
└── requirements.txt             # Dependencias Python
```

## Modelos de Base de Datos

### User (Usuarios)
```python
- id: Integer (PK)
- username: String(80) UNIQUE
- password_hash: String(120)
- role: String(20) ['admin', 'waiter', 'cook']
- full_name: String(100)
- created_at: DateTime
- is_active: Boolean
```

### Product (Productos)
```python
- id: Integer (PK)
- name: String(100)
- price: Float (Nulo para productos base)
- category: String(50) ['Principal', 'Bebida', 'Extra']
- stock: Integer (Stock para productos base o simples)
- created_at: DateTime
- is_active: Boolean
- parent_id: Integer (FK a product.id, para variantes)
- stock_consumption: Integer (Unidades de stock que consume una variante)
```

### Order (Órdenes)
```python
- id: Integer (PK)
- customer_name: String(100)
- customer_phone: String(20)
- status: String(20) ['pending', 'sent_to_kitchen', 'in_preparation', 'ready', 'paid', 'cancelled']
- total: Float
- created_at: DateTime
- updated_at: DateTime
- waiter_id: Integer (FK)
- cash_received: Float # Monto en efectivo recibido para el pago
- change_given: Float # Cambio entregado al cliente
```

### OrderItem (Items de Orden)
```python
- id: Integer (PK)
- order_id: Integer (FK)
- product_id: Integer (FK)
- quantity: Integer
- unit_price: Float # Precio del producto principal + suma de precios de extras
- extras: Text # Un string JSON que contiene una lista de objetos 'extra'. Cada objeto tiene 'id', 'name' y 'price'.
- notes: Text
```

### DailyReport (Reportes Diarios)
```python
- id: Integer (PK)
- date: Date UNIQUE
- total_sales: Float
- cash_in_register: Float
- difference: Float
- created_at: DateTime
```

## Seguridad Implementada

### Autenticación y Autorización
- **Hash de contraseñas**: Werkzeug PBKDF2 SHA256
- **Sesiones seguras**: Flask-Login con cookies firmadas
- **Control de acceso**: Decoradores por rol (@admin_required, @waiter_required, @cook_required)
- **Timeout de sesión**: Cierre automático por inactividad

### Sanitización de Datos
- **Bleach**: Limpieza de inputs HTML para prevenir XSS
- **Validación de tipos**: Conversión segura de datos numéricos
- **Escape de plantillas**: Jinja2 auto-escape habilitado
- **Validación de formularios**: Verificación server-side

### Prevención de Inyecciones
- **SQLAlchemy ORM**: Previene inyección SQL automáticamente
- **Parámetros preparados**: Todas las consultas usan parámetros seguros
- **Validación de entrada**: Verificación de tipos y rangos

### Headers de Seguridad
- **Content Security Policy**: Prevención de XSS
- **X-Frame-Options**: Protección contra clickjacking
- **X-Content-Type-Options**: Prevención de MIME sniffing

## API WebSocket

### Eventos del Cliente al Servidor
```javascript
// Conexión automática por rol
socket.on('connect')
socket.on('disconnect')
```

### Eventos del Servidor al Cliente
```javascript
// Nueva orden para cocina
'new_order': {
    order_id: int,
    customer_name: string,
    items: array
}

// Actualización de estado de la orden
'order_status_update': {
    order_id: int,
    status: string,
    customer_name: string
}

// Actualización de stock de un producto
'stock_update': {
    product_id: int,
    stock: int
}

// Notificaciones generales
'notification': {
    message: string,
    type: string
}
```

### Salas (Rooms)
- **kitchen**: Cocineros reciben nuevas órdenes y actualizaciones de estado.
- **waiters**: Meseros reciben actualizaciones de estado de las órdenes.
- **admin**: Administradores reciben todas las notificaciones.

## Flujo de Datos

### Proceso de Orden
1. **Mesero crea orden** → Estado: 'pending' + WebSocket 'stock_update' para todos.
2. **Mesero envía a cocina** → Estado: 'sent_to_kitchen' + WebSocket 'new_order' a cocina.
3. **Cocinero inicia preparación** → Estado: 'in_preparation' + WebSocket 'order_status_update' a cocina y meseros.
4. **Cocinero marca listo** → Estado: 'ready' + WebSocket 'order_status_update' a cocina y meseros.
5. **Mesero procesa pago** → Estado: 'paid'
6. **Mesero cancela orden** → Estado: 'cancelled' + WebSocket 'stock_update' para todos.

### Gestión de Stock
- **Reserva**: El stock se descuenta de la base de datos en el momento de la **creación de la orden** (`create_order`).
- **Lógica de Descuento**:
    - **Productos Simples (Bebidas, Extras)**: Se descuenta la cantidad pedida del `stock` del propio producto.
    - **Variantes de Productos (Principal)**: Se descuenta del `stock` del producto **padre** una cantidad igual a (`stock_consumption` de la variante * cantidad pedida).
- **Liberación**: El stock se restaura si una orden es cancelada (`cancel_order`). La lógica es simétrica a la de la reserva, devolviendo el stock al producto simple o al producto padre correspondiente.
- **Actualización**: El administrador puede ajustar el stock manualmente desde la gestión del menú. Para productos con variantes, solo se debe editar el stock del producto base.

### Cierre de Caja Diario
1.  Al final del día, el administrador va a la sección de "Cierre de Caja".
2.  El sistema muestra el total de ventas del día.
3.  El administrador ingresa el monto de efectivo contado en caja.
4.  El sistema calcula la diferencia (sobrante o faltante).
5.  El administrador guarda el cierre diario.
6.  Se puede generar un reporte en PDF con el resumen del cierre y el detalle de las ventas del día.

## Personalizaciones y Lógica de Plantillas

### Filtros de Jinja Personalizados
Para manejar la presentación de datos de forma consistente en el frontend, se han implementado filtros personalizados en `app/__init__.py`:

- **`datetime_local`**: Convierte fechas y horas almacenadas en UTC a la zona horaria local de Guatemala (America/Guatemala, UTC-6), asegurando que toda la interfaz muestre una hora consistente.
- **`parse_extras`**: Parsea el campo `OrderItem.extras` (que es un string JSON) para extraer y mostrar de forma legible los nombres de los extras seleccionados (ej: "Queso Extra, Salchicha Adicional").

### Visualización Consistente de Nombres de Productos
Se ha implementado una lógica mejorada para la visualización de nombres de productos en varias secciones de la aplicación, asegurando claridad y consistencia, especialmente para productos con variantes. Cuando un producto es una variante de otro (es decir, tiene un `parent_id` asociado), su nombre se muestra en el formato "Nombre del Producto Base (Nombre de la Variante)". Si el producto no es una variante, se muestra solo su nombre.

Esta mejora aplica a:
- **Reportes de Ventas (Administrador):** En la sección de "Producto más vendido" (web y PDF).
- **Cierre Diario (Administrador):** En el detalle de ventas (web y PDF).
- **Procesamiento de Pago (Mesero):** En la lista de ítems de la orden.

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p instance
EXPOSE 5000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "run:app"]
```

### Docker Compose
```yaml
services:
  restaurant-app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
```

## Variables de Entorno

### Requeridas
- `SECRET_KEY`: Clave secreta para sesiones (cambiar en producción)

### Opcionales
- `FLASK_ENV`: Entorno de ejecución (development/production)
- `DATABASE_URL`: URL de base de datos (por defecto SQLite)

## Comandos Docker

### Desarrollo
```bash
# Construir y levantar
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Reiniciar
docker-compose restart
```

### Producción
```bash
# Construir imagen optimizada
docker build -t restaurant-system .

# Ejecutar contenedor
docker run -d -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -e SECRET_KEY=your-production-secret \
  restaurant-system
```

## Monitoreo y Logs

### Logs de Aplicación
- **Flask**: Logs automáticos en stdout
- **SQLAlchemy**: Logs de consultas en desarrollo
- **SocketIO**: Logs de conexiones WebSocket

### Métricas Importantes
- Número de órdenes por día
- Tiempo promedio de preparación
- Productos más vendidos
- Errores de stock

## Backup y Recuperación

### Base de Datos
```bash
# Backup
cp instance/restaurant.db backup/restaurant_$(date +%Y%m%d).db

# Restauración
cp backup/restaurant_YYYYMMDD.db instance/restaurant.db
```

### Datos Críticos
- Base de datos SQLite
- Logs de aplicación
- Reportes PDF generados

## Escalabilidad

### Limitaciones Actuales
- SQLite: Máximo ~1000 transacciones concurrentes
- Sesiones en memoria: No persisten entre reinicios
- Archivos estáticos: Servidos por Flask (no optimizado)

### Mejoras Futuras
- PostgreSQL para mayor concurrencia
- Redis para sesiones y cache
- Nginx para archivos estáticos
- Load balancer para múltiples instancias

## Troubleshooting

### Problemas Comunes

**Error de conexión WebSocket**
```bash
# Verificar puerto 5000 disponible
netstat -tulpn | grep :5000
```

**Base de datos bloqueada**
```bash
# Reiniciar aplicación
docker-compose restart
```

**Permisos de archivos**
```bash
# Ajustar permisos de instance/
chmod 755 instance/
chmod 644 instance/restaurant.db
```

### Dashboard
*   **El indicador de "Stock Bajo" no muestra los productos esperados**: El umbral para "Stock Bajo" está configurado por defecto en 5 unidades. Esto se puede cambiar en la ruta `dashboard` dentro de `app/routes/admin_routes.py`.

### Logs de Debug
```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)

```

## Frontend Workarounds

### Errores de Extensión del Navegador

En algunos casos, las extensiones del navegador de los usuarios (como traductores automáticos o herramientas para guardar páginas) pueden intentar acceder a elementos del DOM que no existen en la aplicación, como `translate-page` o `save-page`. Esto puede generar errores en la consola del navegador que no se originan en el código de la aplicación.

Se han intentado los siguientes workarounds en `app/templates/layouts/base.html` para mitigar estos errores:
1.  Añadir elementos `div` ocultos con los IDs `translate-page` y `save-page`.
2.  Añadir un script que crea dinámicamente estos elementos cuando el DOM está cargado.

A pesar de estos intentos, los errores pueden persistir en la consola del navegador. Sin embargo, no parecen afectar la funcionalidad principal de la aplicación y, por el momento, se consideran un problema menor de carácter externo.