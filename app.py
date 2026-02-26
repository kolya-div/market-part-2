import os
from flask import Flask, render_template, g, request
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production-abc123xyz')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///promarket.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # ── Database ───────────────────────────────────────────────────────────────
    from models import db, User
    db.init_app(app)

    # ── Flask-Login ────────────────────────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    # ── Blueprints ─────────────────────────────────────────────────────────────
    from apps.main import main_bp
    from apps.auth import auth_bp
    from apps.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ── Security Headers ───────────────────────────────────────────────────────
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Permissive CSP (allow Unsplash & Google Fonts for the frontend)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://images.unsplash.com https://via.placeholder.com; "
            "connect-src 'self';"
        )
        return response

    # ── DB Init & Seed ─────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

        # Auto-seed on first run if no admin user exists
        from models import User as _User
        if not _User.query.filter_by(is_admin=True).first():
            try:
                from seed import run_seed
                run_seed()
                print('[App] Auto-seeded database on first run.')
            except Exception as e:
                print(f'[App] Seed error: {e}')

    # ── CLI Commands ───────────────────────────────────────────────────────────
    @app.cli.command('seed')
    def seed_cmd():
        """Seed the database with demo data."""
        from seed import run_seed
        run_seed()

    @app.cli.command('create-admin')
    def create_admin_cmd():
        """Create an admin user interactively."""
        from models import User
        username = input('Admin username: ')
        password = input('Admin password: ')
        email = input('Admin email (optional): ').strip() or None
        if User.query.filter_by(username=username).first():
            print('User already exists.')
            return
        u = User(username=username, email=email, is_admin=True)
        u.set_password(password)
        from models import db
        db.session.add(u)
        db.session.commit()
        print(f'Admin "{username}" created successfully.')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
