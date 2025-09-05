from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Product, Order, OrderItem, DailyReport, ComboItem
from app.services.report_service import generate_daily_report_pdf, generate_sales_report_pdf
from app import db, socketio
from datetime import datetime, date, timedelta, time
from werkzeug.security import generate_password_hash
import bleach
from functools import wraps
from sqlalchemy.orm import aliased
from zoneinfo import ZoneInfo
import logging

admin_bp = Blueprint('admin', __name__)

# Define the timezone for Guatemala
guatemala_tz = ZoneInfo('America/Guatemala')

def get_current_gt_datetime():
    """Returns the current datetime in Guatemala timezone."""
    return datetime.now(guatemala_tz)

def get_day_range_utc(start_date_local):
    """
    Takes a local date and returns a tuple of two UTC datetime objects
    representing the start and end of that day.
    """
    start_of_day_local = datetime.combine(start_date_local, time.min, tzinfo=guatemala_tz)
    end_of_day_local = datetime.combine(start_date_local, time.max, tzinfo=guatemala_tz)
    
    # Convert to UTC for database queries
    start_of_day_utc = start_of_day_local.astimezone(ZoneInfo('UTC'))
    end_of_day_utc = end_of_day_local.astimezone(ZoneInfo('UTC'))
    
    return start_of_day_utc, end_of_day_utc

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acceso denegado. Solo administradores.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    today_local = get_current_gt_datetime().date()
    start_of_day_utc, end_of_day_utc = get_day_range_utc(today_local)

    today_orders = Order.query.filter(
        Order.created_at.between(start_of_day_utc, end_of_day_utc),
        Order.status == 'paid'
    ).count()
    
    today_sales = db.session.query(db.func.sum(Order.total)).filter(
        Order.created_at.between(start_of_day_utc, end_of_day_utc),
        Order.status == 'paid'
    ).scalar() or 0
    
    low_stock_products = Product.query.filter(Product.parent_id.is_(None), Product.stock <= 5, Product.is_active == True).all()
    
    return render_template('admin/dashboard.html', 
                         today_orders=today_orders,
                         today_sales=today_sales,
                         low_stock_products=low_stock_products)

@admin_bp.route('/menu')
@login_required
@admin_required
def menu():
    products = Product.query.filter(Product.parent_id.is_(None), Product.is_active==True).order_by(Product.category, Product.name).all()
    component_products_query = Product.query.filter(Product.category.in_(['Principal', 'Bebida']), Product.parent_id.is_(None), Product.is_active==True).order_by(Product.name).all()
    component_products = [p.to_dict() for p in component_products_query]
    return render_template('admin/menu.html', products=products, component_products=component_products)

@admin_bp.route('/add_product', methods=['POST'])
@login_required
@admin_required
def add_product():
    try:
        category = bleach.clean(request.form.get('category', '').strip())
        name = bleach.clean(request.form.get('name', '').strip())
        price_str = request.form.get('price', '0')
        stock_str = request.form.get('stock', '0')

        if not name or not category:
            flash('Nombre y categoría son requeridos.', 'error')
            return redirect(url_for('admin.menu'))

        product = Product(name=name, category=category)

        if category == 'Combo':
            price = float(price_str)
            if price <= 0:
                flash('El precio para un combo debe ser mayor a cero.', 'error')
                return redirect(url_for('admin.menu'))
            product.price = price
            product.stock = 999 # Combos don't have their own physical stock
            
            db.session.add(product)
            db.session.flush() # Flush to get the product ID

            component_ids = request.form.getlist('component_ids[]')
            component_quantities = request.form.getlist('component_quantities[]')

            if not component_ids:
                raise Exception("Un combo debe tener al menos un componente.")

            for i in range(len(component_ids)):
                comp_id = int(component_ids[i])
                quantity = int(component_quantities[i])
                if quantity > 0:
                    combo_item = ComboItem(combo_product_id=product.id, component_product_id=comp_id, quantity=quantity)
                    db.session.add(combo_item)
            flash_message = 'Combo agregado exitosamente.'

        elif category == 'Principal':
            product.price = None
            product.stock = int(stock_str)
            flash_message = 'Producto base agregado exitosamente.'
            db.session.add(product)

        else: # Bebida, Extra
            price = float(price_str)
            if price <= 0:
                flash('El precio debe ser mayor a cero.', 'error')
                return redirect(url_for('admin.menu'))
            product.price = price
            product.stock = int(stock_str)
            flash_message = 'Producto agregado exitosamente.'
            db.session.add(product)

        db.session.commit()
        flash(flash_message, 'success')

    except ValueError:
        flash('Error en los datos numéricos de precio o stock.', 'error')
        db.session.rollback()
    except Exception as e:
        flash(f'Error al agregar producto: {e}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.menu'))


