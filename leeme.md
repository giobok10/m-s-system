### **Requisitos Funcionales**

### **Rol: Administrador**

### **Funcionalidad 1: Gestión del Menú y del Inventario**

- **Descripción:** El administrador puede gestionar la lista de todos los productos disponibles para la venta, incluyendo comidas, bebidas y extras.
- **Requisitos:**
    - El administrador debe tener una vista de todos los productos en el menú.
    - El sistema debe permitir categorizar los productos para que se vean de forma ordenada (por ejemplo, "Principal", "Bebidas", "Extras").
    - Para cada producto, el sistema debe guardar la siguiente información:
        - **ID del producto:** Un identificador único.
        - **Nombre del producto:** El nombre con el que se vende.
        - **Precio:** El costo del producto en quetzales.
        - **Categoría:** La categoría a la que pertenece (Principal, Bebida, Extra).
    - El administrador debe poder:
        - **Agregar** nuevos productos.
        - **Editar** los datos de los productos existentes (nombre, precio, categoría).
        - **Eliminar** productos.

### **Funcionalidad 2: Gestión de Stock**

- **Descripción:** El administrador puede actualizar y editar la cantidad de productos disponibles para la venta.
- **Requisitos:**
    - El administrador debe tener una vista de todos los productos registrados en el inventario.
    - Debe haber una opción para "actualizar stock" que permita ingresar la cantidad de unidades de cada producto.
    - Debe poder editar el stock de un producto en caso de un error al ingresar la cantidad.

### **Funcionalidad 3: Cierre de Caja y Balance Diario**

- **Descripción:** El administrador puede cerrar el día de ventas, obtener un reporte detallado y hacer un balance con el dinero físico para verificar que no haya desbalances.
- **Requisitos:**
    - Al final del día, el administrador ingresa el monto total de dinero en efectivo en la caja.
    - El sistema genera un reporte detallado de todas las ventas del día, que debe incluir:
        - La cantidad de cada producto vendido.
        - El nombre de cada producto.
        - El precio por unidad de cada producto.
        - El total de ventas del día.
    - El sistema compara el total de ventas con el monto ingresado para el balance.
    - Si hay un desbalance (sobra o falta dinero), el sistema debe mostrar la diferencia exacta.
    - El reporte de ventas y el balance deben poder ser descargados en formato PDF.

### **Funcionalidad 4: Reportes de Ventas (Semanal y Mensual)**

- **Descripción:** El administrador puede consultar reportes que le muestren lo que más se vendió y los días más activos, tanto de forma semanal como mensual.
- **Requisitos:**
    - El sistema debe permitir generar un reporte semanal que muestre:
        - El producto más vendido de la semana.
        - El día con más ventas en esa semana.
    - El sistema debe permitir generar un reporte mensual que muestre:
        - El producto más vendido del mes.
        - El día de la semana con más ventas en ese mes.
    - El sistema debe basar estos reportes en los datos de las ventas diarias (fecha y nombre del producto).

### **Rol: Mesero/Cajero**

### **Funcionalidad 1: Tomar Pedido**

- **Descripción:** El mesero/cajero debe poder tomar una orden de un cliente, incluyendo los productos principales, extras, y notas especiales.
- **Requisitos:**
    - El mesero debe poder ingresar el nombre del cliente y su número de teléfono (opcional).
    - Debe haber una interfaz visual con el menú del restaurante, categorizado por "Principal", "Bebidas" y "Extras".
    - Al seleccionar un producto principal, debe aparecer una opción para agregar "extras" o "notas".
    - El mesero debe poder especificar la cantidad de cada producto.
    - El sistema debe mostrar el stock disponible de cada producto.

### **Funcionalidad 2: Gestionar la Orden**

- **Descripción:** El mesero debe poder modificar los productos de una orden antes de enviarla a la cocina, incluyendo editar la cantidad o quitar productos.
- **Requisitos:**
    - El mesero debe ver un resumen claro de los productos que ha agregado a la orden.
    - Debe haber una opción para **eliminar** un producto de la orden.
    - Debe haber una opción para **editar** un producto, que permita:
        - Cambiar la cantidad de ese producto.
        - Modificar los extras o las notas especiales.

