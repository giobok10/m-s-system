from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

# Association table for the combo recipes
class ComboItem(db.Model):
    __tablename__ = 'combo_item'
    id = db.Column(db.Integer, primary_key=True)
    combo_product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    component_product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    component = db.relationship('Product', foreign_keys=[component_product_id])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_active = db.Column(db.Boolean, default=True)

    components = db.relationship('ComboItem', foreign_keys=[ComboItem.combo_product_id], lazy='dynamic', cascade="all, delete-orphan")
    parent_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    variants = db.relationship('Product', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', primaryjoin='and_(Product.parent_id == Product.id, Product.is_active == True)')
    stock_consumption = db.Column(db.Integer, nullable=False, default=1)

    @property
    def is_base_product(self):
        return self.parent_id is None

    @property
    def available_stock(self):
        if self.is_base_product:
            return self.stock
        else:
            return self.parent.stock if self.parent else 0

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'stock': self.stock,
            'parent_id': self.parent_id,
            'stock_consumption': self.stock_consumption,
            'variants': [v.to_dict() for v in self.variants],
            'components': []
        }
        if self.category == 'Combo':
            data['components'] = [
                {
                    'component': item.component.to_dict(),
                    'quantity': item.quantity
                }
                for item in self.components
            ]
        return data

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    waiter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cash_received = db.Column(db.Float)
    change_given = db.Column(db.Float)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    waiter = db.relationship('User', backref='orders')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'status': self.status,
            'total': self.total,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cash_received': self.cash_received,
            'change_given': self.change_given,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    extras = db.Column(db.Text)
    notes = db.Column(db.Text)
    product = db.relationship('Product', backref='order_items')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'extras': self.extras,
            'notes': self.notes
        }

class DailyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_sales = db.Column(db.Float, default=0.0)
    cash_in_register = db.Column(db.Float)
    difference = db.Column(db.Float)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