@admin_bp.route('/edit_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        name = bleach.clean(request.form.get('name', '').strip())
        if not name:
            flash('El nombre es un campo requerido.', 'error')
            return redirect(url_for('admin.menu'))
        product.name = name

        if product.category == 'Combo':
            product.price = float(request.form.get('price', '0'))
            # Clear old components
            ComboItem.query.filter_by(combo_product_id=product.id).delete()
            # Add new components
            component_ids = request.form.getlist('component_ids[]')
            component_quantities = request.form.getlist('component_quantities[]')
            if not component_ids:
                raise Exception("Un combo debe tener al menos un componente.")
            for i in range(len(component_ids)):
                comp_id = int(component_ids[i])
                quantity = int(component_quantities[i])
                if quantity > 0:
                    combo_item = ComboItem(combo_product_id=product.id, component_product_id=comp_id, quantity=quantity)
                    db.session.add(combo_item)

        elif not product.is_base_product: # Is a Variant
            product.price = float(request.form.get('price', '0'))
            product.stock_consumption = int(request.form.get('stock_consumption', '1'))
        else: # Is a Base or Simple Product
            product.stock = int(request.form.get('stock', '0'))
            if product.category != 'Principal':
                product.price = float(request.form.get('price', '0'))

        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')

    except ValueError:
        flash('Error en los datos numéricos.', 'error')
        db.session.rollback()
    except Exception as e:
        flash(f'Error al actualizar producto: {e}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.menu'))

# --- Other routes remain the same ---

@admin_bp.route('/add_variant/<int:parent_id>', methods=['POST'])
@login_required
@admin_required
def add_variant(parent_id):
    parent_product = Product.query.get_or_404(parent_id)
    name = bleach.clean(request.form.get('variant_name', '').strip())
    price_str = request.form.get('variant_price', '0')
    consumption_str = request.form.get('variant_consumption', '1')
    try:
        price = float(price_str)
        stock_consumption = int(consumption_str)
        if not name or price <= 0 or stock_consumption <= 0:
            flash('Datos de variante inválidos.', 'error')
            return redirect(url_for('admin.menu'))
        variant = Product(
            name=name,
            price=price,
            category=parent_product.category,
            stock=0, # Variants don't have their own stock
            parent_id=parent_product.id,
            stock_consumption=stock_consumption
        )
        db.session.add(variant)
        db.session.commit()
        flash('Variante agregada exitosamente.', 'success')
    except ValueError:
        flash('Error en los datos numéricos de la variante.', 'error')
    except Exception as e:
        flash(f'Error al agregar variante: {e}', 'error')
        db.session.rollback()
    return redirect(url_for('admin.menu'))

