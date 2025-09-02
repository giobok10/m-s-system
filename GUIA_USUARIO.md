# Guía de Usuario - Sistema de Restaurante

## Introducción

Este sistema está diseñado para gestionar las operaciones diarias de un restaurante, desde la toma de órdenes hasta el cierre de caja. Está dividido en tres roles principales: **Administrador**, **Mesero/Cajero** y **Cocinero**.

## Instalación y Configuración

### Requisitos Previos
- Docker y Docker Compose instalados
- Puerto 5000 disponible

### Instalación
1. Descargar el código del sistema
2. Abrir terminal en la carpeta del proyecto
3. Ejecutar: `docker-compose up --build -d`
4. Abrir navegador en: `http://localhost:5000`

### Primer Acceso
- **Usuario**: `admin`
- **Contraseña**: La que hayas configurado en la variable `DEFAULT_ADMIN_PASSWORD` durante la instalación.

⚠️ **IMPORTANTE**: Si usaste una contraseña débil para la configuración inicial, se recomienda cambiarla.

## Rol: Administrador

### Acceso al Sistema
1. Iniciar sesión con credenciales de administrador
2. Serás dirigido al Dashboard principal

### Dashboard Principal
El dashboard muestra:
- **Órdenes del día**: Número total de órdenes procesadas
- **Ventas del día**: Monto total vendido
- **Stock bajo**: Productos con menos de 5 unidades
- **Accesos rápidos**: Cierre diario y reportes

### Gestión del Menú

Ahora, la gestión de productos en la categoría "Principal" es diferente a la de "Bebidas" y "Extras".

#### Agregar Productos Simples (Bebidas y Extras)
1. Ir a **Menú** en la navegación.
2. Hacer clic en **"Agregar Producto"**.
3. Seleccionar la **Categoría** "Bebida" o "Extra".
4. Completar el resto del formulario como antes (Nombre, Precio, Stock).
5. Hacer clic en **"Agregar"**.

#### Agregar Productos con Variantes (Categoría Principal)

Este es un proceso de dos pasos: primero creas el "Producto Base" y luego le añades sus "Variantes".

**Paso 1: Crear el Producto Base**
1.  Ir a **Menú** y hacer clic en **"Agregar Producto"**.
2.  Seleccionar la **Categoría** "Principal (Producto Base)". El campo de precio se ocultará, ya que el precio se define en las variantes.
3.  **Nombre**: Escribe el nombre general del producto (ej. "Tacos de Res").
4.  **Stock Inicial**: Ingresa la cantidad total de unidades que se pueden preparar (ej. si puedes hacer 15 tacos, ingresa 15).
5.  Hacer clic en **"Agregar"**. El producto aparecerá en la lista con una etiqueta de "Stock Base".

**Paso 2: Añadir Variantes al Producto Base**
1.  Busca el producto base que acabas de crear en la categoría "Principal".
2.  Haz clic en el botón verde **"+ Agregar Variante"**.
3.  Se abrirá un formulario para la variante. Complétalo:
    *   **Nombre de la Variante**: El formato de venta (ej. "Unidad" o "Porción de 3").
    *   **Precio**: El precio de venta para *esta* variante (ej. Q7 para la unidad, Q15 para la porción).
    *   **Consumo de Stock**: ¿Cuántas unidades del stock base consume esta variante? (ej. "Unidad" consume `1`, "Porción de 3" consume `3`).
4.  Haz clic en **"Agregar Variante"**.
5.  Repite el proceso para todas las variantes que necesites (Unidad, Porción, etc.). Las variantes aparecerán debajo de su producto base.

#### Editar Productos
1. En la página de Menú, buscar el producto
2. Hacer clic en el ícono de editar (lápiz)
3. Modificar los datos necesarios
4. Hacer clic en **"Actualizar"**

#### Eliminar Productos
1. Buscar el producto en la lista
2. Hacer clic en el ícono de eliminar (basura)
3. Confirmar la eliminación

⚠️ **Nota**: Los productos eliminados se marcan como inactivos, no se borran permanentemente.

### Gestión de Stock

#### Actualizar Stock
1. Ir a **Menú**
2. Editar el producto que necesita actualización de stock
3. Cambiar el valor en el campo **"Stock"**
4. Guardar cambios

#### Monitoreo de Stock Bajo
- El dashboard muestra automáticamente productos con stock ≤ 5 unidades
- Estos productos aparecen con alerta amarilla

### Gestión de Usuarios

#### Crear Usuarios
1. Ir a **Usuarios** en la navegación
2. Hacer clic en **"Agregar Usuario"**
3. Completar:
   - **Usuario**: Nombre de usuario único
   - **Contraseña**: Contraseña segura
   - **Nombre Completo**: Nombre real del empleado
   - **Rol**: Mesero o Cocinero
