from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Product, Category, BannerSlide, UIAsset, Order, User
from functools import wraps
import html

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator: require authenticated admin user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


def _s(val):
    """Sanitize string input against XSS."""
    if val is None:
        return None
    return html.escape(str(val).strip())


# ─── Dashboard Stats ──────────────────────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def stats():
    return jsonify({
        'success': True,
        'stats': {
            'products': Product.query.filter_by(is_deleted=False).count(),
            'categories': Category.query.filter_by(is_active=True).count(),
            'orders': Order.query.count(),
            'users': User.query.count(),
            'banners': BannerSlide.query.filter_by(is_active=True).count(),
            'ui_assets': UIAsset.query.count(),
        }
    })


# ─── Products CRUD ────────────────────────────────────────────────────────────
@admin_bp.route('/products', methods=['GET'])
@login_required
@admin_required
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    products = Product.query.filter_by(is_deleted=False).order_by(
        Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'page': page,
    })


@admin_bp.route('/products', methods=['POST'])
@login_required
@admin_required
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data'}), 400

    name = _s(data.get('name'))
    price = data.get('price')
    if not name or price is None:
        return jsonify({'success': False, 'message': 'Name and price required'}), 400

    product = Product(
        name=name,
        description=_s(data.get('description')),
        price=float(price),
        old_price=float(data['old_price']) if data.get('old_price') else None,
        discount=float(data.get('discount', 0)),
        image=_s(data.get('image')),
        brand=_s(data.get('brand')),
        stock=int(data.get('stock', 10)),
        rating=float(data.get('rating', 4.5)),
        rating_count=int(data.get('rating_count', 0)),
        tag=_s(data.get('tag')),
        is_featured=bool(data.get('is_featured', False)),
        category_id=int(data['category_id']) if data.get('category_id') else None,
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'product': product.to_dict()}), 201


