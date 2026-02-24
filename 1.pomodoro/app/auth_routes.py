"""認証関連のルート"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from .auth import authenticate_user, register_user, get_current_user, is_authenticated

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログインページとログイン処理"""
    if request.method == 'GET':
        # 既にログイン済みの場合はホームにリダイレクト
        if is_authenticated():
            return redirect(url_for('main.index'))
        return render_template('login.html')
    
    # POSTリクエスト（ログイン処理）
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'ユーザー名とパスワードを入力してください'}), 400
        flash('ユーザー名とパスワードを入力してください', 'error')
        return render_template('login.html')
    
    success, message = authenticate_user(username, password)
    
    if success:
        session['username'] = username
        session.permanent = True
        
        if request.is_json:
            return jsonify({'ok': True, 'message': message, 'username': username}), 200
        
        # リダイレクト先を取得（デフォルトはホーム）
        next_url = request.args.get('next') or url_for('main.index')
        return redirect(next_url)
    else:
        if request.is_json:
            return jsonify({'error': message}), 401
        flash(message, 'error')
        return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録ページと登録処理"""
    if request.method == 'GET':
        # 既にログイン済みの場合はホームにリダイレクト
        if is_authenticated():
            return redirect(url_for('main.index'))
        return render_template('register.html')
    
    # POSTリクエスト（登録処理）
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    
    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'ユーザー名とパスワードを入力してください'}), 400
        flash('ユーザー名とパスワードを入力してください', 'error')
        return render_template('register.html')
    
    success, message = register_user(username, password, email)
    
    if success:
        # 登録後、自動的にログイン
        session['username'] = username
        session.permanent = True
        
        if request.is_json:
            return jsonify({'ok': True, 'message': message, 'username': username}), 201
        
        flash(message, 'success')
        return redirect(url_for('main.index'))
    else:
        if request.is_json:
            return jsonify({'error': message}), 400
        flash(message, 'error')
        return render_template('register.html')


@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """ログアウト処理"""
    session.clear()
    
    if request.is_json:
        return jsonify({'ok': True, 'message': 'ログアウトしました'}), 200
    
    flash('ログアウトしました', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/current-user', methods=['GET'])
def current_user():
    """現在のログインユーザー情報を取得（API用）"""
    username = get_current_user()
    
    if username:
        return jsonify({
            'authenticated': True,
            'username': username
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200
