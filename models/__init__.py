from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# ─── Users ───────────────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ─── Brute-Force Protection ───────────────────────────────────────────────────
class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(150), nullable=True)
    attempts = db.Column(db.Integer, default=1)
    blocked_until = db.Column(db.DateTime, nullable=True)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)


# ─── Categories ──────────────────────────────────────────────────────────────
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    products = db.relationship('Product', backref='category_obj', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'image_url': self.image_url,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
        }


# ─── Products ─────────────────────────────────────────────────────────────────
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    discount = db.Column(db.Float, default=0.0)
    image = db.Column(db.String(500), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    stock = db.Column(db.Integer, default=10)
    rating = db.Column(db.Float, default=4.5)
    rating_count = db.Column(db.Integer, default=0)
    tag = db.Column(db.String(50), nullable=True)  # 'new', 'sale', 'hot', 'stock'
    is_featured = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'old_price': self.old_price,
            'discount': self.discount,
            'image': self.image,
            'brand': self.brand,
            'stock': self.stock,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'tag': self.tag,
            'is_featured': self.is_featured,
            'category_id': self.category_id,
        }


# ─── Cart ─────────────────────────────────────────────────────────────────────
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(150), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product', backref='cart_items')


# ─── Orders ───────────────────────────────────────────────────────────────────
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(150), nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='pending')  # pending, processing, shipped, delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    user = db.relationship('User', backref='orders')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'items': [i.to_dict() for i in self.items],
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'quantity': self.quantity,
            'price': self.price_at_purchase,
        }


# ─── Banner Slides ────────────────────────────────────────────────────────────
class BannerSlide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(300), nullable=True)
    badge_text = db.Column(db.String(50), nullable=True)
    badge_style = db.Column(db.String(200), nullable=True)  # CSS style string
    button_text = db.Column(db.String(100), default='Shop Now')
    image_url = db.Column(db.String(500), nullable=True)
    bg_gradient = db.Column(db.String(200), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'badge_text': self.badge_text,
            'badge_style': self.badge_style,
            'button_text': self.button_text,
            'image_url': self.image_url,
            'bg_gradient': self.bg_gradient,
            'sort_order': self.sort_order,
        }


# ─── UI Assets (Dynamic CMS) ─────────────────────────────────────────────────
class UIAsset(db.Model):
    __tablename__ = 'ui_asset'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    label = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Text, nullable=True)
    asset_type = db.Column(db.String(20), default='text')  # text, image, color
    section = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'label': self.label,
            'value': self.value,
            'asset_type': self.asset_type,
            'section': self.section,
            'description': self.description,
        }
