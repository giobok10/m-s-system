### 2025-09-05

*   **Corrección de Lógica de Fechas en Reportes (Administrador)**:
    *   **Solucionado:** Se corrigió un error lógico fundamental que causaba que los datos de días anteriores se mostraran en las vistas del día actual (ej. el Cierre Diario del 5 de septiembre mostraba las ventas del 4 de septiembre). 
    *   **Causa:** La conversión de fechas y zonas horarias directamente en la consulta a la base de datos era inconsistente.
    *   **Solución:** Se reescribió la lógica de consulta en las rutas del administrador (`dashboard`, `reports`, `daily_close`). Ahora, la aplicación calcula el rango exacto de 24 horas para la fecha local (en zona horaria de Guatemala) y lo convierte a UTC antes de consultar la base de datos. Esto garantiza que las consultas de fechas sean precisas y robustas.

*   **Corrección de Errores Críticos y Mejoras de Estabilidad (Producción)**:
    *   **Solucionado (Generación de PDF):** Se corrigió un error que causaba que los reportes PDF (como el Cierre Diario) mostraran datos incorrectos o desactualizados en dispositivos móviles. El problema se debía al caché del navegador y se solucionó añadiendo cabeceras `Cache-Control` para forzar la descarga de una versión nueva del reporte cada vez.
    *   **Solucionado (Manejo de Fechas):** Se corrigió la causa raíz de las fechas y horas incorrectas en la base de datos. Se modificaron los modelos de datos (`User`, `Product`, `Order`, `DailyReport`) para que las columnas de fecha/hora (`created_at`, `updated_at`) utilicen la zona horaria de la base de datos (UTC) de forma nativa. Esto asegura que todas las nuevas órdenes y registros tengan una marca de tiempo precisa y consistente.
    *   **Mejora (Estabilidad de Conexión):** Se ajustó la configuración de `Socket.IO` para incluir un mecanismo de "heartbeat" (`ping/pong`). Esto reduce significativamente los errores de desconexión (`Bad file descriptor`, `Session is disconnected`) que ocurrían en el entorno de producción de Render, mejorando la estabilidad de las actualizaciones en tiempo real.

### 2025-09-04 (Sesión de Tarde)

*   **Corrección en Cálculo de Precios de Combos (Mesero)**:
    *   **Solucionado:** Se corrigió un error crítico que impedía que el costo de los "extras" se sumara al precio total de los "combos" al crear una orden. La lógica del backend ahora calcula y guarda correctamente el precio final, incluyendo los extras, para todos los tipos de productos.

### 2025-09-04

*   **Corrección en Toma de Pedidos (Mesero)**:
    *   **Solucionado:** Se corrigió un error en la actualización visual del stock en la página de "Tomar Pedido". El stock de los productos que son componentes de un "Combo" no se estaba descontando visualmente al agregar el combo a la orden. La lógica ha sido robustecida para que ahora el consumo de stock por combos se refleje correctamente en tiempo real en el menú.
    *   **Solucionado:** Se corrigió un error crítico que impedía agregar productos de la categoría "Principal" a una orden. El problema ocurría porque la lista de variantes del producto no se estaba enviando correctamente a la interfaz, causando un error de JavaScript que bloqueaba la aparición del modal.
    *   **Mejora:** Si un producto de tipo "Principal" no tiene variantes definidas, ahora se mostrará un modal informativo indicando que no se puede vender, en lugar de fallar silenciosamente.

*   **Mejora de Experiencia de Usuario (Mesero)**:
    *   **Nueva Funcionalidad:** El stock visible en la página de "Tomar Pedido" ahora se actualiza dinámicamente. Cuando se agrega un producto a la "Orden Actual", el stock mostrado en el menú disminuirá visualmente, y se restaurará si el producto es eliminado de la orden. Esto proporciona un feedback inmediato y preciso del inventario disponible antes de crear la orden.

### 2025-09-03 (Sesión de Tarde)

*   **Nueva Funcionalidad: Sistema de Combos**:
    *   **Descripción:** Se ha implementado un sistema completo para crear y gestionar "Combos" o paquetes de productos.
    *   **Base de Datos:** Se añadió la tabla `combo_item` para definir las "recetas" de los combos.
    *   **Panel de Administrador:** Se actualizó la interfaz de "Gestión de Menú" para permitir la creación y edición de productos de categoría "Combo", permitiendo al administrador asignar múltiples productos componentes y sus cantidades.
    *   **Lógica de Stock:** Se implementó la deducción automática de stock. Al crear una orden que incluye un combo, el sistema ahora descuenta las cantidades correspondientes del stock de cada producto componente. La lógica de cancelación también fue actualizada para restaurar el stock correctamente.

