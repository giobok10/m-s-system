# Sistema de Gestión para Restaurantes

Un sistema web integral para la gestión de órdenes, inventario y ventas en un restaurante. La aplicación está diseñada para optimizar el flujo de trabajo entre meseros, cocineros y administradores, con actualizaciones en tiempo real para una comunicación fluida.

![Login](https://i.imgur.com/example.png) <!-- Reemplazar con una captura de pantalla real -->

## ✨ Características Principales

### Rol de Administrador
- **Dashboard General:** Vista rápida de ventas del día, órdenes activas y productos con bajo stock.
- **Gestión de Usuarios:** Crear, editar y desactivar cuentas para meseros y cocineros.
- **Gestión de Menú:** 
    - Crear productos simples (bebidas, extras) y productos principales.
    - Sistema de **Variantes**: Permite que un producto base (ej. "Tacos de Res") se venda en diferentes formatos (ej. "Porción de 3", "Unidad"), cada uno con su propio precio y consumo de stock.
- **Reportes de Ventas:** Generar reportes de ventas diarios, semanales y mensuales en formato web y PDF.
- **Cierre de Caja Diario:** Registrar el total de ventas, el efectivo en caja y calcular diferencias.

### Rol de Mesero
- **Toma de Pedidos:** Interfaz intuitiva para tomar órdenes, seleccionar variantes de productos y añadir extras.
- **Envío a Cocina:** Enviar órdenes a cocina con un solo clic.
- **Seguimiento en Tiempo Real:** Ver el estado de las órdenes (`en preparación`, `listo`) actualizado en tiempo real.
- **Procesamiento de Pagos:** Registrar el pago de las órdenes y generar un recibo en PDF.

### Rol de Cocinero
- **Dashboard de Cocina:** Recibir y visualizar nuevas órdenes en tiempo real a medida que llegan.
- **Gestión de Estado:** Marcar órdenes como `en preparación` y `listo para servir`.
- **Vista de Inventario:** Consultar el stock disponible de los productos base.

### Tecnologías Clave
- **Actualizaciones en Tiempo Real:** Gracias a **WebSockets (Flask-SocketIO)**, los cambios en las órdenes y el stock se reflejan instantáneamente en todas las pantallas sin necesidad de recargar la página.
- **Contenerización:** La aplicación está completamente contenerizada con **Docker** y **Docker Compose** para un despliegue y desarrollo consistentes.

## 🚀 Stack Tecnológico

- **Backend:** Python 3.11, Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Base de Datos:** SQLite (por defecto), compatible con PostgreSQL
- **Tiempo Real:** Flask-SocketIO, Eventlet
- **Servidor de Producción:** Gunicorn
- **Contenedores:** Docker, Docker Compose

## ⚙️ Instalación y Ejecución Local

Sigue estos pasos para levantar el proyecto en tu máquina local.

### Prerrequisitos
- Tener [Docker](https://www.docker.com/get-started/) y [Docker Compose](https://docs.docker.com/compose/install/) instalados.

### Pasos

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/giobok10/m-s-system.git
    cd m-s-system
    ```

2.  **Crea el archivo de entorno:**
    Crea un archivo llamado `.env` en la raíz del proyecto. Este archivo contendrá las credenciales y claves secretas. Puedes copiar y pegar el siguiente contenido, **reemplazando los valores por tus propios secretos**.

    ```ini
    # .env
    # Claves secretas de la aplicación. NO subir este archivo a GitHub.

    # Clave secreta para firmar sesiones. Debe ser una cadena larga y aleatoria.
    SECRET_KEY=tu-clave-secreta-larga-y-aleatoria-aqui

    # Contraseña que tendrá el usuario 'admin' la primera vez que la base de datos se cree.
    DEFAULT_ADMIN_PASSWORD=unaContraseñaFuerteParaElAdmin123!
    ```

3.  **Construye y levanta los contenedores:**
    Este comando construirá la imagen de Docker y ejecutará la aplicación. La primera vez puede tardar unos minutos.
    ```bash
    docker-compose up --build -d
    ```

4.  **¡Listo!**
    La aplicación estará disponible en tu navegador en la dirección [http://localhost:5000](http://localhost:5000).

## 👤 Uso y Credenciales

La primera vez que la aplicación se ejecuta, crea un usuario administrador por defecto.

-   **Usuario:** `admin`
-   **Contraseña:** La que hayas configurado en la variable `DEFAULT_ADMIN_PASSWORD` de tu archivo `.env`.

Desde el panel de administrador podrás crear los usuarios para los meseros y cocineros.