4. Hacer clic en **"Crear Usuario"**

⚠️ **Importante**: Solo el administrador puede crear cuentas de meseros y cocineros.

### Cierre de Caja Diario

#### Proceso de Cierre
1. Al final del día, ir a **Dashboard** → **"Ir a Cierre"**
2. El sistema muestra:
   - **Total de ventas del día** (calculado automáticamente)
   - **Campo para efectivo en caja** (ingresar manualmente)
3. Ingresar el monto real de efectivo contado
4. Hacer clic en **"Registrar Cierre"**

#### Interpretación de Resultados
- **Balance perfecto**: Efectivo = Ventas (diferencia = 0)
- **Sobrante**: Efectivo > Ventas (diferencia positiva)
- **Faltante**: Efectivo < Ventas (diferencia negativa)

#### Generar Reporte PDF
1. Después del cierre, hacer clic en **"Generar Reporte PDF"**
2. El reporte incluye:
   - Resumen de ventas
   - Detalle de productos vendidos
   - Balance de caja
   - Diferencias encontradas

### Reportes de Ventas

#### Reporte Semanal
1. Ir a **Reportes**
2. Seleccionar **"Reporte Semanal"**
3. Elegir la semana deseada
4. El reporte muestra:
   - Producto más vendido de la semana
   - Día con más ventas

#### Reporte Mensual
1. Ir a **Reportes**
2. Seleccionar **"Reporte Mensual"**
3. Elegir el mes deseado
4. El reporte muestra:
   - Producto más vendido del mes
   - Día de la semana con más actividad

## Rol: Mesero/Cajero

### Dashboard de Mesero
Al iniciar sesión, verás:
- **Órdenes activas**: Todas las órdenes en proceso
- **Estados de órdenes**: Código de colores para cada estado
- **Botón "Nueva Orden"**: Para crear órdenes nuevas

### Tomar Pedidos

#### Crear Nueva Orden
1. Hacer clic en **"Nueva Orden"** o **"Tomar Orden"**
2. Completar datos del cliente (opcional):
   - **Nombre del cliente**
   - **Teléfono** (opcional)

#### Agregar Productos a la Orden

El proceso varía ligeramente dependiendo de la categoría del producto.

**Para Bebidas y productos simples:**
1.  En el menú, haz clic en el botón **"+"** junto a la bebida.
2.  Se abrirá una ventana para que definas la **cantidad** y **notas**.
3.  Haz clic en **"Agregar a Orden"**.

**Para productos Principales (con Variantes):**
1.  En el menú, haz clic en el botón **"+"** junto al producto principal (ej. "Tacos de Res").
2.  Aparecerá una primera ventana para **seleccionar la variante** que el cliente desea (ej. "Unidad" o "Porción de 3").
3.  Tras seleccionar la variante, aparecerá la segunda ventana para definir la **cantidad**, agregar **extras** y **notas especiales**.
4.  El stock disponible se calculará automáticamente basado en el consumo de la variante seleccionada.
5.  Haz clic en **"Agregar a Orden"** para añadirlo al pedido.

#### Finalizar Orden
1. Revisar todos los productos en el resumen
2. Verificar el total
3. Hacer clic en **"Crear Orden"**

### Gestionar Órdenes

#### Estados de Órdenes
- **Pendiente** (azul): Orden creada, no enviada a cocina
- **Enviada a Cocina** (amarillo): En cola de preparación
- **En Preparación** (celeste): Cocinero trabajando en la orden
- **Lista** (verde): Orden terminada, lista para entrega

#### Enviar Orden a Cocina
1. Abrir la orden desde el dashboard
2. Revisar todos los productos
3. Hacer clic en **"Mandar a Cocina"**

⚠️ **Importante**: Una vez enviada a cocina, no se puede modificar la orden.

#### Cancelar Orden
1. Solo se pueden cancelar órdenes **pendientes** o **enviadas a cocina**
2. Abrir la orden
3. Hacer clic en **"Anular Pedido"**
4. Confirmar la cancelación

#### Agregar Productos a Orden Activa
1. Buscar la orden en el dashboard
2. Hacer clic en **"Ver Detalles"**
3. Si está en estado **pendiente**, se puede modificar
4. Agregar nuevos productos siguiendo el proceso normal

#### Ver Detalles y Generar Recibos
1.  Desde el **Dashboard de Mesero**, puedes hacer clic en cualquier orden para ver sus detalles.
2.  En la página de detalles, verás toda la información de la orden, incluyendo cliente, mesero, y todos los productos.
3.  Si una orden ya ha sido **pagada**, en esta misma pantalla de detalles encontrarás un botón de **"Generar Recibo PDF"**, que te permitirá descargar o imprimir un comprobante en cualquier momento.