*   **Mejoras y Correcciones Críticas**:
    *   **Solucionado:** Corregido un `SyntaxError` en el panel de administrador que impedía la edición de cualquier producto.
    *   **Solucionado:** Corregido un `TypeError` crítico en la página de "Tomar Pedido" que impedía su funcionamiento.
    *   **Solucionado:** Se corrigieron múltiples bugs en la lógica de JavaScript de "Tomar Pedido", incluyendo errores en el cálculo de stock de extras, la asignación incorrecta de extras a productos y un bug que impedía que el modal de cantidad se cerrara.
    *   **Mejora:** Se habilitó la funcionalidad para añadir "Extras" a los productos de tipo "Combo".
    *   **Mejora:** Se refinó la lista de productos disponibles al crear un combo para mostrar solo componentes relevantes (Principales y Bebidas).

*   **Configuración y Seguridad**:
    *   **Solucionado:** Corregido un error en `docker-compose.yml` que causaba que la contraseña de administrador por defecto se estableciera como una cadena vacía.
    *   **Mejora:** Se cambió la contraseña por defecto del usuario `admin` a un valor más seguro.

*   **Documentación**:
    *   Actualizada la `GUIA_USUARIO.md` y `DOCUMENTACION_TECNICA.md` para reflejar todas las nuevas funcionalidades y cambios.

### 2025-09-03

*   **Mejora en la Selección de Extras (Mesero)**:
    *   **Cambio:** Se ha modificado la interfaz de "Tomar Pedido" para permitir la selección de cantidades para los productos "Extra".
    *   **De:** Anteriormente, los extras solo podían ser seleccionados con un checkbox (una unidad por producto principal).
    *   **A:** Ahora, cada extra tiene un campo numérico, permitiendo al mesero agregar múltiples unidades de un mismo extra a un solo producto (ej. "Torta con doble queso extra").
    *   **Impacto:** Se actualizó la lógica del frontend (JavaScript) para calcular precios y validar stock basado en cantidades, y se ajustó el backend (`waiter_routes.py`) para procesar y almacenar correctamente esta nueva información, incluyendo la restauración de stock al cancelar una orden.

*   **Corrección de Error en Reportes (Producción)**:
    *   **Solucionado:** Se corrigió un `TypeError` que causaba un "Internal Server Error" en la página de reportes (`/admin/reports`) cuando la aplicación se ejecutaba en el servidor de producción (Render).
    *   **Causa:** El error ocurría porque el código intentaba procesar un objeto de tipo `date` como si fuera un `string`. Este comportamiento variaba entre la base de datos local (SQLite) y la de producción (PostgreSQL).
    *   **Solución:** Se eliminó la conversión innecesaria en `admin_routes.py`, asegurando que el formato de fecha se maneje correctamente en ambos entornos.

### 2025-09-02 (Sesión de Tarde)

*   **Cambio de Estrategia de Base de Datos para Producción**:
    *   **Mejora:** Se migró la estrategia de base de datos para producción de SQLite a una base de datos PostgreSQL externa y persistente.
    *   **Causa:** Se identificó que los sistemas de archivos de las plataformas de hosting gratuitas (como Render) son efímeros, lo que causaba la pérdida total de los datos de la base de datos SQLite en cada reinicio o despliegue.
    *   **Solución:** Se añadió el driver `psycopg2-binary` a los requerimientos y se actualizó la configuración para leer la URL de la base de datos desde la variable de entorno `DATABASE_URL`.
    *   **Documentación:** Se actualizaron los archivos `README.md` y `DOCUMENTACION_TECNICA.md` para reflejar que el uso de una base de datos PostgreSQL externa es obligatorio para producción.

### 2025-09-02

*   **Gestión de Seguridad**:
    *   **Añadido:** Se creó un script temporal (`set_admin_password.py`) para permitir el cambio de la contraseña del administrador de forma segura a través de la línea de comandos. El script se eliminó después de su uso.
    *   **Mejora:** Se actualizó la contraseña del administrador a un valor seguro.

### 2025-09-01

