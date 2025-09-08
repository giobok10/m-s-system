# Documentación Técnica - Sistema de Restaurante

## Arquitectura del Sistema

### Stack Tecnológico
- **Backend**: Flask 2.3.3 con Python 3.11
- **Base de Datos**: PostgreSQL con SQLAlchemy ORM
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
│   ├── sockets/                 # Eventos WebSocket
│   ├── services/                # Lógica de negocio
│   ├── static/                  # Archivos estáticos
│   └── templates/               # Plantillas HTML
├── instance/                    # Directorio de instancia de Flask (si es necesario)
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
- category: String(50) ['Principal', 'Bebida', 'Extra', 'Combo']
- stock: Integer (Stock para productos base o simples)
- created_at: DateTime
- is_active: Boolean
- parent_id: Integer (FK a product.id, para variantes)
- stock_consumption: Integer (Unidades de stock que consume una variante)
# Relación a ComboItem para productos de categoría 'Combo'
- components: relationship('ComboItem') 
```

### ComboItem (Componentes de Combo)
```python
- id: Integer (PK)
- combo_product_id: Integer (FK a product.id)
- component_product_id: Integer (FK a product.id)
- quantity: Integer (Cantidad del componente en el combo)
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
- cash_received: Float
- change_given: Float
```

### OrderItem (Items de Orden)
```python
- id: Integer (PK)
- order_id: Integer (FK)
- product_id: Integer (FK)
- quantity: Integer
- unit_price: Float
- extras: Text # String JSON con lista de extras
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

- **Hash de contraseñas**: Werkzeug PBKDF2 SHA256
- **Control de acceso**: Decoradores por rol
- **Sanitización de Datos**: Bleach para prevenir XSS
- **Prevención de Inyecciones**: SQLAlchemy ORM

## API WebSocket

- **`new_order`**: Notifica a la cocina de una nueva orden.
- **`order_status_update`**: Notifica a meseros y cocineros de cambios de estado de una orden (ej. 'en preparación', 'listo').
- **`stock_update`**: Notifica a todos de cambios en el stock.

## Rutas Principales (Endpoints)

Además de las rutas obvias para servir las páginas, existen las siguientes rutas clave que manejan la lógica de negocio:

- **`POST /admin/variant/add/<int:product_id>`**: Añade una nueva variante a un producto base.
- **`POST /admin/variant/edit/<int:variant_id>`**: Actualiza los datos de una variante existente.
- **`POST /admin/variant/delete/<int:variant_id>`**: Elimina una variante de producto.

## Flujo de Datos

### Proceso de Orden
1. **Mesero crea orden** → Estado: 'pending' + WebSocket 'stock_update' para todos.
2. **Mesero envía a cocina** → Estado: 'sent_to_kitchen' + WebSocket 'new_order' a cocina.
3. **Cocinero inicia preparación** → Estado: 'in_preparation' + WebSocket 'order_status_update'.
4. **Cocinero marca listo** → Estado: 'ready' + WebSocket 'order_status_update'.
5. **Mesero procesa pago** → Estado: 'paid'
6. **Mesero cancela orden** → Estado: 'cancelled' + WebSocket 'stock_update' para todos.

### Gestión de Stock
- **Reserva**: El stock se descuenta de la base de datos en el momento de la **creación de la orden** (`create_order`).
- **Lógica de Descuento**:
    - **Productos Simples (Bebida, Extra)**: Se descuenta la cantidad pedida del `stock` del propio producto.
    - **Variantes de Productos (Principal)**: Se descuenta del `stock` del producto **padre** una cantidad igual a (`stock_consumption` de la variante * cantidad pedida).
    - **Combos**: Se itera sobre los componentes definidos en la tabla `ComboItem`. Para cada componente, se descuenta el stock de su producto base correspondiente, multiplicado por la cantidad definida en el combo y la cantidad pedida del combo.
- **Liberación**: El stock se restaura si una orden es cancelada (`cancel_order`). La lógica es simétrica a la de la reserva.

### Cierre de Caja Diario
- El administrador registra el efectivo en caja al final del día y el sistema calcula las ventas y la diferencia, generando un reporte en PDF si se solicita.

## Guía de Despliegue y Seguridad en Producción

Para producción, es **obligatorio** usar una base de datos externa (como PostgreSQL en Supabase o Neon) y configurar las credenciales a través de variables de entorno para máxima seguridad.

**Variables de Entorno Críticas:**
- `SECRET_KEY`: Clave secreta y aleatoria para firmar sesiones.
- `DEFAULT_ADMIN_PASSWORD`: Contraseña inicial para el usuario `admin`.
- `DATABASE_URL`: URL de conexión a la base de datos PostgreSQL externa.
- `CORS_ALLOWED_ORIGINS`: Lista de URLs permitidas para conectarse al servidor de WebSockets, separadas por comas (ej. `https://mi-app.onrender.com,http://localhost:5000`).

## Historial de Cambios

### 2025-09-05 (Sesión de Tarde)

*   **Corrección de Errores en Rutas de Administrador (top_product_query)**:
    *   **Descripción:** Se corrigió un `SyntaxError` y `IndentationError` en `app/routes/admin_routes.py` que impedían el inicio de la aplicación. El error se encontraba en la consulta `top_product_query` dentro de la función `reports`, donde un paréntesis cerraba prematuramente la consulta, causando que los métodos encadenados (`.join`, `.filter`, etc.) fueran interpretados como sintaxis inválida. Se eliminó el paréntesis incorrecto para permitir la correcta construcción de la consulta.
    *   **Impacto:** La aplicación ahora puede iniciarse y los reportes de administrador funcionan correctamente sin errores.