#### Cuando la Orden está Lista
1. La orden aparecerá con estado **"Lista"** (verde)
2. Hacer clic en **"Procesar Pago"**

#### Proceso de Cobro
1. El sistema muestra el **total de la orden**
2. Ingresar el **monto de efectivo recibido**
3. El sistema calcula automáticamente el **cambio**
4. Hacer clic en **"Procesar Pago"**

#### Comprobante de Pago
- Inmediatamente después de procesar un pago, el sistema te mostrará una pantalla de "Pago Exitoso" con el resumen del recibo.
- Desde aquí, puedes usar el botón **"Generar PDF"** para obtener el comprobante.
- Si necesitas reimprimir el recibo más tarde, siempre puedes buscar la orden pagada en tu historial y generar el PDF desde la pantalla de detalles.

## Rol: Cocinero

### Dashboard de Cocina
Al iniciar sesión verás:
- **Órdenes pendientes**: Solo órdenes enviadas por meseros
- **Orden de llegada**: Las órdenes se muestran por orden cronológico
- **Contador de órdenes**: Número total de órdenes pendientes

### Gestión de Órdenes

#### Información de Cada Orden
- **Número de orden**: Identificador único
- **Nombre del cliente**: Para identificar la orden
- **Hora de creación**: Cuándo se tomó la orden
- **Lista de productos**: Con cantidades, extras y notas especiales

#### Estados de Preparación

**Orden Nueva** (amarillo)
1. Hacer clic en **"Iniciar Preparación"**
2. La orden cambia a estado **"En Preparación"**

**En Preparación** (celeste)
1. Cuando termines de cocinar, hacer clic en **"Marcar como Listo"**
2. La orden desaparece de tu pantalla
3. Los meseros reciben notificación automática

### Consulta de Stock
1. Ir a **"Stock"** en la navegación
2. Ver todos los productos disponibles
3. Verificar cantidades antes de confirmar órdenes

⚠️ **Importante**: Si no hay suficiente stock de un producto, contactar al administrador.

## Notificaciones en Tiempo Real

### Para Cocineros
- **Nueva orden**: Notificación automática cuando llega una orden
- **Sonido de alerta**: (Si está habilitado en el navegador)

### Para Meseros
- **Orden lista**: Notificación cuando el cocinero termina una orden
- **Actualización automática**: El dashboard se actualiza solo

## Consejos de Uso

### Mejores Prácticas

#### Para Administradores
- Realizar cierre de caja diariamente
- Revisar stock bajo semanalmente
- Generar reportes mensualmente para análisis
- Mantener respaldos de la base de datos

#### Para Meseros
- Verificar stock antes de tomar órdenes grandes
- Confirmar detalles con el cliente antes de enviar a cocina
- Procesar pagos inmediatamente cuando las órdenes estén listas
- Mantener órdenes organizadas por mesa/cliente

#### Para Cocineros
- Revisar extras y notas especiales cuidadosamente
- Marcar órdenes como "en preparación" al comenzar
- Comunicar problemas de stock inmediatamente
- Seguir el orden cronológico de las órdenes

### Solución de Problemas Comunes

#### "No puedo ver las órdenes nuevas"
- Verificar conexión a internet
- Refrescar la página (F5)
- Cerrar sesión y volver a entrar

#### "El stock no se actualiza"
- Solo el administrador puede actualizar stock manualmente
- El stock se reduce automáticamente al enviar órdenes a cocina

#### "No puedo procesar el pago"
- Verificar que la orden esté en estado "Lista"
- Asegurar que el monto ingresado sea mayor o igual al total

#### "La orden desapareció"
- Verificar en qué estado estaba la orden
- Las órdenes pagadas o canceladas no aparecen en órdenes activas

### Atajos de Teclado
- **Ctrl + Enter**: Enviar formulario activo
- **Escape**: Cerrar ventanas emergentes
- **F5**: Refrescar página

## Seguridad

### Buenas Prácticas
- **Cerrar sesión** al terminar el turno
- **No compartir** credenciales de usuario
- **Cambiar contraseñas** periódicamente
- **Reportar** actividad sospechosa al administrador

### Respaldo de Datos
- El sistema guarda automáticamente todos los datos
- Los reportes PDF se pueden descargar como respaldo
- Contactar al administrador para respaldos completos

## Soporte Técnico

### Información del Sistema
- **Versión**: 1.0
- **Navegadores compatibles**: Chrome, Firefox, Safari, Edge
- **Dispositivos**: Computadoras, tablets, smartphones

### Contacto
Para problemas técnicos o dudas sobre el sistema, contactar al administrador del restaurante.
