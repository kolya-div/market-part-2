from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, Product, Category, BannerSlide, UIAsset, CartItem, Order, OrderItem
from functools import lru_cache
import json

main_bp = Blueprint('main', __name__)


# ─── Pages ────────────────────────────────────────────────────────────────────
@main_bp.route('/')
def home():
    return render_template('index.html')


# ─── UI Config (Dynamic CMS) ──────────────────────────────────────────────────
@main_bp.route('/api/ui-config', methods=['GET'])
def get_ui_config():
    """Return all UIAssets as {key: value} JSON. Cached per request cycle."""
    assets = UIAsset.query.all()
    config = {a.key: a.value for a in assets}
    return jsonify(config)


# ─── Products API ─────────────────────────────────────────────────────────────
@main_bp.route('/api/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category_id = request.args.get('category_id', type=int)
    featured = request.args.get('featured', type=int)
    tag = request.args.get('tag')
    sort = request.args.get('sort', 'newest')  # newest, price_asc, price_desc, rating

    q = Product.query.filter_by(is_deleted=False)

    if category_id:
        q = q.filter_by(category_id=category_id)
    if featured:
        q = q.filter_by(is_featured=True)
    if tag:
        q = q.filter_by(tag=tag)

    if sort == 'price_asc':
        q = q.order_by(Product.price.asc())
    elif sort == 'price_desc':
        q = q.order_by(Product.price.desc())
    elif sort == 'rating':
        q = q.order_by(Product.rating.desc())
    else:
        q = q.order_by(Product.id.desc())

    products = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'page': page,
    })


@main_bp.route('/api/products/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'success': False, 'message': 'Query too short'}), 400

    results = Product.query.filter(
        Product.is_deleted == False,
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%'),
            Product.brand.ilike(f'%{query}%'),
        )
    ).limit(20).all()

    return jsonify({'success': True, 'products': [p.to_dict() for p in results]})


@main_bp.route('/api/products/<int:pid>', methods=['GET'])
def get_product(pid):
    product = Product.query.filter_by(id=pid, is_deleted=False).first_or_404()
    return jsonify({'success': True, 'product': product.to_dict()})


# ─── Categories API ───────────────────────────────────────────────────────────
@main_bp.route('/api/categories', methods=['GET'])
def get_categories():
    cats = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return jsonify({'success': True, 'categories': [c.to_dict() for c in cats]})


# ─── Banners API ──────────────────────────────────────────────────────────────
@main_bp.route('/api/banners', methods=['GET'])
def get_banners():
    banners = BannerSlide.query.filter_by(is_active=True).order_by(
        BannerSlide.sort_order).all()
    return jsonify({'success': True, 'banners': [b.to_dict() for b in banners]})


# ─── Cart API (server-side, session-based) ────────────────────────────────────
@main_bp.route('/api/cart', methods=['GET'])
def get_cart():
    from flask import session as flask_session
    sid = flask_session.get('cart_session_id')
    uid = current_user.id if current_user.is_authenticated else None

    items = []
    if uid:
        items = CartItem.query.filter_by(user_id=uid).all()
    elif sid:
        items = CartItem.query.filter_by(session_id=sid).all()

    return jsonify({
        'success': True,
        'items': [{
            'product_id': i.product_id,
            'quantity': i.quantity,
            'product': i.product.to_dict() if i.product else None,
        } for i in items]
    })


@main_bp.route('/api/cart', methods=['POST'])
def add_to_cart():
    from flask import session as flask_session
    import uuid
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if not product_id:
        return jsonify({'success': False, 'message': 'product_id required'}), 400

    product = Product.query.filter_by(id=product_id, is_deleted=False).first()
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

    uid = current_user.id if current_user.is_authenticated else None
    sid = None
    if not uid:
        if 'cart_session_id' not in flask_session:
            flask_session['cart_session_id'] = str(uuid.uuid4())
        sid = flask_session['cart_session_id']

    existing = CartItem.query.filter_by(
        product_id=product_id,
        user_id=uid,
        session_id=sid
    ).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(product_id=product_id, user_id=uid,
                        session_id=sid, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Added to cart'})


# ─── Checkout API ─────────────────────────────────────────────────────────────
@main_bp.route('/api/checkout', methods=['POST'])
def checkout():
    from flask import session as flask_session
    uid = current_user.id if current_user.is_authenticated else None
    sid = flask_session.get('cart_session_id')

    items = []
    if uid:
        items = CartItem.query.filter_by(user_id=uid).all()
    elif sid:
        items = CartItem.query.filter_by(session_id=sid).all()

    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    total = sum(i.product.price * i.quantity for i in items if i.product)

    order = Order(user_id=uid, session_id=sid, total_amount=total, status='pending')
    db.session.add(order)
    db.session.flush()

    for i in items:
        oi = OrderItem(
            order_id=order.id,
            product_id=i.product_id,
            quantity=i.quantity,
            price_at_purchase=i.product.price if i.product else 0,
        )
        db.session.add(oi)
        db.session.delete(i)

    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id, 'total': total})
