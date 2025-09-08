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
- **Contraseña**: La que hayas configurado en tus variables de entorno para `DEFAULT_ADMIN_PASSWORD`.

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

Ahora, la gestión de productos se divide en cuatro categorías: "Principal" (productos base), "Bebida", "Extra" y "Combo".

#### Agregar Productos Simples (Bebidas y Extras)
1. Ir a **Menú** en la navegación.
2. Hacer clic en **"Agregar Producto"**.
3. Seleccionar la **Categoría** "Bebida" o "Extra".
4. Completar el resto del formulario (Nombre, Precio, Stock).
5. Hacer clic en **"Agregar"**.

#### Agregar Productos con Variantes (Categoría Principal)

Este es un proceso de dos pasos: primero creas el "Producto Base" y luego le añades sus "Variantes" vendibles.

**Paso 1: Crear el Producto Base**
1.  Ir a **Menú** y hacer clic en **"Agregar Producto"**.
2.  Seleccionar la **Categoría** "Principal (Producto Base)". El campo de precio se ocultará.
3.  **Nombre**: Escribe el nombre general del producto (ej. "Tacos de Res").
4.  **Stock Inicial**: Ingresa la cantidad total de unidades que se pueden preparar (ej. si puedes hacer 15 tacos, ingresa 15).
5.  Hacer clic en **"Agregar"**.

**Paso 2: Añadir Variantes al Producto Base**
1.  Busca el producto base que acabas de crear.
2.  Haz clic en el botón verde **"+ Agregar Variante"**.
3.  Completa el formulario:
    *   **Nombre de la Variante**: El formato de venta (ej. "Unidad" o "Porción de 3").
    *   **Precio**: El precio de venta para *esta* variante.
    *   **Consumo de Stock**: ¿Cuántas unidades del stock base consume esta variante? (ej. "Unidad" consume `1`, "Porción de 3" consume `3`).
4.  Haz clic en **"Agregar Variante"**.

#### Agregar Combos (Paquetes de Productos)

Esta función te permite vender un paquete de varios productos a un precio fijo, y el sistema descontará el stock de cada componente automáticamente.

1.  Ir a **Menú** y hacer clic en **"Agregar Producto"**.
2.  Seleccionar la **Categoría** "Combo (Paquete de productos)".
3.  **Nombre**: Escribe el nombre del combo (ej. "Combo Hamburguesa con Papas").
4.  **Precio**: Ingresa el precio final de venta del combo.
5.  **Componentes del Combo**: Aparecerá una nueva sección.
    *   Haz clic en **"Agregar Componente"**.
    *   En la fila que aparece, selecciona un producto existente (ej. "Hamburguesa Simple") y la cantidad que incluye el combo (ej. `1`).
    *   Repite el proceso para todos los componentes (ej. agrega "Papas Fritas" con cantidad `1`).
6.  Haz clic en **"Agregar"**. El combo aparecerá en la lista, mostrando los componentes que lo conforman.

#### Editar Productos
1. En la página de Menú, buscar el producto
2. Hacer clic en el ícono de editar (lápiz)
3. Modificar los datos necesarios
4. Hacer clic en **"Actualizar"**

#### Editar una Variante
1. En la página de Menú, busca el producto principal que contiene la variante.
2. Al lado del nombre de la variante que deseas modificar, haz clic en el ícono de editar (lápiz).
3. Se abrirá una ventana emergente con los datos de la variante.
4. Modifica el nombre, el precio o el consumo de stock.
5. Haz clic en **"Actualizar Variante"** para guardar los cambios.

#### Eliminar Productos
1. Buscar el producto en la lista
2. Hacer clic en el ícono de eliminar (basura)
3. Confirmar la eliminación

#### Eliminar una Variante
1. En la página de Menú, busca el producto principal que contiene la variante.
2. Al lado del nombre de la variante que deseas eliminar, haz clic en el ícono de eliminar (basura).
3. Confirma la eliminación. La variante desaparecerá, pero el producto base permanecerá.


⚠️ **Nota**: Los productos eliminados se marcan como inactivos, no se borran permanentemente.

### Gestión de Stock

#### Actualizar Stock
1. Ir a **Menú**
2. Editar el producto que necesita actualización de stock
3. Cambiar el valor en el campo **"Stock"**
4. Guardar cambios

#### Monitoreo de Stock Bajo
- El dashboard muestra automáticamente productos con stock ≤ 5 unidades

### Gestión de Usuarios

#### Crear Usuarios
1. Ir a **Usuarios** en la navegación
2. Hacer clic en **"Agregar Usuario"**
3. Completar el formulario.
4. Hacer clic en **"Crear Usuario"**

### Cierre de Caja Diario

#### Proceso de Cierre
1. Al final del día, ir a **Dashboard** → **"Ir a Cierre"**
2. Ingresar el monto real de efectivo contado
3. Hacer clic en **"Registrar Cierre"**

#### Generar Reporte PDF
1. Después del cierre, hacer clic en **"Generar Reporte PDF"**

### Reportes de Ventas
- Permite generar reportes de ventas semanales o mensuales.

## Rol: Mesero/Cajero

### Dashboard de Mesero
- Muestra órdenes activas y completadas.

### Tomar Pedidos
- Permite crear nuevas órdenes, agregar productos (simples, variantes o combos) y extras.
- El sistema valida el stock disponible antes de crear la orden.

### Gestionar Órdenes
- **Enviar a Cocina**: Notifica a la cocina de una nueva orden.
- **Cancelar Orden**: Anula una orden y restaura el stock descontado.
- **Procesar Pago**: Registra el pago, calcula el cambio y marca la orden como completada.
- **Generar Recibo**: Permite imprimir un comprobante en PDF en cualquier momento para órdenes pagadas.

## Rol: Cocinero

### Dashboard de Cocina
- Muestra en tiempo real las órdenes pendientes de preparar.

### Gestión de Órdenes
- **Iniciar Preparación**: Cambia el estado de la orden para notificar a los meseros.
- **Marcar como Listo**: Notifica a los meseros que la orden está lista para ser entregada.

### Consulta de Stock
- Permite ver el stock actual de los productos.

## Notificaciones en Tiempo Real
- El sistema usa WebSockets para notificar a todos los roles sobre cambios importantes (nuevas órdenes, órdenes listas, etc.) sin necesidad de recargar la página.