@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('admin.menu'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(is_active=True).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = bleach.clean(request.form.get('username', '').strip())
    password = request.form.get('password', '')
    role = bleach.clean(request.form.get('role', '').strip())
    full_name = bleach.clean(request.form.get('full_name', '').strip())
    if not username or not password or role not in ['waiter', 'cook'] or not full_name:
        flash('Todos los campos son requeridos y el rol debe ser válido.', 'error')
        return redirect(url_for('admin.users'))
    if User.query.filter_by(username=username).first():
        flash('El nombre de usuario ya existe.', 'error')
        return redirect(url_for('admin.users'))
    try:
        user = User(username=username, password_hash=generate_password_hash(password), role=role, full_name=full_name)
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
    except Exception as e:
        flash('Error al crear usuario.', 'error')
        db.session.rollback()
    return redirect(url_for('admin.users'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    logging.warning("--- ENTERING REPORTS ROUTE ---")
    period = request.args.get('period', 'monthly')
    today_local = get_current_gt_datetime().date()
    logging.warning(f"[REPORTS] Today in GT Timezone: {today_local}")

    if period == 'weekly':
        start_date_local = today_local - timedelta(days=today_local.weekday())
        end_date_local = start_date_local + timedelta(days=6)
        period_label = f"Semana del {start_date_local.strftime('%d/%m')} al {end_date_local.strftime('%d/%m')}"
    else:  # monthly
        start_date_local = today_local.replace(day=1)
        next_month = start_date_local.replace(day=28) + timedelta(days=4)
        end_date_local = next_month - timedelta(days=next_month.day)
        period_label = f"Mes de {start_date_local.strftime('%B de %Y')}"

    start_range_utc, end_range_utc = get_day_range_utc(start_date_local)[0], get_day_range_utc(end_date_local)[1]
    logging.warning(f"[REPORTS] Querying for UTC range: {start_range_utc} to {end_range_utc}")

    # --- Correctly query and build report_data ---
    total_sales_query = db.session.query(db.func.sum(Order.total)).filter(Order.status == 'paid', Order.created_at.between(start_range_utc, end_range_utc)).scalar() or 0
    total_orders_query = db.session.query(db.func.count(Order.id)).filter(Order.status == 'paid', Order.created_at.between(start_range_utc, end_range_utc)).scalar() or 0

    top_products_query = db.session.query(
        Product.name,
        db.func.sum(OrderItem.quantity).label('total_quantity')
    ).join(OrderItem, OrderItem.product_id == Product.id)\
     .join(Order, Order.id == OrderItem.order_id)\
     .filter(Order.status == 'paid', Order.created_at.between(start_range_utc, end_range_utc))\
     .group_by(Product.name).order_by(db.desc('total_quantity')).limit(5).all()

    grouping_expression = db.func.date_trunc('day', Order.created_at.op('AT TIME ZONE')('America/Guatemala'))
    top_day_query = db.session.query(
        grouping_expression.label('sale_day'),
        db.func.sum(Order.total).label('total_sales')
    ).filter(
        Order.status == 'paid',
        Order.created_at.between(start_range_utc, end_range_utc)
    ).group_by(grouping_expression).order_by(db.desc('total_sales')).first()
    logging.warning(f"[REPORTS] Top day query result: {top_day_query}")

    dia_mas_ventas_str = "N/A"
    if top_day_query and top_day_query.sale_day:
        # Convert the UTC date from the database back to local GT time for display
        sale_day_local = top_day_query.sale_day.astimezone(guatemala_tz)
        dia_mas_ventas_str = f"{sale_day_local.strftime('%A, %d de %B')} (Total: Q{top_day_query.total_sales:.2f})"

    logging.warning(f"[REPORTS] Final 'dia_mas_ventas_str': {dia_mas_ventas_str}")

    report_data = {
        'period_label': period_label,
        'total_sales': total_sales_query,
        'total_orders': total_orders_query,
        'top_selling_products': top_products_query,
        'dia_mas_ventas': dia_mas_ventas_str
    }
    # --- End of report_data section ---

    if request.args.get('download') == 'pdf':
        return generate_sales_report_pdf(report_data, period)

    return render_template('admin/reports.html', report_data=report_data, period=period)


@admin_bp.route('/daily_close', methods=['GET', 'POST'])
@login_required
@admin_required
def daily_close():
    logging.warning("--- ENTERING DAILY CLOSE ROUTE ---")
    today_local = get_current_gt_datetime().date()
    start_of_day_utc, end_of_day_utc = get_day_range_utc(today_local)
    today_date_str = today_local.strftime('%A, %d de %B de %Y')
    logging.warning(f"[DAILY_CLOSE] Today is {today_local}. UTC range: {start_of_day_utc} to {end_of_day_utc}")

    # --- Initialize variables for GET request ---
    total_sales = 0
    orders_data = []

    if request.method == 'POST':
        logging.warning("[DAILY_CLOSE] POST request received.")
        cash_in_register = request.form.get('cash_in_register', 0)
        try:
            cash_in_register = float(cash_in_register)
            total_sales = db.session.query(db.func.sum(Order.total)).filter(
                Order.created_at.between(start_of_day_utc, end_of_day_utc),
                Order.status == 'paid'
            ).scalar() or 0
            logging.warning(f"[DAILY_CLOSE] Calculated total_sales in POST: {total_sales}")
            
            daily_report = DailyReport.query.filter_by(date=today_local).first()
            if not daily_report:
                daily_report = DailyReport(date=today_local)
                db.session.add(daily_report)
            
            daily_report.total_sales = total_sales
            daily_report.cash_in_register = cash_in_register
            daily_report.difference = cash_in_register - total_sales
            daily_report.closed_at = get_current_gt_datetime()
            
            db.session.commit()
            flash('Cierre de caja actualizado exitosamente.', 'success')
            logging.warning(f"[DAILY_CLOSE] Daily report for {today_local} updated.")
            return redirect(url_for('admin.daily_close'))

        except Exception as e:
            logging.error(f"[DAILY_CLOSE] Error in POST: {e}")
            flash('Error al procesar el cierre de caja.', 'error')
            db.session.rollback()

    # --- Logic for GET request ---
    daily_report = DailyReport.query.filter_by(date=today_local).first()
    if daily_report:
        logging.warning(f"[DAILY_CLOSE] Found existing daily_report for {today_local} with total sales: {daily_report.total_sales}")
        total_sales = daily_report.total_sales
    else:
        # If no report, calculate sales for the day so far
        logging.warning(f"[DAILY_CLOSE] No daily_report found for {today_local}. Calculating current sales.")
        total_sales = db.session.query(db.func.sum(Order.total)).filter(
            Order.created_at.between(start_of_day_utc, end_of_day_utc),
            Order.status == 'paid'
        ).scalar() or 0

    # Fetch orders for display
    orders = Order.query.filter(
        Order.created_at.between(start_of_day_utc, end_of_day_utc),
        Order.status.in_(['paid', 'cancelled'])
    ).order_by(Order.created_at.desc()).all()
    orders_data = [{'order': order.to_dict(), 'waiter_name': order.waiter.full_name if order.waiter else 'N/A'} for order in orders]

    if 'download' in request.args and request.args.get('download') == 'pdf':
        logging.warning("[DAILY_CLOSE] PDF download requested.")
        
        # Use today's date for the PDF if no report is closed yet
        report_date_for_pdf = daily_report.date if daily_report else today_local
        logging.warning(f"[DAILY_CLOSE] PDF generation for date: {report_date_for_pdf}")
        
        start_pdf_utc, end_pdf_utc = get_day_range_utc(report_date_for_pdf)

        pdf_orders = Order.query.filter(
            Order.created_at.between(start_pdf_utc, end_pdf_utc),
            Order.status.in_(['paid', 'cancelled'])
        ).order_by(Order.created_at.asc()).all()

        pdf_orders_data = []
        for order in pdf_orders:
            items_str = ", ".join([f"{item.quantity}x {item.product.name}" for item in order.items])
            order_local_time = order.created_at.astimezone(guatemala_tz)
            pdf_orders_data.append({
                'id': order.id,
                'time': order_local_time.strftime('%H:%M:%S'),
                'total': f"Q{order.total:.2f}",
                'status': order.status,
                'items': items_str
            })
        
        # Use calculated total_sales for the PDF, not necessarily from a saved report
        final_total_sales = db.session.query(db.func.sum(Order.total)).filter(
            Order.created_at.between(start_pdf_utc, end_pdf_utc),
            Order.status == 'paid'
        ).scalar() or 0

        context = {
            'daily_report': daily_report, # Can be None
            'total_sales': final_total_sales,
            'report_date_str': report_date_for_pdf.strftime('%A, %d de %B de %Y'),
            'orders_data': pdf_orders_data
        }
        
        return generate_daily_report_pdf(context)

    return render_template('admin/daily_close.html', total_sales=total_sales, daily_report=daily_report, today_date=today_date_str, orders_data=orders_data)

