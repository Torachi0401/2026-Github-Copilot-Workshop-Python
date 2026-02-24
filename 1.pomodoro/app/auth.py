"""簡易認証機能"""
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


# インメモリユーザーストア（本番環境ではデータベースを使用）
_users = {}
_user_data = {}  # ユーザーごとのデータを保存


def init_auth(app):
    """認証機能を初期化"""
    # セッション設定
    app.config.setdefault('SESSION_TYPE', 'filesystem')
    
    # デモユーザーを追加
    register_user('demo', 'demo123', 'demo@example.com')
    

def register_user(username, password, email=None):
    """ユーザーを登録"""
    if username in _users:
        return False, 'ユーザー名は既に使用されています'
    
    _users[username] = {
        'username': username,
        'password_hash': generate_password_hash(password),
        'email': email
    }
    
    # ユーザー専用のデータストアを初期化
    _user_data[username] = {
        'pomodoro_store': [],
        'next_id': 1,
        'gamification_data': {
            'total_xp': 0,
            'unlocked_badges': []
        }
    }
    
    return True, 'ユーザー登録に成功しました'


def authenticate_user(username, password):
    """ユーザーを認証"""
    user = _users.get(username)
    if not user:
        return False, 'ユーザー名またはパスワードが正しくありません'
    
    if not check_password_hash(user['password_hash'], password):
        return False, 'ユーザー名またはパスワードが正しくありません'
    
    return True, 'ログインに成功しました'


def get_current_user():
    """現在のログインユーザーを取得"""
    return session.get('username')


def is_authenticated():
    """ログイン状態を確認"""
    return 'username' in session


def get_user_data(username):
    """ユーザーのデータストアを取得"""
    return _user_data.get(username, {
        'pomodoro_store': [],
        'next_id': 1,
        'gamification_data': {
            'total_xp': 0,
            'unlocked_badges': []
        }
    })


def login_required(f):
    """ログインが必要なエンドポイントのデコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            if request.is_json:
                return jsonify({'error': 'ログインが必要です'}), 401
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_all_users():
    """すべてのユーザー情報を取得（パスワードハッシュを除く）"""
    return [
        {
            'username': user['username'],
            'email': user.get('email')
        }
        for user in _users.values()
    ]
