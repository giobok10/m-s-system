from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Product, Order, OrderItem
from app import db, socketio
from datetime import datetime, date
import bleach
import json
from functools import wraps
from app.services.report_service import generate_receipt_pdf

waiter_bp = Blueprint('waiter', __name__)

def waiter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'waiter':
            flash('Acceso denegado. Solo meseros.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@waiter_bp.route('/dashboard')
@login_required
@waiter_required
def dashboard():
    view_mode = request.args.get('view', 'mine')
    today = date.today()

    # Base query for active orders
    active_orders_query = Order.query.filter(
        Order.status.in_(['pending', 'sent_to_kitchen', 'in_preparation', 'ready'])
    )

    # Base query for completed orders (today only)
    completed_orders_query = Order.query.filter(
        Order.status == 'paid',
        db.func.date(Order.created_at) == today
    )

    if view_mode == 'mine':
        active_orders_query = active_orders_query.filter(Order.waiter_id == current_user.id)
        completed_orders_query = completed_orders_query.filter(Order.waiter_id == current_user.id)

    active_orders = active_orders_query.order_by(Order.created_at.desc()).all()
    completed_orders = completed_orders_query.order_by(Order.created_at.desc()).all()

    return render_template('waiter/dashboard.html',
                         active_orders=active_orders,
                         completed_orders=completed_orders,
                         view_mode=view_mode)

@waiter_bp.route('/take_order')
@login_required
@waiter_required
def take_order():
    # Fetch products that are directly sellable
    products = Product.query.filter(
        Product.parent_id.is_(None), 
        Product.is_active==True, 
        Product.category != 'Extra'
    ).order_by(Product.category, Product.name).all()
    
    extras = Product.query.filter_by(is_active=True, category='Extra').order_by(Product.name).all()
    return render_template('waiter/take_order.html', products=products, extras=extras)

@waiter_bp.route('/create_order', methods=['POST'])
@login_required
@waiter_required
def create_order():
    customer_name = bleach.clean(request.form.get('customer_name', '').strip())
    customer_phone = bleach.clean(request.form.get('customer_phone', '').strip())
    
    try:
        items_data = request.form.getlist('items')
        if not items_data:
            flash('No se puede crear una orden vacía.', 'error')
            return redirect(url_for('waiter.take_order'))

        parsed_items = [json.loads(item) for item in items_data]
        
        # --- Stock Validation --- #
        stock_requirements = {}

        for item_data in parsed_items:
            product = Product.query.get(int(item_data['product_id']))
            quantity = int(item_data['quantity'])

            if product.category == 'Combo':
                for component_item in product.components:
                    comp = component_item.component
                    base_product = comp.parent if not comp.is_base_product else comp
                    consumption = comp.stock_consumption if not comp.is_base_product else 1
                    total_consumption = consumption * component_item.quantity * quantity
                    stock_requirements[base_product.id] = stock_requirements.get(base_product.id, 0) + total_consumption
            elif product.is_base_product:
                stock_requirements[product.id] = stock_requirements.get(product.id, 0) + quantity
            else: # Is a variant
                parent_id = product.parent_id
                consumption = product.stock_consumption * quantity
                stock_requirements[parent_id] = stock_requirements.get(parent_id, 0) + consumption

            # Handle extras stock
            for extra_data in item_data.get('extras', []):
                extra = Product.query.get(int(extra_data['id']))
                extra_quantity = int(extra_data['quantity'])
                stock_requirements[extra.id] = stock_requirements.get(extra.id, 0) + (extra_quantity * quantity)

        for product_id, required_stock in stock_requirements.items():
            product_to_check = Product.query.get(product_id)
            if not product_to_check or product_to_check.stock < required_stock:
                flash(f'Stock insuficiente para {product_to_check.name if product_to_check else "producto"}. Pedido: {required_stock}, Disponible: {product_to_check.stock if product_to_check else 0}', 'error')
                return redirect(url_for('waiter.take_order'))

        # --- Create Order and Items --- #
        order = Order(customer_name=customer_name, customer_phone=customer_phone, waiter_id=current_user.id)
        db.session.add(order)
        db.session.flush()

        grand_total = 0
        for item_data in parsed_items:
            product = Product.query.get(int(item_data['product_id']))
            quantity = int(item_data['quantity'])
            notes = item_data.get('notes', '')
            extras_data = item_data.get('extras', [])

            item_price = product.price
            # Always add extras price, regardless of category
            for extra in extras_data:
                extra_product = Product.query.get(extra['id'])
                if extra_product:
                    item_price += extra_product.price * int(extra['quantity'])

            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity, unit_price=item_price, extras=json.dumps(extras_data), notes=notes)
            db.session.add(order_item)
            grand_total += item_price * quantity
        
        order.total = grand_total

        # --- Decrement Stock --- #
        for product_id, consumed_stock in stock_requirements.items():
            product_to_update = Product.query.get(product_id)
            if product_to_update:
                product_to_update.stock -= consumed_stock
                socketio.emit('stock_update', {'product_id': product_to_update.id, 'stock': product_to_update.stock})

        db.session.commit()
        flash('Orden creada exitosamente.', 'success')
        return redirect(url_for('waiter.view_order', order_id=order.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la orden: {e}', 'error')
        return redirect(url_for('waiter.take_order'))

@waiter_bp.route('/order/<int:order_id>')
@login_required
@waiter_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('waiter/view_order.html', order=order)

@waiter_bp.route('/send_to_kitchen/<int:order_id>', methods=['POST'])
@login_required
@waiter_required
def send_to_kitchen(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'pending':
        flash('Esta orden ya fue enviada a cocina.', 'error')
        return redirect(url_for('waiter.view_order', order_id=order_id))
    order.status = 'sent_to_kitchen'
    db.session.commit()
    def get_display_name(product):
        if not product.is_base_product and product.parent:
            return f"{product.parent.name} ({product.name})"
        return product.name
    socketio.emit('new_order', {
        'order_id': order.id,
        'customer_name': order.customer_name,
        'items': [{
            'product_name': get_display_name(item.product),
            'quantity': item.quantity,
            'extras': item.extras,
            'notes': item.notes
        } for item in order.items]
    }, room='kitchen')
    flash('Orden enviada a cocina exitosamente.', 'success')
    return redirect(url_for('waiter.dashboard'))

@waiter_bp.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
@waiter_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status not in ['pending', 'sent_to_kitchen']:
        flash('No se puede cancelar esta orden.', 'error')
        return redirect(url_for('waiter.view_order', order_id=order_id))
    
    # Restore stock
    for item in order.items:
        product = item.product
        if product.category == 'Combo':
            for component_item in product.components:
                comp = component_item.component
                base_product = comp.parent if not comp.is_base_product else comp
                consumption = comp.stock_consumption if not comp.is_base_product else 1
                total_to_restore = consumption * component_item.quantity * item.quantity
                base_product.stock += total_to_restore
                socketio.emit('stock_update', {'product_id': base_product.id, 'stock': base_product.stock})
        elif product.is_base_product:
            product.stock += item.quantity
            socketio.emit('stock_update', {'product_id': product.id, 'stock': product.stock})
        else: # It's a variant
            parent = product.parent
            if parent:
                parent.stock += product.stock_consumption * item.quantity
                socketio.emit('stock_update', {'product_id': parent.id, 'stock': parent.stock})

        # Restore stock for extras
        if item.extras:
            try:
                extras_list = json.loads(item.extras)
                for extra_data in extras_list:
                    extra_product = Product.query.get(extra_data.get('id'))
                    if extra_product:
                        extra_quantity = int(extra_data.get('quantity', 1))
                        extra_product.stock += extra_quantity * item.quantity
                        socketio.emit('stock_update', {'product_id': extra_product.id, 'stock': extra_product.stock})
            except (json.JSONDecodeError, TypeError):
                pass
    
    order.status = 'cancelled'
    db.session.commit()
    flash('Orden cancelada y stock restaurado.', 'success')
    return redirect(url_for('waiter.dashboard'))

@waiter_bp.route('/process_payment/<int:order_id>', methods=['GET', 'POST'])
@login_required
@waiter_required
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'ready':
        flash('La orden debe estar lista para procesar el pago.', 'error')
        return redirect(url_for('waiter.view_order', order_id=order_id))
    if request.method == 'POST':
        cash_received_str = request.form.get('cash_received')
        try:
            cash_received = float(cash_received_str) if cash_received_str else 0.0
            if cash_received < order.total:
                flash('El efectivo recibido es menor al total de la orden.', 'error')
                return render_template('waiter/process_payment.html', order=order)
            change = cash_received - order.total
            order.status = 'paid'
            order.cash_received = cash_received
            order.change_given = change
            db.session.commit()
            flash('Pago procesado exitosamente.', 'success')
            return render_template('waiter/payment_receipt.html', order=order, cash_received=cash_received, change=change)
        except (ValueError, TypeError):
            flash('Monto de efectivo inválido.', 'error')
            return render_template('waiter/process_payment.html', order=order)
    return render_template('waiter/process_payment.html', order=order)

@waiter_bp.route('/receipt/<int:order_id>/pdf')
@login_required
@waiter_required
def receipt_pdf(order_id):
    order = Order.query.get_or_404(order_id)
    cash_received = request.args.get('cash_received', default=order.cash_received or 0, type=float)
    change = request.args.get('change', default=order.change_given or 0, type=float)
    if order.status != 'paid':
        flash('La orden no ha sido pagada.', 'error')
        return redirect(url_for('waiter.view_order', order_id=order_id))
    pdf_buffer = generate_receipt_pdf(order, cash_received, change)
    return pdf_buffer, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': f'inline; filename=recibo_orden_{order.id}.pdf'}