*   **Corrección en Reportes de Ventas (Administrador)**:
    *   **Solucionado:** Se corrigió la lógica para calcular el "Producto más vendido" en los reportes semanales y mensuales. Ahora el sistema agrupa correctamente las variantes de un producto (ej. "Tacos de res (Unidad)" y "Tacos de res (porción de 3)") bajo el producto base.
    *   **Mejora:** El cálculo ahora se basa en el consumo de stock (`stock_consumption`) en lugar de la cantidad de items vendidos, reflejando con mayor precisión el uso del inventario y mostrando el producto más popular real.
*   **Corrección de Errores en Toma de Pedidos (Mesero)**:
    *   **Solucionado:** Se corrigió un error visual en la página "Tomar Pedido" donde el stock de los productos se mostraba incorrectamente al añadir diferentes tipos de productos a una misma orden. El error se debía a una variable global que no se reiniciaba.
    *   **Solucionado:** Se corrigió un `Internal Server Error` en la página de "Tomar Pedido" causado por un error de sintaxis en la plantilla de Jinja2.
*   **Mejora en Toma de Pedidos (Mesero)**:
    *   **Añadido:** Se agregó el campo para ingresar el "Teléfono del Cliente (Opcional)" en el formulario de "Tomar Pedido", completando la funcionalidad descrita en la guía de usuario.

### 2025-08-31 (Sesión de Tarde)

*   **Corrección de Errores Críticos en Módulos de Cocinero y Mesero**:
    *   **Solucionado (Cocinero):** Se corrigió la vista de "Inventario" del cocinero (`/cook/stock`) para que ya no muestre las variantes de los productos, sino únicamente los productos base y simples con su stock real, solucionando una inconsistencia visual.
    *   **Solucionado (Mesero):** Se corrigió un error crítico (`TypeError`) que impedía la carga de la página de "Tomar Pedido" (`/waiter/take_order`). El error fue causado por una incorrecta serialización de los datos de las variantes en la plantilla.
    *   **Solucionado (Mesero):** Se corrigió un error en la ventana de "Agregar Producto" donde el "Stock disponible" se mostraba como `NaN` para los productos con variantes.
    *   **Restaurado (Mesero):** Se restauró la funcionalidad que actualiza dinámicamente el stock visible de los "Extras" en la ventana de "Agregar Producto", la cual se había perdido durante las modificaciones anteriores.
    *   **Solucionado (Mesero):** Corregido un error que mostraba el precio y total como `NaN` para productos simples (bebidas, extras) al ser agregados a una orden.
*   **Mejora Visual (Cocinero):** Se ha mejorado la presentación de las órdenes en el dashboard del cocinero. Ahora los extras y las notas se muestran claramente agrupados debajo de cada producto.
*   **Mejora de Claridad (Cocinero):** El nombre de los productos con variantes ahora se muestra de forma completa en el dashboard del cocinero (ej. "Tacos de Res (Unidad)") para evitar ambigüedades.
*   **Mejora Visual (Cocinero):** Corregido un error visual donde el botón "Marcar como Listo" permanecía con apariencia de deshabilitado después de que una orden cambiara de estado en tiempo real.
*   **Mejora de Claridad (Mesero):** Se ha mejorado la presentación de las órdenes en la vista de "Detalles de la Orden" y en el comprobante PDF. Ahora los nombres de los productos con variantes se muestran de forma completa (ej. "Tacos de Res (Unidad)") para mayor claridad.

### 2025-08-31 (Implementación de lee.md)

*   **Visualización Consistente de Nombres de Productos**:
    *   **Reportes de Administrador:** Implementada la visualización completa de nombres de productos (incluyendo variantes como "Producto Base (Variante)") en los reportes de ventas mensuales y semanales, tanto en la interfaz web como en los PDFs generados.
    *   **Cierre Diario:** Implementada la visualización completa de nombres de productos en el detalle de ventas del cierre diario, tanto en la interfaz web como en los PDFs generados.
    *   **Procesamiento de Pago (Mesero):** Implementada la visualización completa de nombres de productos en los ítems de la orden en la pantalla de procesamiento de pago.

### 2025-08-31