### **Funcionalidad 3: Enviar y Anular Pedido**

- **Descripción:** El mesero debe poder enviar una orden a la cocina para su preparación o anularla si es necesario antes de que se prepare.
- **Requisitos:**
    - El sistema debe tener un botón o una opción clara para **"Mandar a Cocina"**.
    - Solo después de que el mesero presione este botón, el pedido se debe mostrar en la pantalla del cocinero.
    - Debe haber una opción para **"Anular Pedido"** para órdenes que aún no han sido enviadas a la cocina.
    - Anular un pedido no debe afectar el inventario ni los reportes de ventas.

### **Funcionalidad 4: Procesar Cobro**

- **Descripción:** El mesero/cajero puede procesar el pago de una orden, manejar efectivo y calcular el cambio de forma automática.
- **Requisitos:**
    - El sistema debe mostrar el total de la orden, incluyendo productos principales, bebidas y extras.
    - El mesero debe poder ingresar el monto de efectivo que el cliente entrega.
    - El sistema debe calcular automáticamente y mostrar el monto exacto del cambio a devolver.
    - El sistema debe generar un comprobante de pago con el detalle de los productos, el total de la orden, el monto de efectivo recibido y el cambio entregado, en un pdf descargable.

### **Funcionalidad 5: Agregar a una Orden Activa**

- **Descripción:** El mesero debe poder agregar productos a una orden que ya fue tomada pero que aún no ha sido pagada.
- **Requisitos:**
    - El mesero debe tener una forma de identificar las órdenes que están activas (por ejemplo, en una lista de espera).
    - Al seleccionar una orden activa, debe haber una opción para **agregar nuevos productos** a ella.
    - Esta adición debe actualizar automáticamente el total de la orden.
    - El mesero debe poder agregar productos a una orden activa hasta el momento en que se realice el cobro.

### **Rol: Cocinero**

### **Funcionalidad 1: Recepción y Gestión de Pedidos**

- **Descripción:** El cocinero debe recibir los pedidos confirmados por el mesero y gestionarlos de forma simple.
- **Requisitos:**
    - El cocinero solo ve los pedidos que han sido enviados por el mesero (al presionar el botón "Mandar a Cocina").
    - Cada pedido debe mostrarse de forma clara e individual, en el orden en que fue recibido.
    - La información de cada pedido debe incluir:
        - **ID de la Orden** (para identificarla de forma única).
        - **Nombre del Cliente** (para saber a quién pertenece el pedido).
        - **Detalle completo de la orden:**
            - Nombre del producto.
            - Cantidad de cada producto.
            - Cualquier extra o nota especial agregada (ej. "con salchicha extra", "sin cebolla").
    - Para cada pedido, debe haber dos botones claros:
        - Uno para marcar el pedido como **"En Preparación"**.
        - 
            - Otro para marcar el pedido como **"Listo"** (cuando ya está terminado).

### **Funcionalidad 2: Consulta de Stock**

- **Descripción:** El cocinero debe poder ver la cantidad de productos terminados disponibles para la venta.
- **Requisitos:**
    - El cocinero debe tener acceso a una vista en tiempo real del stock.
    - Esta vista debe mostrar el nombre del producto y la cantidad disponible.
    - El cocinero debe poder saber la cantidad de productos disponibles que le quedan en el día.

### **Requisitos No Funcionales**

### **1. Usabilidad y Diseño**

- **Descripción:** El sistema debe ser intuitivo, fácil de aprender y simple de usar para todos los roles (administrador, mesero/cajero y cocinero).
- **Requisitos:**
    - La interfaz debe ser limpia, organizada y no estar sobrecargada de información.
    - Los menús y botones deben tener un diseño consistente y ser fáciles de encontrar.
    - La información más importante para cada rol (por ejemplo, el menú para el mesero, la lista de pedidos para el cocinero) debe ser visible en la pantalla principal.

### **2. Rendimiento**

