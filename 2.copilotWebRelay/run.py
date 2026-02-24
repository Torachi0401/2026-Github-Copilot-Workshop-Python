from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # 環境変数でデバッグモードを制御（デフォルトはFalse）
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