*   **Nueva Funcionalidad: Variantes de Productos**: 
    *   **Descripción:** Se ha implementado un sistema de variantes que permite a ciertos productos (categoría "Principal") tener un stock base y venderse en diferentes formatos (ej. "Taco por Unidad" y "Taco por Porción").
    *   **Cambios en Base de Datos (Backend):** Se modificó el modelo `Product` para soportar una relación padre-hijo. Los productos base (padres) manejan el stock, mientras que las variantes (hijos) tienen su propio precio y definen cuánto stock del padre consumen.
    *   **Panel de Administrador (Frontend/Backend):**
        *   Se rediseñó la página de "Gestión de Menú" para permitir la creación de "Productos Base" en la categoría "Principal".
        *   Se añadió una nueva interfaz para crear y gestionar "Variantes" para cada producto base, especificando su nombre, precio y consumo de stock.
    *   **Toma de Pedidos de Mesero (Frontend/Backend):**
        *   Se actualizó la interfaz de "Tomar Pedido" para que al seleccionar un producto principal, se muestre un modal con sus variantes disponibles.
        *   La lógica de creación de órdenes fue reescrita para validar y descontar el stock del producto base según la variante y cantidad seleccionada.
    *   **Lógica de Cancelación (Backend):** Se ajustó la lógica de cancelación de órdenes para restaurar correctamente el stock al producto base cuando se cancela un pedido que contiene variantes.

### 2025-08-30 (Tarde)

*   **Implementación Completa de WebSockets para Actualizaciones en Tiempo Real**:
    *   **Solucionado:** Se eliminó la necesidad de recargar la página para ver actualizaciones. Ahora, todos los cambios de estado de órdenes y de stock se reflejan instantáneamente en todos los roles.
    *   **Mejora en Notificaciones de Stock (Backend):** Se añadieron eventos de WebSocket (`stock_update`) que se emiten desde el servidor cada vez que el stock de un producto cambia (al crear/cancelar órdenes o al editar desde el panel de administrador).
    *   **Mejora en Notificaciones de Órdenes (Backend):** Las actualizaciones de estado de las órdenes (ej. 'en preparación', 'listo') ahora se emiten a las salas de `kitchen` y `waiters`, permitiendo que todos los cocineros y meseros vean los cambios en tiempo real.
    *   **Actualización Dinámica de la Interfaz (Frontend):** Se centralizó y reescribió la lógica de JavaScript (`main.js`) para manejar los eventos de WebSocket. El nuevo código manipula el DOM directamente para:
        *   Añadir tarjetas de nuevas órdenes en el dashboard del cocinero.
        *   Actualizar el estado y los botones de las órdenes en los dashboards de cocineros y meseros.
        *   Eliminar las órdenes de la vista del cocinero una vez que están listas.
        *   Reflejar la cantidad de stock actualizada en la página de "Tomar Pedido" y en la de "Inventario" del cocinero.
    *   **Optimización de la Experiencia de Usuario:** Las acciones del cocinero (iniciar/terminar preparación) ya no recargan la página, proporcionando una experiencia de usuario fluida y verdaderamente en tiempo real.

### 2025-08-30

*   **Revisión Completa de la Lógica de Inventario**:
    *   **Cambio en Flujo de Stock (Backend)**: Se modificó la lógica de negocio fundamental. El stock ahora se descuenta de la base de datos en el momento de la **creación de la orden**, no al enviarla a cocina. Esto asegura que el inventario sea consistente y preciso en todo momento.
    *   **Ajuste en Cancelaciones (Backend)**: Se actualizó la lógica de cancelación para que devuelva correctamente el stock al inventario si una orden es cancelada en estado `pendiente` o `sent_to_kitchen`.
    *   **Feedback Visual Inmediato (Frontend)**: Se implementó una actualización completa de la interfaz de "Tomar Pedido". Ahora, el stock visible tanto en las tarjetas de producto como en las opciones de extras se actualiza dinámicamente a medida que el mesero construye la orden, previniendo agregar más productos de los disponibles y reflejando el estado del "carrito" en tiempo real.

### 2025-08-29

