from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Product, Order, OrderItem
from app import db, socketio
from functools import wraps

cook_bp = Blueprint('cook', __name__)

def cook_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'cook':
            flash('Acceso denegado. Solo cocineros.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@cook_bp.route('/dashboard')
@login_required
@cook_required
def dashboard():
    orders = Order.query.filter(
        Order.status.in_(['sent_to_kitchen', 'in_preparation'])
    ).order_by(Order.created_at).all()
    
    return render_template('cook/dashboard.html', orders=orders)

@cook_bp.route('/start_preparation/<int:order_id>', methods=['POST'])
@login_required
@cook_required
def start_preparation(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status != 'sent_to_kitchen':
        return jsonify({'success': False, 'message': 'Esta orden no puede ser preparada.'}), 400
    
    order.status = 'in_preparation'
    db.session.commit()
    
    # Emit socket event to both rooms
    socketio.emit('order_status_update', {
        'order_id': order.id,
        'status': 'in_preparation',
        'customer_name': order.customer_name
    }, room='waiters')
    socketio.emit('order_status_update', {
        'order_id': order.id,
        'status': 'in_preparation',
        'customer_name': order.customer_name
    }, room='kitchen')
    
    return jsonify({'success': True, 'message': 'Orden marcada como en preparación.'})

@cook_bp.route('/mark_ready/<int:order_id>', methods=['POST'])
@login_required
@cook_required
def mark_ready(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status != 'in_preparation':
        return jsonify({'success': False, 'message': 'Esta orden no está en preparación.'}), 400
    
    order.status = 'ready'
    db.session.commit()
    
    # Emit socket event to both rooms
    socketio.emit('order_status_update', {
        'order_id': order.id,
        'status': 'ready',
        'customer_name': order.customer_name
    }, room='waiters')
    socketio.emit('order_status_update', {
        'order_id': order.id,
        'status': 'ready',
        'customer_name': order.customer_name
    }, room='kitchen')
    
    return jsonify({'success': True, 'message': 'Orden marcada como lista.'})

@cook_bp.route('/stock')
@login_required
@cook_required
def stock():
    products = Product.query.filter(Product.parent_id.is_(None), Product.is_active==True).order_by(Product.category, Product.name).all()
    return render_template('cook/stock.html', products=products)
