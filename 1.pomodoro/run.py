from app import create_app
import os


app = create_app({'ENABLE_WEBSOCKET': True})


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    
    # WebSocketを使用する場合はsocketio.runを使用
    if hasattr(app, 'socketio'):
        app.socketio.run(app, debug=debug_mode, host="0.0.0.0")
    else:
        app.run(debug=debug_mode, host="0.0.0.0")
