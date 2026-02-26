from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, LoginAttempt
from datetime import datetime, timedelta
import secrets
import html

auth_bp = Blueprint('auth', __name__)

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _get_client_ip():
    """Get real client IP (handles proxies)."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'


def _check_brute_force(ip, username):
    """Returns (is_blocked, attempts_left, blocked_until)."""
    attempt = LoginAttempt.query.filter_by(
        ip_address=ip, username=username
    ).first()
    if not attempt:
        return False, MAX_ATTEMPTS, None

    # Check if block has expired
    if attempt.blocked_until and datetime.utcnow() > attempt.blocked_until:
        attempt.attempts = 0
        attempt.blocked_until = None
        db.session.commit()
        return False, MAX_ATTEMPTS, None

    if attempt.blocked_until:
        return True, 0, attempt.blocked_until

    return False, max(0, MAX_ATTEMPTS - attempt.attempts), None


def _record_failed_attempt(ip, username):
    """Record a failed login attempt, block if threshold exceeded."""
    attempt = LoginAttempt.query.filter_by(ip_address=ip, username=username).first()
    if not attempt:
        attempt = LoginAttempt(ip_address=ip, username=username, attempts=1)
        db.session.add(attempt)
    else:
        attempt.attempts += 1
        attempt.last_attempt = datetime.utcnow()

    if attempt.attempts >= MAX_ATTEMPTS:
        attempt.blocked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)

    db.session.commit()


def _clear_attempts(ip, username):
    """Clear attempts on successful login."""
    attempt = LoginAttempt.query.filter_by(ip_address=ip, username=username).first()
    if attempt:
        attempt.attempts = 0
        attempt.blocked_until = None
        db.session.commit()


def _sanitize(value):
    """Basic XSS sanitization."""
    if value is None:
        return value
    return html.escape(str(value))


@auth_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """Issue a CSRF token stored in the session."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return jsonify({'csrf_token': session['csrf_token']})


def _validate_csrf(data):
    """Validate CSRF token from JSON body against session."""
    token = data.get('csrf_token') if data else None
    return token and token == session.get('csrf_token')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    username = _sanitize(data.get('username', '').strip())
    password = data.get('password', '')
    email = _sanitize(data.get('email', '').strip())

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already taken'}), 409

    user = User(username=username, email=email or None)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Account created successfully'})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    ip = _get_client_ip()
    username = _sanitize(data.get('username', '').strip())
    password = data.get('password', '')

    is_blocked, attempts_left, blocked_until = _check_brute_force(ip, username)
    if is_blocked:
        remaining = int((blocked_until - datetime.utcnow()).total_seconds() / 60) + 1
        return jsonify({
            'success': False,
            'message': f'Too many failed attempts. Blocked for {remaining} more minutes.'
        }), 429

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        _clear_attempts(ip, username)
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            }
        })

    _record_failed_attempt(ip, username)
    _, attempts_left, _ = _check_brute_force(ip, username)
    msg = f'Invalid credentials. {attempts_left} attempt(s) remaining.'
    if attempts_left == 0:
        msg = f'Too many failed attempts. Blocked for {LOCKOUT_MINUTES} minutes.'
    return jsonify({'success': False, 'message': msg}), 401


@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    ip = _get_client_ip()
    username = _sanitize(data.get('username', '').strip())
    password = data.get('password', '')

    is_blocked, attempts_left, blocked_until = _check_brute_force(ip, username)
    if is_blocked:
        remaining = int((blocked_until - datetime.utcnow()).total_seconds() / 60) + 1
        return jsonify({
            'success': False,
            'message': f'Account locked. Try again in {remaining} minute(s).'
        }), 429

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if not user.is_admin:
            _record_failed_attempt(ip, username)
            return jsonify({'success': False, 'message': 'Access denied: admin only'}), 403

        _clear_attempts(ip, username)
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Admin login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': True
            }
        })

    _record_failed_attempt(ip, username)
    _, attempts_left, _ = _check_brute_force(ip, username)
    msg = f'Invalid credentials. {attempts_left} attempt(s) remaining.'
    if attempts_left == 0:
        msg = f'Too many failed attempts. Blocked for {LOCKOUT_MINUTES} minutes.'
    return jsonify({'success': False, 'message': msg}), 401


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'is_admin': current_user.is_admin
            }
        })
    return jsonify({'success': False, 'message': 'Not logged in'}), 401
