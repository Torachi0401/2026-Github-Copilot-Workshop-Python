"""WebSocket リアルタイム同期機能のテスト"""
import pytest
from app import create_app


def test_websocket_enabled_in_production():
    """本番環境ではWebSocketが有効化される"""
    app = create_app({'ENABLE_WEBSOCKET': True})
    assert hasattr(app, 'socketio')


def test_websocket_disabled_in_test():
    """テスト環境ではENABLE_WEBSOCKET=Falseで無効化可能"""
    app = create_app({'ENABLE_WEBSOCKET': False})
    assert not hasattr(app, 'socketio')


def test_websocket_module_imports():
    """WebSocketモジュールが正しくインポートできる"""
    from app.websocket import init_socketio, register_handlers
    assert callable(init_socketio)
    assert callable(register_handlers)


def test_socketio_initialization():
    """SocketIOが正しく初期化される"""
    app = create_app({'ENABLE_WEBSOCKET': True})
    
    # SocketIOインスタンスが存在する
    assert hasattr(app, 'socketio')
    assert app.socketio is not None
    
    # アプリが正しく設定されている
    assert app.socketio.server is not None


# WebSocketイベントのテストには実際の接続が必要なため、
# ここでは基本的な初期化テストのみを実施
# より詳細なテストはE2Eテストで実施することを推奨
