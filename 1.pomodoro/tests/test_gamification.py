"""ゲーミフィケーション機能のテスト"""
import json
from datetime import datetime, timezone, timedelta
from app.models import db, Pomodoro


def test_complete_gives_xp(client):
    """ポモドーロ完了時にXPが付与されることをテスト"""
    # start
    resp = client.post('/api/start', json={'type': 'work'})
    assert resp.status_code == 201
    data = resp.get_json()
    pid = data['id']
    
    # complete
    resp2 = client.post('/api/complete', json={'id': pid})
    assert resp2.status_code == 200
    complete_data = resp2.get_json()
    
    # XPが付与されていることを確認
    assert 'xp_gained' in complete_data
    assert complete_data['xp_gained'] == 10
    assert complete_data['total_xp'] == 10
    assert complete_data['level'] == 1
    assert complete_data['level_up'] == False


def test_level_up(client):
    """レベルアップのテスト"""
    # 10回完了してレベルアップ（100 XP必要）
    for i in range(10):
        resp = client.post('/api/start', json={'type': 'work'})
        pid = resp.get_json()['id']
        resp2 = client.post('/api/complete', json={'id': pid})
        data = resp2.get_json()
        
        if i < 9:
            assert data['level'] == 1
            assert data['level_up'] == False
        else:
            # 10回目でレベルアップ
            assert data['level'] == 2
            assert data['level_up'] == True


def test_gamification_stats(client):
    """ゲーミフィケーション統計APIのテスト"""
    # 初期状態
    resp = client.get('/api/gamification/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['level'] == 1
    assert data['total_xp'] == 0
    assert data['streak_days'] == 0
    
    # ポモドーロ完了後
    resp = client.post('/api/start', json={'type': 'work'})
    pid = resp.get_json()['id']
    client.post('/api/complete', json={'id': pid})
    
    resp = client.get('/api/gamification/stats')
    data = resp.get_json()
    assert data['level'] == 1
    assert data['total_xp'] == 10


def test_achievements(client):
    """バッジ獲得のテスト"""
    # 初期状態
    resp = client.get('/api/gamification/achievements')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['total_count'] == 0
    
    # 1回完了
    resp = client.post('/api/start', json={'type': 'work'})
    pid = resp.get_json()['id']
    client.post('/api/complete', json={'id': pid})
    
    # 「初めてのポモドーロ」バッジを取得
    resp = client.get('/api/gamification/achievements')
    data = resp.get_json()
    assert data['total_count'] >= 1
    badge_ids = [b['id'] for b in data['achievements']]
    assert 'first_pomodoro' in badge_ids


def test_streak_calculation(client):
    """ストリーク計算のテスト"""
    # 3日連続のデータを作成
    now = datetime.now(timezone.utc)
    
    with client.application.app_context():
        for i in range(3):
            date = now - timedelta(days=2-i)
            rec = Pomodoro(
                start_time=date.replace(hour=10, minute=0).isoformat(),
                end_time=date.replace(hour=10, minute=25).isoformat(),
                duration_sec=1500,
                status='completed',
                type='work',
            )
            db.session.add(rec)
        db.session.commit()
    
    # ストリークを確認
    resp = client.get('/api/gamification/stats')
    data = resp.get_json()
    assert data['streak_days'] == 3
    
    # バッジ確認
    resp = client.get('/api/gamification/achievements')
    data = resp.get_json()
    badge_ids = [b['id'] for b in data['achievements']]
    assert 'streak_3' in badge_ids


def test_weekly_stats(client):
    """週間統計のテスト"""
    # 今週のデータを作成
    now = datetime.now(timezone.utc)
    
    with client.application.app_context():
        for i in range(5):
            date = now - timedelta(days=i)
            rec = Pomodoro(
                start_time=date.replace(hour=10, minute=0).isoformat(),
                end_time=date.replace(hour=10, minute=25).isoformat(),
                duration_sec=1500,
                status='completed',
                type='work',
            )
            db.session.add(rec)
        db.session.commit()
    
    # 週間統計を確認
    resp = client.get('/api/gamification/weekly-stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['total_completed'] == 5
    assert data['total_focus_seconds'] == 7500
    assert 'daily_counts' in data


def test_monthly_stats(client):
    """月間統計のテスト"""
    # 今月のデータを作成
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    with client.application.app_context():
        for i in range(10):
            date = month_start + timedelta(days=i)
            rec = Pomodoro(
                start_time=date.replace(hour=10, minute=0).isoformat(),
                end_time=date.replace(hour=10, minute=25).isoformat(),
                duration_sec=1500,
                status='completed',
                type='work',
            )
            db.session.add(rec)
        db.session.commit()
    
    # 月間統計を確認
    resp = client.get('/api/gamification/monthly-stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['total_completed'] == 10
    assert data['total_focus_seconds'] == 15000
    assert 'weekly_counts' in data
    assert 'completion_rate' in data


def test_weekly_10_badge(client):
    """今週10回完了バッジのテスト"""
    # 今週10回のデータを作成
    now = datetime.now(timezone.utc)
    
    with client.application.app_context():
        for i in range(10):
            date = now - timedelta(days=i % 7)
            rec = Pomodoro(
                start_time=date.replace(hour=10 + i % 8, minute=0).isoformat(),
                end_time=date.replace(hour=10 + i % 8, minute=25).isoformat(),
                duration_sec=1500,
                status='completed',
                type='work',
            )
            db.session.add(rec)
        db.session.commit()
    
    # バッジ確認
    resp = client.get('/api/gamification/achievements')
    data = resp.get_json()
    badge_ids = [b['id'] for b in data['achievements']]
    assert 'weekly_10' in badge_ids