@admin_bp.route('/products/<int:pid>', methods=['PUT'])
@login_required
@admin_required
def update_product(pid):
    product = Product.query.get_or_404(pid)
    data = request.get_json() or {}

    if 'name' in data:
        product.name = _s(data['name'])
    if 'description' in data:
        product.description = _s(data['description'])
    if 'price' in data:
        product.price = float(data['price'])
    if 'old_price' in data:
        product.old_price = float(data['old_price']) if data['old_price'] else None
    if 'discount' in data:
        product.discount = float(data['discount'])
    if 'image' in data:
        product.image = _s(data['image'])
    if 'brand' in data:
        product.brand = _s(data['brand'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'rating' in data:
        product.rating = float(data['rating'])
    if 'rating_count' in data:
        product.rating_count = int(data['rating_count'])
    if 'tag' in data:
        product.tag = _s(data['tag'])
    if 'is_featured' in data:
        product.is_featured = bool(data['is_featured'])
    if 'category_id' in data:
        product.category_id = int(data['category_id']) if data['category_id'] else None

    db.session.commit()
    return jsonify({'success': True, 'product': product.to_dict()})


@admin_bp.route('/products/<int:pid>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    product.is_deleted = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Product deleted'})


# ─── Categories CRUD ──────────────────────────────────────────────────────────
@admin_bp.route('/categories', methods=['GET'])
@login_required
@admin_required
def list_categories():
    cats = Category.query.order_by(Category.sort_order).all()
    return jsonify({'success': True, 'categories': [c.to_dict() for c in cats]})


@admin_bp.route('/categories', methods=['POST'])
@login_required
@admin_required
def create_category():
    data = request.get_json() or {}
    name = _s(data.get('name'))
    slug = _s(data.get('slug'))
    if not name or not slug:
        return jsonify({'success': False, 'message': 'Name and slug required'}), 400

    cat = Category(
        name=name,
        slug=slug,
        image_url=_s(data.get('image_url')),
        sort_order=int(data.get('sort_order', 0)),
        is_active=bool(data.get('is_active', True)),
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({'success': True, 'category': cat.to_dict()}), 201


@admin_bp.route('/categories/<int:cid>', methods=['PUT'])
@login_required
@admin_required
def update_category(cid):
    cat = Category.query.get_or_404(cid)
    data = request.get_json() or {}
    if 'name' in data:
        cat.name = _s(data['name'])
    if 'slug' in data:
        cat.slug = _s(data['slug'])
    if 'image_url' in data:
        cat.image_url = _s(data['image_url'])
    if 'sort_order' in data:
        cat.sort_order = int(data['sort_order'])
    if 'is_active' in data:
        cat.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify({'success': True, 'category': cat.to_dict()})


@admin_bp.route('/categories/<int:cid>', methods=['DELETE'])
@login_required
@admin_required
def delete_category(cid):
    cat = Category.query.get_or_404(cid)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Category deleted'})


# ─── Banner Slides CRUD ───────────────────────────────────────────────────────
@admin_bp.route('/banners', methods=['GET'])
@login_required
@admin_required
def list_banners():
    banners = BannerSlide.query.order_by(BannerSlide.sort_order).all()
    return jsonify({'success': True, 'banners': [b.to_dict() for b in banners]})


@admin_bp.route('/banners', methods=['POST'])
@login_required
@admin_required
def create_banner():
    data = request.get_json() or {}
    title = _s(data.get('title'))
    if not title:
        return jsonify({'success': False, 'message': 'Title required'}), 400

    b = BannerSlide(
        title=title,
        subtitle=_s(data.get('subtitle')),
        badge_text=_s(data.get('badge_text')),
        badge_style=_s(data.get('badge_style')),
        button_text=_s(data.get('button_text', 'Shop Now')),
        image_url=_s(data.get('image_url')),
        bg_gradient=_s(data.get('bg_gradient')),
        sort_order=int(data.get('sort_order', 0)),
        is_active=bool(data.get('is_active', True)),
    )
    db.session.add(b)
    db.session.commit()
    return jsonify({'success': True, 'banner': b.to_dict()}), 201


@admin_bp.route('/banners/<int:bid>', methods=['PUT'])
@login_required
@admin_required
def update_banner(bid):
    b = BannerSlide.query.get_or_404(bid)
    data = request.get_json() or {}
    fields = ['title', 'subtitle', 'badge_text', 'badge_style',
              'button_text', 'image_url', 'bg_gradient']
    for f in fields:
        if f in data:
            setattr(b, f, _s(data[f]))
    if 'sort_order' in data:
        b.sort_order = int(data['sort_order'])
    if 'is_active' in data:
        b.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify({'success': True, 'banner': b.to_dict()})


@admin_bp.route('/banners/<int:bid>', methods=['DELETE'])
@login_required
@admin_required
def delete_banner(bid):
    b = BannerSlide.query.get_or_404(bid)
    db.session.delete(b)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Banner deleted'})


# ─── UI Assets ────────────────────────────────────────────────────────────────
@admin_bp.route('/ui-assets', methods=['GET'])
@login_required
@admin_required
def list_ui_assets():
    section = request.args.get('section')
    q = UIAsset.query
    if section:
        q = q.filter_by(section=section)
    assets = q.order_by(UIAsset.section, UIAsset.key).all()
    return jsonify({'success': True, 'assets': [a.to_dict() for a in assets]})


@admin_bp.route('/ui-assets', methods=['PUT'])
@login_required
@admin_required
def update_ui_assets():
    """Bulk update: [{key, value}, ...]"""
    data = request.get_json() or {}
    updates = data.get('updates', [])

    updated = 0
    for item in updates:
        key = item.get('key')
        value = item.get('value')
        if not key:
            continue
        asset = UIAsset.query.filter_by(key=key).first()
        if asset:
            asset.value = value  # intentionally not escaping image URLs
            updated += 1

    db.session.commit()
    return jsonify({'success': True, 'updated': updated})


@admin_bp.route('/ui-assets/<string:key>', methods=['PUT'])
@login_required
@admin_required
def update_ui_asset(key):
    asset = UIAsset.query.filter_by(key=key).first_or_404()
    data = request.get_json() or {}
    asset.value = data.get('value', asset.value)
    db.session.commit()
    return jsonify({'success': True, 'asset': asset.to_dict()})


# ─── Orders ───────────────────────────────────────────────────────────────────
@admin_bp.route('/orders', methods=['GET'])
@login_required
@admin_required
def list_orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return jsonify({
        'success': True,
        'orders': [o.to_dict() for o in orders.items],
        'total': orders.total,
        'pages': orders.pages,
    })


@admin_bp.route('/orders/<int:oid>', methods=['PUT'])
@login_required
@admin_required
def update_order_status(oid):
    order = Order.query.get_or_404(oid)
    data = request.get_json() or {}
    status = data.get('status')
    valid = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if status not in valid:
        return jsonify({'success': False, 'message': f'Invalid status. Use: {valid}'}), 400
    order.status = status
    db.session.commit()
    return jsonify({'success': True, 'order': order.to_dict()})


# ─── Seed Demo Data ───────────────────────────────────────────────────────────
@admin_bp.route('/seed', methods=['POST'])
@login_required
@admin_required
def seed_database():
    """Seed demo products, categories, banners, and UI assets."""
    from seed import run_seed
    run_seed()
    return jsonify({'success': True, 'message': 'Database seeded with demo data'})
