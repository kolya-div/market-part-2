"""
Seed script — populates the DB with realistic demo data.
Run via: python seed.py  OR  call run_seed() from admin API.
"""
from datetime import datetime


def run_seed():
    from models import db, User, Category, Product, BannerSlide, UIAsset

    # ── Admin User ────────────────────────────────────────────────────────────
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@electromarket.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)

    # ── Categories ────────────────────────────────────────────────────────────
    categories_data = [
        ('Phones', 'phones',
         'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&q=80&w=200&h=200', 1),
        ('Laptops', 'laptops',
         'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&q=80&w=200&h=200', 2),
        ('Watches', 'watches',
         'https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&q=80&w=200&h=200', 3),
        ('Audio', 'audio',
         'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=200&h=200', 4),
        ('Tablets', 'tablets',
         'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&q=80&w=200&h=200', 5),
        ('Gaming', 'gaming',
         'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&q=80&w=200&h=200', 6),
        ('Cameras', 'cameras',
         'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=200&h=200', 7),
        ('Smart Home', 'smart-home',
         'https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&q=80&w=200&h=200', 8),
    ]

    cat_map = {}
    for name, slug, img, order in categories_data:
        cat = Category.query.filter_by(slug=slug).first()
        if not cat:
            cat = Category(name=name, slug=slug, image_url=img, sort_order=order)
            db.session.add(cat)
            db.session.flush()
        cat_map[slug] = cat.id

    # ── Products ──────────────────────────────────────────────────────────────
    products_data = [
        {
            'name': 'iPhone 15 Pro Max 256GB Natural Titanium',
            'description': 'A17 Pro chip, Titanium design, 48MP camera system',
            'price': 1199.0, 'old_price': None, 'discount': 0,
            'image': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Apple', 'stock': 45, 'rating': 4.9, 'rating_count': 124,
            'tag': 'new', 'is_featured': True, 'category': 'phones',
        },
        {
            'name': 'Apple Watch Ultra 2',
            'description': 'Rugged GPS + Cellular, 49mm titanium case',
            'price': 799.0, 'old_price': 899.0, 'discount': 15,
            'image': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Apple', 'stock': 12, 'rating': 4.7, 'rating_count': 89,
            'tag': 'sale', 'is_featured': True, 'category': 'watches',
        },
        {
            'name': 'AirPods Pro (2nd Generation)',
            'description': 'USB-C, Active Noise Cancellation, Adaptive Audio',
            'price': 249.0, 'old_price': None, 'discount': 0,
            'image': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Apple', 'stock': 78, 'rating': 4.8, 'rating_count': 312,
            'tag': 'hot', 'is_featured': True, 'category': 'audio',
        },
        {
            'name': 'Dell XPS 15 9530',
            'description': 'Intel i9-13900H, NVIDIA RTX 4070, 32GB RAM, 1TB SSD',
            'price': 2499.0, 'old_price': None, 'discount': 0,
            'image': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Dell', 'stock': 8, 'rating': 4.8, 'rating_count': 45,
            'tag': 'stock', 'is_featured': True, 'category': 'laptops',
        },
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'description': '512GB, Titanium Black, Unlocked, Galaxy AI',
            'price': 1299.0, 'old_price': 1499.0, 'discount': 20,
            'image': 'https://images.unsplash.com/photo-1628102491629-778571d893a3?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Samsung', 'stock': 23, 'rating': 4.8, 'rating_count': 112,
            'tag': 'sale', 'is_featured': True, 'category': 'phones',
        },
        {
            'name': 'MacBook Pro 14" M3 Max',
            'description': 'M3 Max chip, 36GB RAM, 1TB SSD, Liquid Retina XDR',
            'price': 2999.0, 'old_price': None, 'discount': 0,
            'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Apple', 'stock': 15, 'rating': 4.9, 'rating_count': 67,
            'tag': 'new', 'is_featured': True, 'category': 'laptops',
        },
        {
            'name': 'Sony WH-1000XM5',
            'description': 'Industry-leading noise cancellation, 30-hr battery',
            'price': 349.0, 'old_price': 399.0, 'discount': 12,
            'image': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Sony', 'stock': 34, 'rating': 4.7, 'rating_count': 203,
            'tag': 'sale', 'is_featured': False, 'category': 'audio',
        },
        {
            'name': 'iPad Pro 13" M4',
            'description': 'Ultra Retina XDR display, M4 chip, Apple Pencil Pro compatible',
            'price': 1299.0, 'old_price': None, 'discount': 0,
            'image': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Apple', 'stock': 20, 'rating': 4.8, 'rating_count': 91,
            'tag': 'new', 'is_featured': True, 'category': 'tablets',
        },
        {
            'name': 'PlayStation 5 Digital Edition',
            'description': 'Ultra-high speed SSD, ray tracing, 4K gaming',
            'price': 399.0, 'old_price': 499.0, 'discount': 20,
            'image': 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Sony', 'stock': 6, 'rating': 4.9, 'rating_count': 445,
            'tag': 'hot', 'is_featured': True, 'category': 'gaming',
        },
        {
            'name': 'Sony Alpha A7 IV',
            'description': '33MP full-frame mirrorless, 4K 60fps, Real-time Eye AF',
            'price': 2498.0, 'old_price': None, 'discount': 0,
            'image': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Sony', 'stock': 11, 'rating': 4.8, 'rating_count': 78,
            'tag': 'stock', 'is_featured': False, 'category': 'cameras',
        },
        {
            'name': 'Samsung Smart Hub Starter Kit',
            'description': 'SmartThings Hub + 4 smart bulbs + smart plug bundle',
            'price': 149.0, 'old_price': 199.0, 'discount': 25,
            'image': 'https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Samsung', 'stock': 40, 'rating': 4.5, 'rating_count': 156,
            'tag': 'sale', 'is_featured': False, 'category': 'smart-home',
        },
        {
            'name': 'Lenovo ThinkPad X1 Carbon Gen 11',
            'description': 'Intel Core i7-1365U, 16GB LPDDR5, 512GB SSD, 14" 2.8K OLED',
            'price': 1849.0, 'old_price': 2199.0, 'discount': 16,
            'image': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&q=80&w=400&h=400',
            'brand': 'Lenovo', 'stock': 18, 'rating': 4.6, 'rating_count': 33,
            'tag': 'sale', 'is_featured': False, 'category': 'laptops',
        },
    ]

    for pd in products_data:
        if not Product.query.filter_by(name=pd['name']).first():
            p = Product(
                name=pd['name'], description=pd['description'],
                price=pd['price'], old_price=pd.get('old_price'),
                discount=pd.get('discount', 0), image=pd['image'],
                brand=pd['brand'], stock=pd['stock'], rating=pd['rating'],
                rating_count=pd['rating_count'], tag=pd['tag'],
                is_featured=pd['is_featured'],
                category_id=cat_map.get(pd['category']),
            )
            db.session.add(p)

    # ── Banner Slides ─────────────────────────────────────────────────────────
    banners_data = [
        {
            'title': 'MacBook Pro\nM3 Max',
            'subtitle': 'Mind-blowing. Head-turning.',
            'badge_text': 'New Release',
            'badge_style': 'background:#3B82F6; color:white;',
            'button_text': 'Shop Now',
            'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&q=80&w=500',
            'bg_gradient': 'linear-gradient(135deg, #1a2744 0%, #0f3460 100%)',
            'sort_order': 1,
        },
        {
            'title': 'iPad Pro\nM4 Chip',
            'subtitle': 'Outrageously powerful.',
            'badge_text': 'Staff Pick',
            'badge_style': 'background:#8b5cf6; color:white;',
            'button_text': 'Shop Tablets',
            'image_url': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&q=80&w=500',
            'bg_gradient': 'linear-gradient(135deg, #1f1c2c 0%, #928dab 100%)',
            'sort_order': 2,
        },
        {
            'title': 'iPhone 15\nPro Max',
            'subtitle': 'Titanium strength. Pro photography.',
            'badge_text': 'Hot Deal',
            'badge_style': 'background:white; color:#FF416C;',
            'button_text': 'Shop Phones',
            'image_url': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&q=80&w=500',
            'bg_gradient': 'linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%)',
            'sort_order': 3,
        },
    ]

    for bd in banners_data:
        if not BannerSlide.query.filter_by(title=bd['title']).first():
            b = BannerSlide(**bd)
            db.session.add(b)

    # ── UI Assets (Dynamic CMS Content) ──────────────────────────────────────
    ui_assets_data = [
        # Topbar
        ('topbar_delivery_text', 'Topbar → Delivery Text', 'Free delivery on orders over $150', 'text', 'topbar', 'Announcement bar — left side text 1'),
        ('topbar_support_text', 'Topbar → Support Text', 'Support: 1-800-ELECTRO', 'text', 'topbar', 'Announcement bar — left side text 2'),
        ('topbar_track_link', 'Topbar → Track Order Link', 'Track Order', 'text', 'topbar', 'Right side link 1'),
        ('topbar_help_link', 'Topbar → Help Center Link', 'Help Center', 'text', 'topbar', 'Right side link 2'),
        ('topbar_lang_link', 'Topbar → Language/Currency', 'EN / USD', 'text', 'topbar', 'Right side link 3'),
        # Navbar
        ('logo_text_main', 'Navbar → Logo Main Text', 'Electro', 'text', 'navbar', 'First part of the logo text'),
        ('logo_text_accent', 'Navbar → Logo Accent Text', 'Market', 'text', 'navbar', 'Second (colored) part of the logo text'),
        ('nav_home_btn', 'Navbar → Home Button', 'Home', 'text', 'navbar', 'Navigation link'),
        ('nav_catalog_btn', 'Navbar → Catalog Button', 'Catalog', 'text', 'navbar', 'Navigation link'),
        ('nav_deals_btn', 'Navbar → Deals Button', 'Deals', 'text', 'navbar', 'Navigation link'),
        ('nav_arrivals_btn', 'Navbar → New Arrivals Button', 'New Arrivals', 'text', 'navbar', 'Navigation link'),
        ('nav_search_placeholder', 'Navbar → Search Placeholder', 'Search for premium electronics...', 'text', 'navbar', 'Search input placeholder text'),
        # Category bar
        ('catbar_item1', 'Category Bar → Item 1', 'Smartphones', 'text', 'catbar', ''),
        ('catbar_item2', 'Category Bar → Item 2', 'Laptops & PCs', 'text', 'catbar', ''),
        ('catbar_item3', 'Category Bar → Item 3', 'Tablets', 'text', 'catbar', ''),
        ('catbar_item4', 'Category Bar → Item 4', 'Audio', 'text', 'catbar', ''),
        ('catbar_item5', 'Category Bar → Item 5', 'Smart Home', 'text', 'catbar', ''),
        ('catbar_item6', 'Category Bar → Item 6', 'Gaming', 'text', 'catbar', ''),
        ('catbar_item7', 'Category Bar → Item 7', 'Cameras', 'text', 'catbar', ''),
        ('catbar_item8', 'Category Bar → Item 8', 'Accessories', 'text', 'catbar', ''),
        ('catbar_flash_badge', 'Category Bar → Flash Sale Badge', '⚡ Flash Sale - Up to 40% Off', 'text', 'catbar', 'Badge text on the right of the category bar'),
        # Hero / Banners
        ('hero_btn1_text', 'Hero → Button 1 Text', 'Shop Now', 'text', 'hero', 'CTA button on the first banner card'),
        ('hero_btn2_text', 'Hero → Button 2 Text', 'Shop Audio', 'text', 'hero', 'CTA button on the second banner card'),
        # Features Section
        ('feature1_title', 'Features → Item 1 Title', 'Fast Delivery', 'text', 'features', ''),
        ('feature1_sub', 'Features → Item 1 Subtitle', 'Within 24 hours', 'text', 'features', ''),
        ('feature2_title', 'Features → Item 2 Title', 'Secure Hub', 'text', 'features', ''),
        ('feature2_sub', 'Features → Item 2 Subtitle', '100% secure payment', 'text', 'features', ''),
        ('feature3_title', 'Features → Item 3 Title', 'Return Policy', 'text', 'features', ''),
        ('feature3_sub', 'Features → Item 3 Subtitle', '30 days easy returns', 'text', 'features', ''),
        ('feature4_title', 'Features → Item 4 Title', '24/7 Support', 'text', 'features', ''),
        ('feature4_sub', 'Features → Item 4 Subtitle', 'Dedicated support', 'text', 'features', ''),
        # Shop by Category
        ('categories_section_title', 'Categories → Section Title', 'Shop by Category', 'text', 'categories', ''),
        ('categories_section_sub', 'Categories → Section Subtitle', "Find exactly what you're looking for", 'text', 'categories', ''),
        # Trending
        ('trending_section_title', 'Trending → Section Title', 'Trending Now', 'text', 'trending', ''),
        ('trending_section_sub', 'Trending → Section Subtitle', 'Most loved by our customers', 'text', 'trending', ''),
        # Flash Sale
        ('flash_section_title', 'Flash Sale → Section Title', 'PlayStation 5\nDigital Edition', 'text', 'flash_sale', ''),
        ('flash_section_sub', 'Flash Sale → Description', 'Experience lightning-fast loading with ultra-high speed SSD.', 'text', 'flash_sale', ''),
        ('flash_main_price', 'Flash Sale → Main Price', '$399', 'text', 'flash_sale', ''),
        ('flash_old_price', 'Flash Sale → Old Price', '$499', 'text', 'flash_sale', ''),
        ('flash_btn1_text', 'Flash Sale → Primary Button', 'Shop Deal', 'text', 'flash_sale', ''),
        ('flash_btn2_text', 'Flash Sale → Secondary Button', 'View All Sales', 'text', 'flash_sale', ''),
        ('flash_image', 'Flash Sale → Product Image', 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&q=80&w=600&h=400', 'image', 'flash_sale', 'Flash sale product image URL'),
        # Brands
        ('brands_label', 'Brands → Label', "Trusted by the world's best brands", 'text', 'brands', ''),
        # Cart
        ('cart_title', 'Cart → Drawer Title', 'Your Cart', 'text', 'cart', ''),
        ('cart_checkout_btn', 'Cart → Checkout Button', 'Checkout Now', 'text', 'cart', ''),
        # Add to Cart buttons
        ('product_add_cart_btn', 'Products → Add to Cart Button', 'Add to Cart', 'text', 'products', ''),
        # Catalog page
        ('catalog_banner_title', 'Catalog → Sidebar Banner Title', 'Summer Sale', 'text', 'catalog', ''),
        ('catalog_banner_sub', 'Catalog → Sidebar Banner Subtitle', 'Up to 50% Off', 'text', 'catalog', ''),
        ('catalog_all_products_title', 'Catalog → All Products Title', 'All Products', 'text', 'catalog', ''),
        # Footer / Misc
        ('site_title', 'Site → Browser Tab Title', 'ElectroMarket - Premium Electronics', 'text', 'site', ''),
    ]

    for key, label, value, atype, section, desc in ui_assets_data:
        if not UIAsset.query.filter_by(key=key).first():
            asset = UIAsset(key=key, label=label, value=value,
                            asset_type=atype, section=section, description=desc)
            db.session.add(asset)

    db.session.commit()
    print('[Seed] OK - Database seeded with demo data.')


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        run_seed()
