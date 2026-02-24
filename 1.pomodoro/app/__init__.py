from flask import Flask


def create_app(test_config=None):
    """アプリファクトリ。テスト時は test_config を渡して設定を上書きしてください。"""
    app = Flask(__name__, instance_relative_config=False, static_folder="../static", template_folder="../templates")

    # デフォルト設定
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is not None:
        app.config.update(test_config)

    # ルート登録
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    # 認証ルート登録
    from .auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 認証機能初期化
    from .auth import init_auth
    init_auth(app)

    # 簡易ストレージ（現時点ではメモリ）
    # 形式: list of {id, start_time_iso, end_time_iso, duration_sec, status, type}
    app.config.setdefault('POMODORO_STORE', [])
    app.config.setdefault('POMODORO_NEXT_ID', 1)
    
    # ゲーミフィケーションストレージ
    app.config.setdefault('GAMIFICATION_DATA', {
        'total_xp': 0,
        'unlocked_badges': []  # list of badge IDs
    })

    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # WebSocket初期化（ENABLE_WEBSOCKETがTrueの場合のみ）
    if test_config and test_config.get('ENABLE_WEBSOCKET', False):
        from .websocket import init_socketio
        socketio = init_socketio(app)
        app.socketio = socketio
    elif not test_config:
        # 通常実行時はデフォルトで有効
        from .websocket import init_socketio
        socketio = init_socketio(app)
        app.socketio = socketio

    return app
