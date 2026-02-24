"""認証機能のテスト"""
import pytest
from app import create_app
from app.auth import register_user, authenticate_user, get_user_data, _users, _user_data


@pytest.fixture
def app():
    """テスト用アプリを作成"""
    app = create_app({'TESTING': True})
    yield app
    # テスト後にクリーンアップ
    _users.clear()
    _user_data.clear()


@pytest.fixture
def client(app):
    """テストクライアントを作成"""
    return app.test_client()


def test_register_user():
    """ユーザー登録が正しく動作する"""
    success, message = register_user('testuser', 'testpass123', 'test@example.com')
    assert success is True
    assert 'testuser' in _users
    
    # パスワードはハッシュ化されているか確認
    assert _users['testuser']['password_hash'] != 'testpass123'
    
    # ユーザーデータストアが初期化されているか確認
    user_data = get_user_data('testuser')
    assert 'pomodoro_store' in user_data
    assert 'gamification_data' in user_data


def test_register_duplicate_user():
    """同じユーザー名で登録できない"""
    register_user('testuser', 'pass1')
    success, message = register_user('testuser', 'pass2')
    assert success is False
    assert '既に使用されています' in message


def test_authenticate_user_success():
    """正しい認証情報でログインできる"""
    register_user('testuser', 'testpass123')
    success, message = authenticate_user('testuser', 'testpass123')
    assert success is True


def test_authenticate_user_wrong_password():
    """間違ったパスワードでログインできない"""
    register_user('testuser', 'testpass123')
    success, message = authenticate_user('testuser', 'wrongpass')
    assert success is False


def test_authenticate_user_not_found():
    """存在しないユーザーでログインできない"""
    success, message = authenticate_user('nonexistent', 'anypass')
    assert success is False


def test_login_route(client):
    """ログインページが表示される"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert 'ログイン' in response.get_data(as_text=True)


def test_register_route(client):
    """登録ページが表示される"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert '新規登録' in response.get_data(as_text=True)


def test_login_post_success(client):
    """ログインPOSTリクエストが成功する"""
    # まずユーザーを登録
    register_user('testuser', 'testpass123')
    
    # JSON形式でログイン
    response = client.post('/auth/login', 
        json={'username': 'testuser', 'password': 'testpass123'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    assert data['username'] == 'testuser'


def test_login_post_failure(client):
    """間違った認証情報でログインが失敗する"""
    response = client.post('/auth/login',
        json={'username': 'wrong', 'password': 'wrong'})
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data


def test_register_post_success(client):
    """ユーザー登録POSTリクエストが成功する"""
    response = client.post('/auth/register',
        json={'username': 'newuser', 'password': 'newpass123', 'email': 'new@example.com'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['ok'] is True
    assert data['username'] == 'newuser'


def test_logout(client):
    """ログアウトが正しく動作する"""
    # ログイン
    register_user('testuser', 'testpass123')
    client.post('/auth/login', json={'username': 'testuser', 'password': 'testpass123'})
    
    # ログアウト（JSON形式）
    response = client.post('/auth/logout', json={})
    assert response.status_code == 200


def test_current_user_authenticated(client):
    """認証済みユーザーの情報が取得できる"""
    register_user('testuser', 'testpass123')
    client.post('/auth/login', json={'username': 'testuser', 'password': 'testpass123'})
    
    response = client.get('/auth/current-user')
    assert response.status_code == 200
    data = response.get_json()
    assert data['authenticated'] is True
    assert data['username'] == 'testuser'


def test_current_user_not_authenticated(client):
    """未認証時の情報取得"""
    response = client.get('/auth/current-user')
    assert response.status_code == 200
    data = response.get_json()
    assert data['authenticated'] is False


def test_user_data_isolation():
    """ユーザーごとにデータが分離されている"""
    register_user('user1', 'pass1')
    register_user('user2', 'pass2')
    
    data1 = get_user_data('user1')
    data2 = get_user_data('user2')
    
    # データストアが別々であることを確認
    assert data1 is not data2
    assert data1['pomodoro_store'] is not data2['pomodoro_store']