- **Descripción:** El sistema debe ser rápido y responsivo para asegurar un flujo de trabajo eficiente en el restaurante.
- **Requisitos:**
    - La carga de cualquier página o sección (ej. el menú, la lista de pedidos) debe ser casi instantánea.
    - Las actualizaciones en tiempo real (como cuando un pedido aparece en la pantalla del cocinero) deben ocurrir en menos de 1-2 segundos.
    - Los cálculos (como el total de una orden o el cambio en el cobro) deben ser inmediatos, sin demoras.

### **3. Seguridad** (continuación)

- *Requisitos de Seguridad Adicionales:
    - El registro de usuarios debe ser controlado por roles:
        - Solo el **administrador** debe poder crear las cuentas de los roles de **mesero** y **cocinero**.
        - La cuenta del **primer administrador** debe ser creada durante la instalación del sistema y no a través de un registro público.
    - Las contraseñas de todos los usuarios deben estar encriptadas para proteger la información en caso de una fuga de datos.
    - El sistema debe cerrar la sesión del usuario después de un período de inactividad para evitar accesos no autorizados.

RESUMEN:

### **Requisitos del Sistema Web para Restaurante**

### **Rol 1: Administrador**

- **Funcionalidad 1: Gestión del Menú y del Inventario**
    - **Permite:** Agregar, editar y eliminar productos (principales, bebidas, extras).
    - **Almacena:** ID, nombre, precio, y la categoría (Principal, Bebida, Extra).
- **Funcionalidad 2: Gestión de Stock**
    - **Permite:** Ver y actualizar la cantidad de stock disponible para cada producto.
- **Funcionalidad 3: Cierre de Caja y Balance Diario**
    - **Permite:** Generar un reporte detallado de las ventas del día, comparar con el dinero físico en caja y mostrar cualquier desbalance. El reporte debe ser descargable en PDF.
- **Funcionalidad 4: Reportes de Ventas (Semanal y Mensual)**
    - **Permite:** Generar reportes que muestren los productos más vendidos y los días más activos, tanto por semana como por mes.

---

### **Rol 2: Mesero/Cajero**

- **Funcionalidad 1: Tomar Pedido**
    - **Permite:** Crear una nueva orden, seleccionar productos, agregar extras y notas, e ingresar la información del cliente (nombre, teléfono opcional). Muestra el stock disponible.
- **Funcionalidad 2: Gestionar la Orden**
    - **Permite:** Editar una orden antes de enviarla a la cocina, incluyendo cambiar cantidades, modificar extras o eliminar productos.
- **Funcionalidad 3: Enviar y Anular Pedido**
    - **Permite:** Enviar la orden a la pantalla del cocinero o anularla si el cliente se va antes de que se prepare.
- **Funcionalidad 4: Procesar Cobro**
    - **Permite:** Procesar el pago de una orden, ingresando el efectivo recibido. El sistema calcula el cambio automáticamente y genera un comprobante con todos los detalles en un pdf descargable.
- **Funcionalidad 5: Agregar a una Orden Activa**
    - **Permite:** Añadir productos a una orden que ya está en curso, siempre y cuando no se haya realizado el cobro.

---

### **Rol 3: Cocinero**

- **Funcionalidad 1: Recepción y Gestión de Pedidos**
    - **Permite:** Ver los pedidos en tiempo real solo después de que el mesero los envía. Puede marcar los pedidos como "En Preparación" y "Listo".
- **Funcionalidad 2: Consulta de Stock**
    - **Permite:** Ver en tiempo real la cantidad de productos terminados disponibles para saber qué pueden ofrecer.

---

### **Requisitos No Funcionales**

- **Usabilidad y Diseño:** La interfaz debe ser simple, intuitiva y no estar sobrecargada.
- **Rendimiento:** El sistema debe ser rápido, con cargas y actualizaciones casi instantáneas (menos de 1-2 segundos).
- **Seguridad:** El sistema debe tener un login para cada rol, con acceso restringido. Solo el administrador puede crear las cuentas de mesero y cocinero, y la cuenta del primer administrador se crea de forma segura.

