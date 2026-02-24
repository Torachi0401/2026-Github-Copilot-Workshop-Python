from flask import Flask
from .models import db


def create_app(test_config=None):
    """アプリファクトリ。テスト時は test_config を渡して設定を上書きしてください。"""
    app = Flask(__name__, instance_relative_config=False, static_folder="../static", template_folder="../templates")

    # デフォルト設定
    from config import Config, TestingConfig
    if test_config is not None and test_config.get('TESTING'):
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)
    
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is not None:
        app.config.update(test_config)
    
    # SQLAlchemyを初期化
    db.init_app(app)
    
    # データベーステーブルを作成
    with app.app_context():
        db.create_all()

    # ルート登録
    from .routes import bp

    app.register_blueprint(bp)

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

    return app