*   **Ciclo de Correcciones y Mejoras Críticas**:
    *   **Corrección de Stock de Extras (Implementación Robusta)**: Se solucionó de manera definitiva el error que impedía descontar el stock de los productos "Extra". La nueva implementación guarda los IDs de los extras en la orden, asegurando un descuento preciso y eliminando la dependencia de búsquedas por nombre que fallaban anteriormente.
    *   **Mejora en la Visualización de Órdenes**: Se creó un filtro personalizado (`parse_extras`) para que en todas las vistas (detalles de orden, panel de cocinero) los extras se muestren de forma legible para el usuario (ej: "Salchicha Extra") en lugar de la estructura de datos JSON.
    *   **Mejora en Generación de Recibos PDF**:
        *   Se añadió la funcionalidad para que el botón "Generar PDF" aparezca también en la vista de detalles de una orden ya pagada.
        *   Para soportar esto, se modificó la base de datos para almacenar el monto de efectivo recibido y el cambio directamente en la orden.
        *   Se corrigió un error de zona horaria que mostraba una hora incorrecta en el PDF. La hora del recibo ahora es consistente con la del resto del sistema.
    *   **Corrección en Reporte de Cierre Diario**: Se solucionó un error que causaba que el "Total de Ventas" se mostrara como 0.00 en el PDF del cierre diario si el cierre se guardaba más de una vez en el mismo día.
    *   **Corrección de Errores Introducidos**: 
        *   Se solucionó un `Internal Server Error` en el panel del administrador causado por una falta de actualización en la base de datos después de modificar el modelo `Order`. Se regeneró la base de datos para alinearla con el código.
        *   Se corrigieron múltiples `NameError` y `TypeError` causados por descuidos durante el desarrollo (falta de imports de `json`, manejo incorrecto de tipos de datos), dejando el sistema en un estado estable.

## Historial Completo

### 2025-08-28

*   **Corrección Crítica en Reportes de Administrador**:
    *   **Solucionado:** Se corrigió un `AttributeError` en la página de reportes (`/admin/reports`) que impedía su visualización. El error fue causado por un mal manejo del formato de fecha devuelto por la base de datos SQLite.

*   **Mejoras en el Módulo de Mesero**:
    *   **Mejora:** Se actualizó el panel del mesero (`/waiter/dashboard`) para mostrar una nueva sección con el historial de órdenes completadas (pagadas) por el mesero durante el día actual.
    *   **Nueva Funcionalidad:** Se implementó la capacidad de generar un recibo de pago en formato PDF desde la pantalla de confirmación de pago.
        *   Se añadió una función `generate_receipt_pdf` al servicio de reportes.
        *   Se creó una nueva ruta (`/waiter/receipt/<id>/pdf`) para manejar la generación del PDF.
        *   Se agregó un botón "Generar PDF" en la plantilla del recibo.

*   **Corrección de Errores del Rol de Mesero/Cajero**:
    *   **Solucionado:** Se corrigió un "Internal Server Error" que ocurría al intentar procesar un pago (`/waiter/process_payment/<id>`). El error se debía a la ausencia de la plantilla `waiter/process_payment.html`.
    *   **Mejora Proactiva:** Se creó también la plantilla `waiter/payment_receipt.html` para evitar un error subsiguiente después de procesar el pago, asegurando que el recibo se muestre correctamente.

### 2025-08-27

*   **Corrección en la gestión de inventario para "Extras"**:
    *   **Solucionado:** El inventario de los productos categorizados como "Extra" no se descontaba al enviar una orden a cocina. Se corrigió la lógica para que el stock de los extras se reduzca y se restaure correctamente, al igual que los productos principales.

*   **Corrección de Errores del Rol de Cocinero**:
    *   **Solucionado:** Se corrigió un "Internal Server Error" que ocurría al acceder a la vista de "Inventario" (`/cook/stock`). El error se debía a la ausencia de la plantilla `cook/stock.html`.

*   **Ajustes y Mejoras Adicionales (Rol de Mesero)**:
    *   **Corregido:** Se ajustó la zona horaria de la aplicación a Guatemala (UTC-6) para que las fechas y horas de las órdenes se muestren correctamente.
    *   **Mejora:** En la ventana emergente para agregar productos, ahora se muestra el stock disponible para cada "Extra" y se deshabilita la selección si el stock es cero.
    *   **Mejora:** Se ocultó la categoría vacía de "Extra" del menú principal en la página de "Tomar Pedido" para una interfaz más limpia.

*   **Corrección de Errores del Rol de Mesero**:
    *   **Solucionado:** Se corrigió un error de "Internal Server Error" que ocurría después de crear una orden. El problema era causado por la ausencia de la plantilla `waiter/view_order.html`.
        *   Se creó la plantilla `app/templates/waiter/view_order.html` para mostrar correctamente los detalles de la orden recién creada.
    *   **Solucionado:** Se rediseñó la funcionalidad para agregar "Extras" a un producto en la pantalla "Tomar Pedido".
        *   Anteriormente, solo existía un campo de texto libre. Ahora, los productos categorizados como "Extra" se muestran como opciones seleccionables (checkboxes) en la ventana modal, tal como se especifica en los requisitos.
        *   Se actualizó la lógica del backend (`waiter_routes.py`) y del frontend (`take_order.html`) para calcular y guardar correctamente el costo adicional de los extras en el total de la orden.

