from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, waiter, cook
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=True)  # Can be null for base products that are not for sale
    category = db.Column(db.String(50), nullable=False)  # Principal, Bebida, Extra
    stock = db.Column(db.Integer, default=0) # Stock for base products
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Self-referential relationship for variants
    parent_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    variants = db.relationship('Product', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    # How many units of parent stock this variant consumes.
    stock_consumption = db.Column(db.Integer, nullable=False, default=1)

    # Helper to distinguish base products from variants
    @property
    def is_base_product(self):
        return self.parent_id is None

    # Helper to get available stock, whether it's a base or variant
    @property
    def available_stock(self):
        if self.is_base_product:
            return self.stock
        else:
            return self.parent.stock if self.parent else 0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock_consumption': self.stock_consumption
        }

    @property
    def variants_as_dicts(self):
        return [variant.to_dict() for variant in self.variants]

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')  # pending, sent_to_kitchen, in_preparation, ready, paid, cancelled
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    waiter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cash_received = db.Column(db.Float)
    change_given = db.Column(db.Float)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    waiter = db.relationship('User', backref='orders')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    extras = db.Column(db.Text)  # JSON string for extras
    notes = db.Column(db.Text)
    
    product = db.relationship('Product', backref='order_items')

class DailyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_sales = db.Column(db.Float, default=0.0)
    cash_in_register = db.Column(db.Float)
    difference = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