```
/proyecto-restaurante/
│
├── app/                  # Directorio principal de la aplicación Flask
│   │
│   ├── __init__.py       # Inicializa la aplicación Flask, la base de datos y extensiones (SocketIO)
│   │
│   ├── models.py         # Define los modelos de la base de datos (Producto, Orden, Usuario, etc.) con SQLAlchemy
│   │
│   ├── config.py         # Configuraciones de la aplicación (clave secreta, URI de la base de datos, etc.)
│   │
│   ├── routes/           # Organiza las rutas por rol usando Blueprints
│   │   ├── __init__.py
│   │   ├── admin_routes.py    # Rutas para el Administrador (menú, stock, reportes)
│   │   ├── waiter_routes.py   # Rutas para el Mesero/Cajero (pedidos, cobros)
│   │   ├── cook_routes.py     # Rutas para el Cocinero (visualización de órdenes)
│   │   └── auth_routes.py     # Rutas para el login y logout
│   │
│   ├── sockets/          # Lógica para los eventos de WebSockets
│   │   ├── __init__.py
│   │   └── order_events.py    # Maneja eventos en tiempo real (ej: nueva orden, cambio de estado)
│   │
│   ├── services/         # Lógica de negocio más compleja (ej: generar PDFs)
│   │   ├── __init__.py
│   │   └── report_service.py  # Funciones para crear los reportes de ventas en PDF
│   │
│   ├── static/           # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   │   └── style.css      # Estilos personalizados
│   │   ├── js/
│   │   │   └── main.js        # Lógica de cliente (conexión WebSocket, interacciones básicas)
│   │   └── img/
│   │       └── logo.png
│   │
│   └── templates/        # Plantillas HTML con Jinja2
│       ├── layouts/
│       │   └── base.html      # Plantilla base con la estructura común (nav, footer, etc.)
│       │
│       ├── admin/             # Vistas del panel de administrador
│       │   ├── dashboard.html
│       │   ├── menu.html
│       │   └── reports.html
│       │
│       ├── waiter/            # Vistas para el mesero/cajero
│       │   ├── take_order.html
│       │   └── active_orders.html
│       │
│       ├── cook/              # Vista para el cocinero
│       │   └── kitchen_display.html
│       │
│       └── auth/              # Vistas de autenticación
│           └── login.html
│
├── instance/             # Carpeta para archivos que no van al control de versiones
│   └── restaurant.db     # Aquí se guardará tu base de datos SQLite
│
├── migrations/           # (Opcional) Para migraciones de base de datos con Flask-Migrate
│
├── tests/                # Pruebas unitarias y de integración
│   ├── __init__.py
│   └── test_orders.py
│
├── .env                  # Variables de entorno (no subir a git)
├── .gitignore            # Archivos a ignorar por git (ej: instance/, __pycache__/)
├── Dockerfile            # Instrucciones para construir la imagen Docker de la aplicación
├── docker-compose.yml    # Define los servicios, redes y volúmenes para Docker (útil para microservicios)
├── requirements.txt      # Lista de dependencias de Python (Flask, Flask-SocketIO, etc.)
└── run.py                # Punto de entrada para ejecutar la aplicación

```

### **Explicación de las Decisiones:**

- **`app/`**: Usar un paquete (`app`) para tu aplicación te permite organizar el código de manera modular. Es una práctica estándar en proyectos Flask.
- **Blueprints (`routes/`)**: Separar las rutas por rol (administrador, mesero, cocinero) hace que el código sea mucho más fácil de mantener a medida que el proyecto crece.
- **`sockets/`**: Aislar la lógica de WebSockets en su propio directorio mantiene el código de las rutas limpio y se enfoca solo en las interacciones en tiempo real.
- **`services/`**: Para lógica que no es ni una ruta ni un modelo (como generar un PDF), un directorio de "servicios" es ideal.
- **`instance/`**: Flask recomienda esta carpeta para archivos de configuración específicos de la instancia o, en este caso, la base de datos SQLite. Debe estar en tu `.gitignore`.
- **Docker**: El `Dockerfile` te permitirá crear una imagen autocontenida de tu aplicación, y `docker-compose.yml` te facilitará levantar todo el entorno (incluso si en el futuro agregas otro servicio, como una base de datos diferente o un servicio de notificaciones).

Esta estructura te da una base sólida y organizada para empezar a construir tu sistema.