### 2025-08-26 (Sesión de Tarde)

*   **Clarificación de Funcionalidades del Administrador**:
    *   Se analizó y explicó la funcionalidad de la tarjeta "Stock Bajo" en el dashboard del administrador.
    *   Se confirmó que la lógica funciona correctamente: cuenta los productos cuyo stock es igual or inferior a 5.
    *   Se concluyó que el indicador muestra "0" porque no existen productos que cumplan esta condición actualmente.
*   **Validación del Módulo de Administrador**:
    *   Basado en las pruebas realizadas (gestión de menú, usuarios, reportes, cierre diario), se considera que el módulo de administrador funciona correctamente y sin errores aparentes.
    *   No se realizaron cambios en el código, solo se validó y explicó el comportamiento existente.

### 2025-08-26

*   **Corrección del Dashboard de Administrador**:
    *   Se ajustó el umbral de "Stock Bajo" a 5 unidades, según solicitado.
*   **Implementación de Reporte de Cierre Diario**:
    *   Se implementó la generación de PDF para el reporte de cierre diario en la página `/admin/daily_close`.
    *   Se añadió la lógica para obtener los datos de las órdenes del día y pasarlos al servicio de reportes.
*   **Corrección de Visualización de Fecha**:
    *   Se corrigió la visualización de la fecha en la página de cierre diario para que se muestre correctamente.
*   **Intento de Solución de Errores de Consola del Navegador**:
    *   Se identificaron errores "Cannot find menu item with id translate-page" y "Cannot find menu item with id save-page" en la consola del navegador, probablemente causados por extensiones del navegador.
    *   Se intentaron varios workarounds en `app/templates/layouts/base.html`.
    *   Los errores persisten, pero no parecen afectar la funcionalidad de la aplicación. Se decide ignorar los errores por el momento.

### 2025-08-25

*   **Configuración Inicial y Revisión (Implícito)**:
    *   Revisión de la estructura del proyecto y configuración inicial.
    *   Confirmación del uso de Flask, WebSockets, Docker, SQLite, HTML, CSS, JS, Bootstrap.
    *   Confirmación de la creación de `DOCUMENTACION_TECNICA.md` y `GUIA_USUARIO.md`.

*   **Solución de Error de Conexión Inicial (`ERR_CONNECTION_REFUSED`)**:
    *   Se inspeccionaron `docker-compose.yml`, `run.py` y `Dockerfile`.
    *   Se identificó que el servidor de desarrollo de Flask se estaba utilizando en un entorno de producción.
    *   Se añadió `gunicorn` y `eventlet` a `requirements.txt`.
    *   Se modificó `Dockerfile` para usar `gunicorn` como el comando de inicio.

*   **Corrección de Error de Base de Datos (`unable to open database file`)**:
    *   Se identificó el error `sqlite3.OperationalError: unable to open database file`.
    *   Se modificó `app/config.py` para usar una ruta absoluta para la base de datos SQLite (`sqlite:////app/instance/restaurant.db`).

*   **Corrección de Error de Plantilla (`jinja2.exceptions.UndefinedError: 'moment' is undefined`)**:
    *   Se identificó el error `jinja2.exceptions.UndefinedError: 'moment' is undefined`.
    *   Se añadió `Flask-Moment==1.0.6` a `requirements.txt`.
    *   Se inicializó `Flask-Moment` en `app/__init__.py`.

*   **Corrección de Problemas de Conexión de Socket.IO**:
    *   Se identificó una falta de coincidencia de CORS para Socket.IO.
    *   Se ajustó `CORS_ALLOWED_ORIGINS` en `app/config.py` a `http://localhost:5000`.

*   **Mejoras de Interfaz de Usuario y Localización**:
    *   Se corrigieron las clases CSS en `app/templates/admin/reports.html` para usar Bootstrap.
    *   Se tradujeron los enlaces de navegación en `app/templates/layouts/base.html` al español.
    *   Se confirmó el uso de Quetzales (`Q`) y texto en español en todas las plantillas.

*   **Actualizaciones de Documentación**:
    *   Se actualizó `DOCUMENTACION_TECNICA.md` para reflejar el cambio a `gunicorn` en el `Dockerfile`.

*   **Eliminación de Sugerencia en Página de Inicio de Sesión**:
    *   Se eliminó la sugerencia de usuario y contraseña por defecto de `app/templates/auth/login.html`.