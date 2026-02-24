"""データベース統合テスト"""
import json
from datetime import datetime, timezone
from app.models import db, Pomodoro


def test_db_integration_start_complete(client):
    """startとcompleteのデータベース統合テスト"""
    # start APIを呼び出し
    resp = client.post('/api/start', json={'type': 'work'})
    assert resp.status_code == 201
    data = resp.get_json()
    pid = data['id']
    
    # データベースに保存されていることを確認
    with client.application.app_context():
        pomodoro = db.session.get(Pomodoro, pid)
        assert pomodoro is not None
        assert pomodoro.status == 'running'
        assert pomodoro.type == 'work'
        assert pomodoro.end_time is None
    
    # complete APIを呼び出し
    resp2 = client.post('/api/complete', json={'id': pid})
    assert resp2.status_code == 200
    
    # データベースが更新されていることを確認
    with client.application.app_context():
        pomodoro = db.session.get(Pomodoro, pid)
        assert pomodoro is not None
        assert pomodoro.status == 'completed'
        assert pomodoro.end_time is not None
        assert pomodoro.duration_sec is not None
        assert pomodoro.duration_sec >= 0


def test_db_integration_stats_persistence(client):
    """stats APIのデータベース永続性テスト"""
    # 複数のポモドーロを作成
    ids = []
    for i in range(3):
        resp = client.post('/api/start', json={'type': 'work'})
        pid = resp.get_json()['id']
        ids.append(pid)
        client.post('/api/complete', json={'id': pid})
    
    # stats APIを呼び出して、すべてのレコードが取得できることを確認
    resp = client.get('/api/stats')
    data = resp.get_json()
    assert data['completed_count'] == 3
    
    # データベースから直接確認
    with client.application.app_context():
        all_pomodoros = Pomodoro.query.filter_by(status='completed').all()
        assert len(all_pomodoros) == 3
        for pomodoro in all_pomodoros:
            assert pomodoro.id in ids
            assert pomodoro.status == 'completed'


def test_db_integration_date_filter(client):
    """日付フィルタのデータベース統合テスト"""
    now = datetime.now(timezone.utc)
    
    # 今日のデータを作成
    with client.application.app_context():
        rec1 = Pomodoro(
            start_time=now.replace(hour=10, minute=0).isoformat(),
            end_time=now.replace(hour=10, minute=25).isoformat(),
            duration_sec=1500,
            status='completed',
            type='work',
        )
        db.session.add(rec1)
        db.session.commit()
    
    # 今日の日付でフィルタして取得
    date_str = now.date().isoformat()
    resp = client.get(f'/api/stats?date={date_str}')
    data = resp.get_json()
    assert data['completed_count'] == 1
    assert data['total_focus_seconds'] == 1500
