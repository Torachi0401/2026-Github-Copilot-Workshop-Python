"""WebSocket リアルタイム同期機能"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

# SocketIOインスタンス（app/__init__.pyで初期化される）
socketio = None


def init_socketio(app):
    """SocketIOを初期化"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    register_handlers()
    return socketio


def register_handlers():
    """WebSocketイベントハンドラーを登録"""
    
    @socketio.on('connect')
    def handle_connect():
        """クライアント接続時の処理"""
        print(f'Client connected: {request.sid}')
        emit('connection_response', {'status': 'connected', 'sid': request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """クライアント切断時の処理"""
        print(f'Client disconnected: {request.sid}')
    
    @socketio.on('join_sync')
    def handle_join_sync(data):
        """同期ルームに参加"""
        room = data.get('room', 'default')
        join_room(room)
        emit('sync_status', {'status': 'joined', 'room': room}, room=room)
        print(f'Client {request.sid} joined room: {room}')
    
    @socketio.on('leave_sync')
    def handle_leave_sync(data):
        """同期ルームから退出"""
        room = data.get('room', 'default')
        leave_room(room)
        emit('sync_status', {'status': 'left', 'room': room}, room=room)
        print(f'Client {request.sid} left room: {room}')
    
    @socketio.on('timer_start')
    def handle_timer_start(data):
        """タイマー開始イベントを同期"""
        room = data.get('room', 'default')
        emit('timer_sync', {
            'action': 'start',
            'type': data.get('type', 'work'),
            'duration': data.get('duration'),
            'timestamp': data.get('timestamp')
        }, room=room, include_self=False)
        print(f'Timer start broadcast to room: {room}')
    
    @socketio.on('timer_pause')
    def handle_timer_pause(data):
        """タイマー一時停止イベントを同期"""
        room = data.get('room', 'default')
        emit('timer_sync', {
            'action': 'pause',
            'remaining': data.get('remaining'),
            'timestamp': data.get('timestamp')
        }, room=room, include_self=False)
        print(f'Timer pause broadcast to room: {room}')
    
    @socketio.on('timer_resume')
    def handle_timer_resume(data):
        """タイマー再開イベントを同期"""
        room = data.get('room', 'default')
        emit('timer_sync', {
            'action': 'resume',
            'remaining': data.get('remaining'),
            'timestamp': data.get('timestamp')
        }, room=room, include_self=False)
        print(f'Timer resume broadcast to room: {room}')
    
    @socketio.on('timer_reset')
    def handle_timer_reset(data):
        """タイマーリセットイベントを同期"""
        room = data.get('room', 'default')
        emit('timer_sync', {
            'action': 'reset',
            'timestamp': data.get('timestamp')
        }, room=room, include_self=False)
        print(f'Timer reset broadcast to room: {room}')
    
    @socketio.on('timer_complete')
    def handle_timer_complete(data):
        """タイマー完了イベントを同期"""
        room = data.get('room', 'default')
        emit('timer_sync', {
            'action': 'complete',
            'session_id': data.get('session_id'),
            'timestamp': data.get('timestamp')
        }, room=room, include_self=False)
        print(f'Timer complete broadcast to room: {room}')
