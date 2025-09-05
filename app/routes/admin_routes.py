from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Product, Order, OrderItem, DailyReport, ComboItem
from app.services.report_service import generate_daily_report_pdf, generate_sales_report_pdf
from app import db, socketio
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
import bleach
from functools import wraps
from sqlalchemy.orm import aliased
from zoneinfo import ZoneInfo

admin_bp = Blueprint('admin', __name__)

# Define the timezone for Guatemala
guatemala_tz = ZoneInfo('America/Guatemala')

def get_current_gt_date():
    """Returns the current date in Guatemala timezone."""
    return datetime.now(guatemala_tz).date()

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
    today = get_current_gt_date()
    today_orders = Order.query.filter(
        db.func.date(db.func.timezone('America/Guatemala', Order.created_at)) == today,
        Order.status == 'paid'
    ).count()
    today_sales = db.session.query(db.func.sum(Order.total)).filter(
        db.func.date(db.func.timezone('America/Guatemala', Order.created_at)) == today,
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
    period = request.args.get('period', 'monthly')
    today = get_current_gt_date()
    if period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        period_label = f"Semana del {start_date.strftime('%d/%m')} al {end_date.strftime('%d/%m')}"
    else:
        start_date = today.replace(day=1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        period_label = f"Mes de {start_date.strftime('%B de %Y')}"
    sales_subquery = (db.session.query(OrderItem.product_id, (OrderItem.quantity * Product.stock_consumption).label('total_consumption')).join(Product, Product.id == OrderItem.product_id).join(Order, Order.id == OrderItem.order_id).filter(Order.status == 'paid', db.func.date(db.func.timezone('America/Guatemala', Order.created_at)).between(start_date, end_date)).subquery())
    ParentProduct = aliased(Product)
    grouping_name = db.case((Product.parent_id.isnot(None), ParentProduct.name), else_=Product.name).label('base_product_name')
    top_product_query = (db.session.query(grouping_name, db.func.sum(sales_subquery.c.total_consumption).label('total_grouped_quantity')).join(Product, Product.id == sales_subquery.c.product_id).outerjoin(ParentProduct, Product.parent_id == ParentProduct.id).group_by(grouping_name).order_by(db.desc('total_grouped_quantity')).first())
    product_display_name = "N/A"
    if top_product_query:
        total_sold = int(top_product_query.total_grouped_quantity)
        product_display_name = f"{top_product_query.base_product_name} (Cantidad: {total_sold})"
    top_day_query = db.session.query(db.func.date(db.func.timezone('America/Guatemala', Order.created_at)).label('sale_day'), db.func.sum(Order.total).label('total_sales')).filter(Order.status == 'paid', db.func.date(db.func.timezone('America/Guatemala', Order.created_at)).between(start_date, end_date)).group_by('sale_day').order_by(db.desc('total_sales')).first()
    dia_mas_ventas_str = "N/A"
    if top_day_query:
        sale_day = top_day_query[0]
        if isinstance(sale_day, str):
            sale_day_obj = datetime.strptime(sale_day, '%Y-%m-%d').date()
        else:
            sale_day_obj = sale_day
        dia_mas_ventas_str = f"{sale_day_obj.strftime('%A, %d de %B')} (Total: Q{top_day_query[1]:.2f})"
    report_data = {"periodo": period_label, "producto_mas_vendido": product_display_name, "dia_mas_ventas": dia_mas_ventas_str}
    if 'download' in request.args:
        pdf_buffer = generate_sales_report_pdf(report_data, period)
        return pdf_buffer, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': f'inline; filename=reporte_{period}_{today.strftime("%Y-%m-%d")}.pdf'}
    return render_template('admin/reports.html', report_data=report_data, period=period)

@admin_bp.route('/daily_close', methods=['GET', 'POST'])
@login_required
@admin_required
def daily_close():
    today = get_current_gt_date()
    if request.method == 'POST':
        cash_in_register = request.form.get('cash_in_register', 0)
        try:
            cash_in_register = float(cash_in_register)
            total_sales = db.session.query(db.func.sum(Order.total)).filter(db.func.date(db.func.timezone('America/Guatemala', Order.created_at)) == today, Order.status == 'paid').scalar() or 0
            difference = cash_in_register - total_sales
            daily_report = DailyReport.query.filter_by(date=today).first()
            if daily_report:
                daily_report.total_sales = total_sales
                daily_report.cash_in_register = cash_in_register
                daily_report.difference = difference
            else:
                daily_report = DailyReport(date=today, total_sales=total_sales, cash_in_register=cash_in_register, difference=difference)
                db.session.add(daily_report)
            db.session.commit()
            flash('Cierre diario registrado exitosamente.', 'success')
        except ValueError:
            flash('Monto inválido.', 'error')
        except Exception as e:
            flash('Error al registrar cierre.', 'error')
            db.session.rollback()
    total_sales = db.session.query(db.func.sum(Order.total)).filter(db.func.date(db.func.timezone('America/Guatemala', Order.created_at)) == today, Order.status == 'paid').scalar() or 0
    daily_report = DailyReport.query.filter_by(date=today).first()
    ParentProduct = aliased(Product)
    orders_query = (db.session.query(Product.name.label('variant_name'), ParentProduct.name.label('base_name'), OrderItem.quantity.label('quantity'), OrderItem.unit_price.label('unit_price'), (OrderItem.quantity * OrderItem.unit_price).label('total')).join(OrderItem, OrderItem.product_id == Product.id).outerjoin(ParentProduct, Product.parent_id == ParentProduct.id).join(Order, Order.id == OrderItem.order_id).filter(db.func.date(db.func.timezone('America/Guatemala', Order.created_at)) == today, Order.status == 'paid').all())
    orders_data = []
    for row in orders_query:
        product_display_name = row.variant_name
        if row.base_name:
            product_display_name = f"{row.base_name} ({row.variant_name})"
        orders_data.append({'product_name': product_display_name, 'quantity': row.quantity, 'unit_price': row.unit_price, 'total': row.total})
    if 'download' in request.args and request.args.get('download') == 'pdf':
        if not daily_report:
            flash('No hay un cierre diario registrado para hoy. Registre el cierre primero.', 'error')
            return redirect(url_for('admin.daily_close'))
        pdf_buffer = generate_daily_report_pdf(daily_report, orders_data)
        headers = {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'inline; filename=reporte_diario_{today.strftime("%Y-%m-%d")}.pdf',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        return pdf_buffer, 200, headers
    today_date = today.strftime('%d/%m/%Y')
    return render_template('admin/daily_close.html', total_sales=total_sales, daily_report=daily_report, today_date=today_date, orders_data=orders_data)
